import pytest
import sys

# Django 5.1 + Python 3.14 compatibility fix:
# Python 3.14 changed copy(super()) behavior; patch BaseContext.__copy__ to work correctly.
if sys.version_info >= (3, 14):
    from copy import copy as _copy
    from django.template.context import BaseContext

    def _fixed_base_context_copy(self):
        duplicate = object.__new__(type(self))
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _fixed_base_context_copy


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
