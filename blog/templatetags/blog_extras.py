from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from blog.management.commands.sync_posts import render_markdown

register = template.Library()


@register.simple_tag
def cover_url(cover: str) -> str:
    """Return URL for a cover image: full URL returned as-is, filename resolved via static."""
    if not cover:
        return ''
    if cover.startswith('http://') or cover.startswith('https://'):
        return cover
    return static(f'images/posts/{cover}')


@register.filter
def reading_time_label(minutes: int) -> str:
    return f'{minutes} min read'


@register.simple_tag
def md_preview(content_md: str) -> str:
    return mark_safe(render_markdown(content_md))
