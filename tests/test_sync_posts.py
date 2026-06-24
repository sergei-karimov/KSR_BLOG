import pytest
from pathlib import Path
import textwrap

pytestmark = pytest.mark.django_db


@pytest.fixture
def posts_dir(tmp_path):
    return tmp_path


def write_post(directory: Path, filename: str, content: str):
    (directory / filename).write_text(content, encoding='utf-8')


def test_sync_creates_post(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'my-article.md', textwrap.dedent("""\
        ---
        title: My Article
        date: 2026-01-15
        tags: [python, django]
        status: published
        comments: true
        excerpt: Short description.
        ---
        # My Article

        Hello world content here.
    """))

    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='my-article')
    assert post.title == 'My Article'
    assert post.status == 'published'
    assert post.comments_enabled is True
    assert post.excerpt == 'Short description.'
    assert post.tags.filter(slug='python').exists()
    assert post.tags.filter(slug='django').exists()
    assert '<h1>' in post.content_html


def test_sync_updates_existing_post(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    content = textwrap.dedent("""\
        ---
        title: Original Title
        date: 2026-01-15
        tags: [python]
        status: draft
        comments: false
        ---
        Original content.
    """)
    write_post(posts_dir, 'my-article.md', content)
    sync_posts_from_dir(posts_dir)

    updated = textwrap.dedent("""\
        ---
        title: Updated Title
        date: 2026-01-15
        tags: [python, django]
        status: published
        comments: true
        ---
        Updated content.
    """)
    write_post(posts_dir, 'my-article.md', updated)
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='my-article')
    assert post.title == 'Updated Title'
    assert post.status == 'published'
    assert post.tags.count() == 2


def test_sync_sets_reading_time(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    words = ' '.join(['word'] * 400)
    write_post(posts_dir, 'long-article.md', f"---\ntitle: Long\ndate: 2026-01-15\ntags: []\nstatus: published\ncomments: true\n---\n{words}")
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='long-article')
    assert post.reading_time == 2


def test_sync_auto_generates_excerpt_when_missing(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'no-excerpt.md', textwrap.dedent("""\
        ---
        title: No Excerpt
        date: 2026-01-15
        tags: []
        status: published
        comments: true
        ---
        This is the first paragraph content that should become the excerpt.

        Second paragraph.
    """))
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='no-excerpt')
    assert len(post.excerpt) > 0


def test_extract_excerpt_returns_empty_when_only_headings():
    from blog.management.commands.sync_posts import extract_excerpt
    content = "# Heading One\n\n## Heading Two\n\n### Heading Three"
    assert extract_excerpt(content) == ''


def test_sync_no_date_sets_published_at_none(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'no-date.md', textwrap.dedent("""\
        ---
        title: No Date
        tags: []
        status: published
        comments: true
        ---
        Content here.
    """))
    sync_posts_from_dir(posts_dir)
    post = Post.objects.get(slug='no-date')
    assert post.published_at is None


def test_sync_file_path_relative_to_base_dir(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'path-test.md', textwrap.dedent("""\
        ---
        title: Path Test
        date: 2026-01-15
        tags: []
        status: published
        comments: true
        ---
        Content.
    """))
    base_dir = posts_dir.parent
    sync_posts_from_dir(posts_dir, base_dir=base_dir)
    post = Post.objects.get(slug='path-test')
    assert not post.file_path.startswith(str(base_dir))


def test_sync_skips_invalid_file_and_returns_error_count(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir

    (posts_dir / 'bad.md').write_bytes(b'\xff\xfe invalid utf')
    errors = sync_posts_from_dir(posts_dir)
    assert errors >= 1


def test_sync_handle_command(db):
    from django.test import override_settings
    from django.core.management import call_command
    from pathlib import Path
    import tempfile, textwrap, io

    with tempfile.TemporaryDirectory() as tmpdir:
        posts_path = Path(tmpdir)
        (posts_path / 'cmd-post.md').write_text(textwrap.dedent("""\
            ---
            title: Command Post
            date: 2026-01-15
            tags: []
            status: published
            comments: true
            ---
            Content.
        """), encoding='utf-8')

        out = io.StringIO()
        with override_settings(CONTENT_DIR=posts_path):
            call_command('sync_posts', stdout=out)
        assert 'Synced' in out.getvalue()


def test_sync_handle_missing_content_dir(db):
    from django.test import override_settings
    from django.core.management import call_command
    from pathlib import Path
    import io

    err = io.StringIO()
    with override_settings(CONTENT_DIR=Path('/nonexistent/path/xyz')):
        call_command('sync_posts', stderr=err)
    assert 'not found' in err.getvalue()


def test_sync_handle_logs_warning_on_errors(db):
    from django.test import override_settings
    from django.core.management import call_command
    from pathlib import Path
    import tempfile, io

    with tempfile.TemporaryDirectory() as tmpdir:
        posts_path = Path(tmpdir)
        (posts_path / 'bad.md').write_bytes(b'\xff\xfe\xff\xfe invalid')

        err = io.StringIO()
        with override_settings(CONTENT_DIR=posts_path):
            call_command('sync_posts', stderr=err)
        assert 'error' in err.getvalue().lower()


def test_sync_cover_field(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'cover-test.md', textwrap.dedent("""\
        ---
        title: Cover Test
        date: 2026-01-15
        tags: []
        status: published
        comments: true
        cover: my-image.jpg
        ---
        Content.
    """))
    sync_posts_from_dir(posts_dir)
    post = Post.objects.get(slug='cover-test')
    assert post.cover == 'my-image.jpg'
