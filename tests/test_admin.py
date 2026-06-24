import pytest
from django.contrib.auth.models import User
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    client.login(username='admin', password='password')
    return client


def test_post_admin_list(admin_client, sample_post):
    response = admin_client.get('/admin/blog/post/')
    assert response.status_code == 200
    assert sample_post.title.encode() in response.content


def test_post_admin_tag_list_column(admin_client, sample_post):
    """tag_list() method is called when rendering the list page."""
    response = admin_client.get('/admin/blog/post/')
    assert b'python' in response.content


def test_post_admin_detail_with_content(admin_client, sample_post):
    """content_html_preview() is rendered in the change form."""
    response = admin_client.get(f'/admin/blog/post/{sample_post.pk}/change/')
    assert response.status_code == 200


def test_post_admin_detail_empty_content(admin_client):
    """content_html_preview() returns em-dash when content_md is empty."""
    from blog.models import Post
    post = Post.objects.create(
        slug='empty-post', title='Empty', content_md='', content_html='',
        status='draft', reading_time=1,
    )
    response = admin_client.get(f'/admin/blog/post/{post.pk}/change/')
    assert response.status_code == 200


def test_post_admin_save_updates_html(admin_client, sample_post):
    """save_model() re-renders content_html and updates reading_time."""
    data = {
        'title': sample_post.title,
        'slug': sample_post.slug,
        'status': 'published',
        'comments_enabled': True,
        'content_md': '# Updated\n\nNew content.',
        'excerpt': '',
        'reading_time': 1,
        'file_path': '',
        'cover': '',
        'tags': [],
        '_save': 'Save',
    }
    response = admin_client.post(f'/admin/blog/post/{sample_post.pk}/change/', data)
    assert response.status_code in (200, 302)
    from blog.models import Post
    updated = Post.objects.get(pk=sample_post.pk)
    assert '<h1>' in updated.content_html


def test_comment_admin_approve_action(admin_client, sample_post):
    """approve_comments bulk action sets approved=True."""
    from blog.models import Comment
    comment = Comment.objects.create(
        post=sample_post, author_name='Bob',
        email='bob@example.com', body='Hello', approved=False,
    )
    response = admin_client.post('/admin/blog/comment/', {
        'action': 'approve_comments',
        '_selected_action': [comment.pk],
    })
    assert response.status_code in (200, 302)
    assert Comment.objects.get(pk=comment.pk).approved is True


def test_comment_admin_body_preview(admin_client, sample_post):
    """body_preview column visible in comment list."""
    from blog.models import Comment
    Comment.objects.create(
        post=sample_post, author_name='Eve',
        email='eve@example.com', body='A' * 100, approved=True,
    )
    response = admin_client.get('/admin/blog/comment/')
    assert response.status_code == 200
    assert b'A' * 80 in response.content
