import re
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
import frontmatter
import markdown as md
from datetime import datetime, date

from blog.models import Post, Tag


def render_markdown(content: str) -> str:
    return md.markdown(
        content,
        extensions=['fenced_code', 'codehilite', 'tables'],
        extension_configs={
            'codehilite': {'css_class': 'highlight', 'guess_lang': False},
        },
    )


def extract_excerpt(content_md: str, max_chars: int = 200) -> str:
    paragraphs = [p.strip() for p in content_md.split('\n\n') if p.strip()]
    for para in paragraphs:
        if not para.startswith('#'):
            clean = re.sub(r'[*_`#\[\]()]', '', para).strip()
            return clean[:max_chars]
    return ''


def sync_posts_from_dir(posts_dir: Path) -> None:
    for md_file in sorted(posts_dir.glob('*.md')):
        post_data = frontmatter.load(str(md_file))
        metadata = post_data.metadata
        content_md = post_data.content

        slug = md_file.stem
        title = metadata.get('title', slug)
        status = metadata.get('status', 'draft')
        comments_enabled = bool(metadata.get('comments', True))
        excerpt = metadata.get('excerpt', '') or extract_excerpt(content_md)
        tag_names = metadata.get('tags', [])

        raw_date = metadata.get('date')
        if isinstance(raw_date, (datetime, date)):
            published_at = timezone.make_aware(
                datetime.combine(raw_date, datetime.min.time())
                if isinstance(raw_date, date) and not isinstance(raw_date, datetime)
                else raw_date
            )
        else:
            published_at = None

        content_html = render_markdown(content_md)

        post, _ = Post.objects.update_or_create(
            slug=slug,
            defaults={
                'title': title,
                'content_md': content_md,
                'content_html': content_html,
                'excerpt': excerpt,
                'status': status,
                'comments_enabled': comments_enabled,
                'file_path': str(md_file.relative_to(md_file.parent.parent.parent))
                    if md_file.parent.parent.parent.exists() else str(md_file),
                'published_at': published_at,
            },
        )
        post.reading_time = post.compute_reading_time()
        post.save(update_fields=['reading_time'])

        tags = []
        for tag_name in tag_names:
            tag_slug = slugify(tag_name)
            tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'name': tag_name})
            tags.append(tag)
        post.tags.set(tags)


class Command(BaseCommand):
    help = 'Sync Markdown posts from content/posts/ into the database'

    def handle(self, *args, **options):
        posts_dir = settings.CONTENT_DIR
        if not posts_dir.exists():
            self.stderr.write(f'Content directory not found: {posts_dir}')
            return
        sync_posts_from_dir(posts_dir)
        count = Post.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Synced posts. Total in DB: {count}'))
