import pytest
import uuid
import io
from unittest.mock import patch
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

pytestmark = pytest.mark.django_db


def make_post(title='Test Post', hours_ago=1):
    from blog.models import Post
    return Post.objects.create(
        slug=title.lower().replace(' ', '-'),
        title=title,
        content_md='Content.',
        content_html='<p>Content.</p>',
        excerpt='Content.',
        status='published',
        reading_time=1,
        published_at=timezone.now() - timedelta(hours=hours_ago),
    )


def make_subscriber(email, confirmed=True):
    from blog.models import Subscriber
    return Subscriber.objects.create(
        email=email,
        confirmed=confirmed,
        unsubscribe_token=uuid.uuid4(),
    )


def test_notify_no_new_posts():
    out = io.StringIO()
    call_command('notify_subscribers', '--hours=1', stdout=out)
    assert 'No new posts' in out.getvalue()


def test_notify_no_confirmed_subscribers():
    make_post(hours_ago=0)
    make_subscriber('unconfirmed@example.com', confirmed=False)
    out = io.StringIO()
    call_command('notify_subscribers', '--hours=24', stdout=out)
    assert 'No confirmed subscribers' in out.getvalue()


def test_notify_sends_emails():
    make_post(hours_ago=0)
    make_subscriber('reader@example.com', confirmed=True)

    out = io.StringIO()
    with patch('blog.management.commands.notify_subscribers.send_mail') as mock_mail:
        call_command('notify_subscribers', '--hours=24', stdout=out)
        assert mock_mail.called
        assert mock_mail.call_count == 1

    assert 'Notified 1 subscriber' in out.getvalue()


def test_notify_sends_to_all_subscribers():
    make_post(hours_ago=0)
    make_subscriber('a@example.com', confirmed=True)
    make_subscriber('b@example.com', confirmed=True)

    with patch('blog.management.commands.notify_subscribers.send_mail') as mock_mail:
        call_command('notify_subscribers', '--hours=24')
        assert mock_mail.call_count == 2


def test_notify_skips_old_posts():
    make_post(hours_ago=48)
    make_subscriber('reader@example.com', confirmed=True)

    out = io.StringIO()
    call_command('notify_subscribers', '--hours=24', stdout=out)
    assert 'No new posts' in out.getvalue()
