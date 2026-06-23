from django.contrib import admin
from django.utils.html import format_html
from blog.models import Post, Tag, Subscriber, Comment
from blog.management.commands.sync_posts import render_markdown


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at', 'comments_enabled', 'reading_time', 'tag_list']
    list_filter = ['status', 'tags', 'comments_enabled']
    search_fields = ['title', 'content_md']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['content_html_preview', 'reading_time']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'status', 'published_at', 'tags', 'comments_enabled')}),
        ('Content', {'fields': ('content_md', 'content_html_preview')}),
        ('Meta', {'fields': ('excerpt', 'reading_time', 'file_path')}),
    )

    def tag_list(self, obj):
        return ', '.join(t.name for t in obj.tags.all())
    tag_list.short_description = 'Tags'

    def content_html_preview(self, obj):
        if obj.content_md:
            html = render_markdown(obj.content_md)
            return format_html(
                '<div style="max-height:400px;overflow:auto;border:1px solid #ccc;padding:1em">{}</div>',
                format_html(html)
            )
        return '—'
    content_html_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        obj.content_html = render_markdown(obj.content_md)
        obj.reading_time = obj.compute_reading_time()
        super().save_model(request, obj, form, change)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'confirmed', 'created_at']
    list_filter = ['confirmed']
    readonly_fields = ['unsubscribe_token', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'post', 'approved', 'created_at']
    list_filter = ['approved', 'post']
    actions = ['approve_comments']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
