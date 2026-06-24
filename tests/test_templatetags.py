import pytest


def test_reading_time_label():
    from blog.templatetags.blog_extras import reading_time_label
    assert reading_time_label(5) == '5 min read'
    assert reading_time_label(1) == '1 min read'


def test_cover_url_empty():
    from blog.templatetags.blog_extras import cover_url
    assert cover_url('') == ''


def test_cover_url_full_http():
    from blog.templatetags.blog_extras import cover_url
    url = 'https://example.com/image.jpg'
    assert cover_url(url) == url


def test_cover_url_full_http_scheme():
    from blog.templatetags.blog_extras import cover_url
    url = 'http://example.com/image.jpg'
    assert cover_url(url) == url


def test_cover_url_filename():
    from blog.templatetags.blog_extras import cover_url
    result = cover_url('my-cover.jpg')
    assert 'images/posts/my-cover.jpg' in result


def test_md_preview_returns_html():
    from blog.templatetags.blog_extras import md_preview
    result = md_preview('**bold**')
    assert '<strong>bold</strong>' in result
