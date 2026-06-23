import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import ProgrammingError, OperationalError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse

from blog.models import Post, Tag, Subscriber, Comment
from blog.forms import SubscribeForm, CommentForm


def _published_posts():
    return Post.objects.filter(status='published').prefetch_related('tags')


def home(request):
    posts = _published_posts()
    return render(request, 'blog/home.html', {
        'latest_post': posts.first(),
        'posts': posts[1:7],
    })


def post_list(request):
    tag_slug = request.GET.get('tag')
    posts = _published_posts()
    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=active_tag)
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/post_list.html', {
        'page_obj': page,
        'tags': Tag.objects.all(),
        'active_tag': active_tag,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    related = _published_posts().filter(tags__in=post.tags.all()).exclude(pk=post.pk).distinct()[:3]
    comment_form = CommentForm() if post.comments_enabled else None

    if request.method == 'POST' and post.comments_enabled:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment is awaiting moderation.')
            return redirect(post.get_absolute_url())

    approved_comments = post.comments.filter(approved=True) if post.comments_enabled else None

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related,
        'comment_form': comment_form,
        'comments': approved_comments,
    })


def tag(request, slug):
    tag_obj = get_object_or_404(Tag, slug=slug)
    posts = _published_posts().filter(tags=tag_obj)
    return render(request, 'blog/tag.html', {'tag': tag_obj, 'posts': posts})


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        try:
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            vector = SearchVector('title', weight='A') + SearchVector('content_md', weight='B')
            search_query = SearchQuery(query)
            results = (
                Post.objects.filter(status='published')
                .annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.1)
                .order_by('-rank')
            )
        except (ImportError, ProgrammingError, OperationalError):
            results = Post.objects.filter(
                status='published'
            ).filter(Q(title__icontains=query) | Q(content_md__icontains=query))
    return render(request, 'blog/search.html', {'query': query, 'results': results})


def subscribe(request):
    form = SubscribeForm()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={'unsubscribe_token': uuid.uuid4()},
            )
            if not subscriber.confirmed:
                confirm_path = reverse('blog:confirm_subscription', kwargs={'token': subscriber.unsubscribe_token})
                confirm_url = request.build_absolute_uri(confirm_path)
                send_mail(
                    subject='Confirm your subscription',
                    message=f'Click to confirm: {confirm_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
            return render(request, 'blog/subscribe.html', {'form': form, 'submitted': True})
    return render(request, 'blog/subscribe.html', {'form': form, 'submitted': False})


def confirm_subscription(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    subscriber.confirmed = True
    subscriber.save(update_fields=['confirmed'])
    return render(request, 'blog/subscribe_confirm.html', {'action': 'confirmed'})


def unsubscribe(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    if request.method == 'POST':
        subscriber.delete()
        return render(request, 'blog/subscribe_confirm.html', {'action': 'unsubscribed'})
    return render(request, 'blog/subscribe_confirm.html', {'action': 'unsubscribe_confirm', 'token': token})
