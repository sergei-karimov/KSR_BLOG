import math
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


def sync_posts_from_dir(posts_dir: Path, base_dir: Path | None = None) -> int:
    if base_dir is None:
        base_dir = posts_dir
    errors = 0
    for md_file in sorted(posts_dir.glob('*.md')):
        try:
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
                if isinstance(raw_date, date) and not isinstance(raw_date, datetime):
                    raw_date = datetime.combine(raw_date, datetime.min.time())
                published_at = timezone.make_aware(raw_date) if timezone.is_naive(raw_date) else raw_date
            else:
                published_at = None

            content_html = render_markdown(content_md)
            word_count = len(content_md.split())
            reading_time = max(1, math.ceil(word_count / 200))

            try:
                rel_path = str(md_file.relative_to(base_dir))
            except ValueError:
                rel_path = str(md_file)

            post, _ = Post.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'content_md': content_md,
                    'content_html': content_html,
                    'excerpt': excerpt,
                    'status': status,
                    'comments_enabled': comments_enabled,
                    'file_path': rel_path,
                    'published_at': published_at,
                    'reading_time': reading_time,
                },
            )

            tags = []
            for tag_name in tag_names:
                tag_slug = slugify(tag_name)
                tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'name': tag_name})
                tags.append(tag)
            post.tags.set(tags)
        except Exception as exc:
            errors += 1
            import traceback
            traceback.print_exc()
    return errors


class Command(BaseCommand):
    help = 'Sync Markdown posts from content/posts/ into the database'

    def handle(self, *args, **options):
        posts_dir = settings.CONTENT_DIR
        if not posts_dir.exists():
            self.stderr.write(f'Content directory not found: {posts_dir}')
            return
        errors = sync_posts_from_dir(posts_dir, base_dir=settings.BASE_DIR)
        count = Post.objects.count()
        if errors:
            self.stderr.write(self.style.WARNING(f'Synced with {errors} error(s). Total in DB: {count}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Synced posts. Total in DB: {count}'))
