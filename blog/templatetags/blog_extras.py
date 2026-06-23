from django import template
from blog.management.commands.sync_posts import render_markdown

register = template.Library()


@register.filter
def reading_time_label(minutes: int) -> str:
    return f'{minutes} min read'


@register.simple_tag
def md_preview(content_md: str) -> str:
    return render_markdown(content_md)
