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
