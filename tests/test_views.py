import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_home_returns_200(client, sample_post):
    response = client.get(reverse('blog:home'))
    assert response.status_code == 200


def test_post_detail_returns_200(client, sample_post):
    response = client.get(reverse('blog:post_detail', kwargs={'slug': sample_post.slug}))
    assert response.status_code == 200


def test_post_detail_draft_returns_404(client):
    from blog.models import Post
    post = Post.objects.create(
        slug='draft-post', title='Draft', content_md='', content_html='',
        status='draft', file_path='', reading_time=1,
    )
    response = client.get(reverse('blog:post_detail', kwargs={'slug': post.slug}))
    assert response.status_code == 404


def test_post_list_returns_200(client, sample_post):
    response = client.get(reverse('blog:post_list'))
    assert response.status_code == 200


def test_tag_view_returns_200(client, sample_post):
    response = client.get(reverse('blog:tag', kwargs={'slug': 'python'}))
    assert response.status_code == 200


def test_search_returns_200(client, sample_post):
    response = client.get(reverse('blog:search') + '?q=test')
    assert response.status_code == 200


def test_subscribe_get_returns_200(client):
    response = client.get(reverse('blog:subscribe'))
    assert response.status_code == 200


def test_subscribe_post_creates_subscriber(client):
    response = client.post(reverse('blog:subscribe'), {'email': 'test@example.com'})
    assert response.status_code == 200
    from blog.models import Subscriber
    assert Subscriber.objects.filter(email='test@example.com').exists()


def test_confirm_subscription_sets_confirmed(client):
    import uuid
    from blog.models import Subscriber
    token = uuid.uuid4()
    Subscriber.objects.create(email='sub@example.com', confirmed=False, unsubscribe_token=token)
    response = client.get(reverse('blog:confirm_subscription', kwargs={'token': token}))
    assert response.status_code == 200
    assert Subscriber.objects.get(email='sub@example.com').confirmed is True


def test_unsubscribe_deletes_on_post(client):
    import uuid
    from blog.models import Subscriber
    token = uuid.uuid4()
    Subscriber.objects.create(email='sub2@example.com', confirmed=True, unsubscribe_token=token)
    response = client.post(reverse('blog:unsubscribe', kwargs={'token': token}))
    assert response.status_code == 200
    assert not Subscriber.objects.filter(email='sub2@example.com').exists()


def test_unsubscribe_get_shows_confirmation(client):
    import uuid
    from blog.models import Subscriber
    token = uuid.uuid4()
    Subscriber.objects.create(email='sub3@example.com', confirmed=True, unsubscribe_token=token)
    response = client.get(reverse('blog:unsubscribe', kwargs={'token': token}))
    assert response.status_code == 200
    assert Subscriber.objects.filter(email='sub3@example.com').exists()


def test_post_detail_comment_post_creates_comment(client, sample_post):
    from blog.models import Comment
    response = client.post(
        reverse('blog:post_detail', kwargs={'slug': sample_post.slug}),
        {'author_name': 'Alice', 'email': 'alice@example.com', 'body': 'Great post!'},
    )
    assert response.status_code == 302
    assert Comment.objects.filter(post=sample_post, author_name='Alice').exists()


def test_post_list_multi_tag_filter(client, sample_post):
    response = client.get(reverse('blog:post_list') + '?tag=python&tag=nonexistent')
    assert response.status_code == 200
