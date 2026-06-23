import pytest
from django.utils.text import slugify

pytestmark = pytest.mark.django_db


def test_tag_str():
    from blog.models import Tag
    tag = Tag(name='Python', slug='python')
    assert str(tag) == 'Python'


def test_post_str():
    from blog.models import Post
    post = Post(title='My Post', slug='my-post')
    assert str(post) == 'My Post'


def test_post_get_absolute_url():
    from blog.models import Post
    post = Post(slug='my-post')
    assert post.get_absolute_url() == '/posts/my-post/'


def test_post_is_published(sample_post):
    assert sample_post.status == 'published'


def test_post_tags(sample_post):
    assert sample_post.tags.filter(slug='python').exists()


def test_reading_time_computed():
    from blog.models import Post
    # 200 words per minute average
    words = ' '.join(['word'] * 400)
    post = Post(content_md=words)
    assert post.compute_reading_time() == 2
