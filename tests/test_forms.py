import pytest
from blog.forms import SubscribeForm, CommentForm


def test_subscribe_form_valid():
    form = SubscribeForm(data={'email': 'user@example.com'})
    assert form.is_valid()


def test_subscribe_form_invalid():
    form = SubscribeForm(data={'email': 'not-an-email'})
    assert not form.is_valid()


def test_comment_form_valid():
    form = CommentForm(data={
        'author_name': 'Alice',
        'email': 'alice@example.com',
        'body': 'Great post!',
    })
    assert form.is_valid()


def test_comment_form_missing_body():
    form = CommentForm(data={'author_name': 'Alice', 'email': 'alice@example.com', 'body': ''})
    assert not form.is_valid()
