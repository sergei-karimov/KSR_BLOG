import pytest

@pytest.fixture
def sample_post(db):
    from blog.models import Post, Tag
    tag = Tag.objects.create(name='python', slug='python')
    post = Post.objects.create(
        slug='test-post',
        title='Test Post',
        content_md='# Hello\n\nSome content.',
        content_html='<h1>Hello</h1><p>Some content.</p>',
        excerpt='Some content.',
        status='published',
        comments_enabled=True,
        file_path='content/posts/test-post.md',
        reading_time=1,
    )
    post.tags.add(tag)
    return post
