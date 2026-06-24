from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from blog.models import Post, Subscriber


class Command(BaseCommand):
    help = 'Email confirmed subscribers about posts published in the last 24 hours'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Look back N hours for new posts')

    def handle(self, *args, **options):
        since = timezone.now() - timedelta(hours=options['hours'])
        new_posts = Post.objects.filter(status='published', published_at__gte=since)

        if not new_posts.exists():
            self.stdout.write('No new posts to notify about.')
            return

        subscribers = Subscriber.objects.filter(confirmed=True)
        if not subscribers.exists():
            self.stdout.write('No confirmed subscribers.')
            return

        for post in new_posts:
            subject = f'New post: {post.title}'
            for subscriber in subscribers:
                unsubscribe_url = f"{settings.SITE_URL}/unsubscribe/{subscriber.unsubscribe_token}/"
                body = (
                    f"{post.title}\n\n"
                    f"{post.excerpt}\n\n"
                    f"Read more: {settings.SITE_URL}{post.get_absolute_url()}\n\n"
                    f"---\nUnsubscribe: {unsubscribe_url}"
                )
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [subscriber.email], fail_silently=True)

        self.stdout.write(self.style.SUCCESS(
            f'Notified {subscribers.count()} subscriber(s) about {new_posts.count()} post(s).'
        ))
