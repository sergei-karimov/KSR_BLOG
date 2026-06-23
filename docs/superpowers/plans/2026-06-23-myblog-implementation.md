# MyBlog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal Django blog where articles are authored as Markdown files synced into a PostgreSQL database, with full admin panel, search, subscriptions, and optional comments.

**Architecture:** Markdown files in `content/posts/` serve as the source of truth for article content; a `sync_posts` management command parses YAML frontmatter and upserts records into the database. Django serves all pages as server-rendered HTML with Tailwind CSS styling and Pygments syntax highlighting.

**Tech Stack:** Python 3.12, Django 5.x, PostgreSQL (SQLite for local dev), python-frontmatter, markdown, Pygments, WhiteNoise, Tailwind CSS (CDN), Gunicorn

---

## File Map

```
MyBlog/
├── content/posts/                        # Markdown article files
│   └── hello-world.md                    # Sample post
├── blog/                                 # Main Django app
│   ├── __init__.py
│   ├── models.py                         # Post, Tag, Subscriber, Comment
│   ├── admin.py                          # Admin configuration with MD preview
│   ├── views.py                          # All page views
│   ├── urls.py                           # URL routing
│   ├── forms.py                          # SubscribeForm, CommentForm
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── blog_extras.py               # reading_time filter, md_preview tag
│   └── management/commands/
│       ├── sync_posts.py                 # MD → DB sync
│       └── notify_subscribers.py         # Email new post to subscribers
├── templates/
│   ├── base.html                         # Layout, header, footer, dark mode
│   ├── components/
│   │   └── post_card.html               # Reusable post card
│   └── blog/
│       ├── home.html
│       ├── post_list.html
│       ├── post_detail.html
│       ├── tag.html
│       ├── search.html
│       ├── subscribe.html
│       └── subscribe_confirm.html
├── static/
│   ├── css/main.css                      # Custom CSS vars, typography, dark mode
│   └── js/main.js                        # Dark mode toggle
├── myblog/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_sync_posts.py
│   ├── test_views.py
│   └── test_forms.py
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## Task 1: Project Bootstrap

**Files:**
- Create: `myblog/settings/base.py`
- Create: `myblog/settings/local.py`
- Create: `myblog/settings/production.py`
- Create: `myblog/urls.py`
- Create: `myblog/wsgi.py`
- Create: `myblog/__init__.py`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `.env.example`
- Create: `manage.py`

- [ ] **Step 1: Install Django and create project**

```bash
cd C:\Users\ksr_t\source\repos\MyBlog
python -m venv venv
venv\Scripts\activate      # Windows
pip install django==5.1.* python-frontmatter markdown pygments whitenoise psycopg[binary] python-decouple
pip freeze > requirements.txt
django-admin startproject myblog .
python manage.py startapp blog
```

- [ ] **Step 2: Create settings package**

Delete the generated `myblog/settings.py` and create the directory:

```bash
mkdir myblog\settings
echo. > myblog\settings\__init__.py
```

- [ ] **Step 3: Write `myblog/settings/base.py`**

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myblog.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CONTENT_DIR = BASE_DIR / 'content' / 'posts'

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='blog@example.com')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
```

- [ ] **Step 4: Write `myblog/settings/local.py`**

```python
from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS += ['django.contrib.postgres']
```

Note: SQLite does not support `django.contrib.postgres` search — in local.py, remove it from INSTALLED_APPS and the search view will fall back to `icontains`. Remove `'django.contrib.postgres'` from `INSTALLED_APPS` in local.py:

```python
from .base import *

DEBUG = True

INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.postgres']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

- [ ] **Step 5: Write `myblog/settings/production.py`**

```python
from .base import *
from decouple import config

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

- [ ] **Step 6: Write `myblog/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]
```

- [ ] **Step 7: Write `.env.example`**

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_SETTINGS_MODULE=myblog.settings.local

# Database (production only)
DB_NAME=myblog
DB_USER=myblog
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=blog@example.com
SITE_URL=https://yourdomain.com
```

- [ ] **Step 8: Create `.env` from example and set DJANGO_SETTINGS_MODULE**

```bash
copy .env.example .env
# Edit .env: set SECRET_KEY to a random string and DJANGO_SETTINGS_MODULE=myblog.settings.local
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- [ ] **Step 9: Create requirements-dev.txt**

```
-r requirements.txt
pytest
pytest-django
```

- [ ] **Step 10: Create `content/posts/` directory and sample post**

```bash
mkdir content\posts
```

Create `content/posts/hello-world.md`:

```markdown
---
title: "Hello, World!"
date: 2026-06-23
tags: [general]
status: published
comments: true
excerpt: "The first post on this blog."
---

# Hello, World!

Welcome to my blog. This is the first post.

## Code Example

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("World"))
```

More content here.
```

- [ ] **Step 11: Verify Django starts**

```bash
python manage.py check --settings=myblog.settings.local
```

Expected output: `System check identified no issues (0 silenced).`

- [ ] **Step 12: Commit**

```bash
git init
git add .
git commit -m "feat: bootstrap Django project with settings"
```

---

## Task 2: Post and Tag Models

**Files:**
- Modify: `blog/models.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests for Post and Tag models**

Create `tests/conftest.py`:

```python
import pytest
import django
from django.conf import settings

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
```

Create `tests/test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

Create `pytest.ini` in project root:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = myblog.settings.local
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
```

```bash
pip install pytest pytest-django
pytest tests/test_models.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — models not defined yet.

- [ ] **Step 3: Write `blog/models.py`**

```python
import math
from django.db import models
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content_md = models.TextField(blank=True)
    content_html = models.TextField(blank=True)
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    comments_enabled = models.BooleanField(default=True)
    file_path = models.CharField(max_length=500, blank=True)
    reading_time = models.PositiveIntegerField(default=1)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def compute_reading_time(self) -> int:
        word_count = len(self.content_md.split())
        return max(1, math.ceil(word_count / 200))


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(unique=True)

    def __str__(self):
        return self.email


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author_name} on {self.post}'
```

- [ ] **Step 4: Create and run migrations**

```bash
python manage.py makemigrations blog
python manage.py migrate
```

Expected: migrations applied successfully.

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_models.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add blog/models.py blog/migrations/ tests/ pytest.ini
git commit -m "feat: add Post, Tag, Subscriber, Comment models"
```

---

## Task 3: sync_posts Management Command

**Files:**
- Create: `blog/management/__init__.py`
- Create: `blog/management/commands/__init__.py`
- Create: `blog/management/commands/sync_posts.py`
- Create: `tests/test_sync_posts.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_sync_posts.py`:

```python
import pytest
from pathlib import Path
import tempfile
import textwrap

pytestmark = pytest.mark.django_db


@pytest.fixture
def posts_dir(tmp_path):
    return tmp_path


def write_post(directory: Path, filename: str, content: str):
    (directory / filename).write_text(content, encoding='utf-8')


def test_sync_creates_post(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'my-article.md', textwrap.dedent("""\
        ---
        title: My Article
        date: 2026-01-15
        tags: [python, django]
        status: published
        comments: true
        excerpt: Short description.
        ---
        # My Article

        Hello world content here.
    """))

    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='my-article')
    assert post.title == 'My Article'
    assert post.status == 'published'
    assert post.comments_enabled is True
    assert post.excerpt == 'Short description.'
    assert post.tags.filter(slug='python').exists()
    assert post.tags.filter(slug='django').exists()
    assert '<h1>' in post.content_html


def test_sync_updates_existing_post(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    content = textwrap.dedent("""\
        ---
        title: Original Title
        date: 2026-01-15
        tags: [python]
        status: draft
        comments: false
        ---
        Original content.
    """)
    write_post(posts_dir, 'my-article.md', content)
    sync_posts_from_dir(posts_dir)

    updated = textwrap.dedent("""\
        ---
        title: Updated Title
        date: 2026-01-15
        tags: [python, django]
        status: published
        comments: true
        ---
        Updated content.
    """)
    write_post(posts_dir, 'my-article.md', updated)
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='my-article')
    assert post.title == 'Updated Title'
    assert post.status == 'published'
    assert post.tags.count() == 2


def test_sync_sets_reading_time(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    words = ' '.join(['word'] * 400)
    write_post(posts_dir, 'long-article.md', f"---\ntitle: Long\ndate: 2026-01-15\ntags: []\nstatus: published\ncomments: true\n---\n{words}")
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='long-article')
    assert post.reading_time == 2


def test_sync_auto_generates_excerpt_when_missing(posts_dir):
    from blog.management.commands.sync_posts import sync_posts_from_dir
    from blog.models import Post

    write_post(posts_dir, 'no-excerpt.md', textwrap.dedent("""\
        ---
        title: No Excerpt
        date: 2026-01-15
        tags: []
        status: published
        comments: true
        ---
        This is the first paragraph content that should become the excerpt.

        Second paragraph.
    """))
    sync_posts_from_dir(posts_dir)

    post = Post.objects.get(slug='no-excerpt')
    assert len(post.excerpt) > 0
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_sync_posts.py -v
```

Expected: `ImportError` — `sync_posts_from_dir` not defined yet.

- [ ] **Step 3: Install dependencies and create management command**

```bash
pip install python-frontmatter markdown
pip freeze > requirements.txt
```

Create directories:

```bash
mkdir blog\management
echo. > blog\management\__init__.py
mkdir blog\management\commands
echo. > blog\management\commands\__init__.py
```

- [ ] **Step 4: Write `blog/management/commands/sync_posts.py`**

```python
import re
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
import frontmatter
import markdown as md
from datetime import datetime, date

from blog.models import Post, Tag


def render_markdown(content: str) -> str:
    return md.markdown(
        content,
        extensions=['fenced_code', 'codehilite', 'toc', 'tables'],
        extension_configs={
            'codehilite': {'css_class': 'highlight', 'guess_lang': False},
        },
    )


def extract_excerpt(content_md: str, max_chars: int = 200) -> str:
    paragraphs = [p.strip() for p in content_md.split('\n\n') if p.strip()]
    for para in paragraphs:
        if not para.startswith('#'):
            clean = re.sub(r'[*_`#\[\]()]', '', para).strip()
            return clean[:max_chars]
    return ''


def sync_posts_from_dir(posts_dir: Path) -> None:
    for md_file in sorted(posts_dir.glob('*.md')):
        post_data = frontmatter.load(str(md_file))
        metadata = post_data.metadata
        content_md = post_data.content

        slug = md_file.stem
        title = metadata.get('title', slug)
        status = metadata.get('status', 'draft')
        comments_enabled = bool(metadata.get('comments', True))
        excerpt = metadata.get('excerpt', '') or extract_excerpt(content_md)
        tag_names = metadata.get('tags', [])

        raw_date = metadata.get('date')
        if isinstance(raw_date, (datetime, date)):
            published_at = timezone.make_aware(
                datetime.combine(raw_date, datetime.min.time())
                if isinstance(raw_date, date) and not isinstance(raw_date, datetime)
                else raw_date
            )
        else:
            published_at = None

        content_html = render_markdown(content_md)

        post, _ = Post.objects.update_or_create(
            slug=slug,
            defaults={
                'title': title,
                'content_md': content_md,
                'content_html': content_html,
                'excerpt': excerpt,
                'status': status,
                'comments_enabled': comments_enabled,
                'file_path': str(md_file.relative_to(md_file.parent.parent.parent))
                    if md_file.parent.parent.parent.exists() else str(md_file),
                'published_at': published_at,
            },
        )
        post.reading_time = post.compute_reading_time()
        post.save(update_fields=['reading_time'])

        tags = []
        for tag_name in tag_names:
            tag_slug = slugify(tag_name)
            tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'name': tag_name})
            tags.append(tag)
        post.tags.set(tags)


class Command(BaseCommand):
    help = 'Sync Markdown posts from content/posts/ into the database'

    def handle(self, *args, **options):
        posts_dir = settings.CONTENT_DIR
        if not posts_dir.exists():
            self.stderr.write(f'Content directory not found: {posts_dir}')
            return
        sync_posts_from_dir(posts_dir)
        count = Post.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Synced posts. Total in DB: {count}'))
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_sync_posts.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Run the command manually**

```bash
python manage.py sync_posts
```

Expected: `Synced posts. Total in DB: 1` (the hello-world.md sample).

- [ ] **Step 7: Commit**

```bash
git add blog/management/ tests/test_sync_posts.py requirements.txt
git commit -m "feat: add sync_posts management command"
```

---

## Task 4: Views, URLs, and Forms

**Files:**
- Create: `blog/urls.py`
- Create: `blog/forms.py`
- Modify: `blog/views.py`
- Create: `tests/test_views.py`
- Create: `tests/test_forms.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_views.py`:

```python
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
```

Create `tests/test_forms.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/test_views.py tests/test_forms.py -v
```

Expected: `ImportError` — views/forms not defined.

- [ ] **Step 3: Write `blog/forms.py`**

```python
from django import forms
from blog.models import Comment


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'subscribe-input'})
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'email', 'body']
        widgets = {
            'author_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your comment...'}),
        }
```

- [ ] **Step 4: Write `blog/views.py`**

```python
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

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
    comment_form = CommentForm()

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
        except Exception:
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
            if created or not subscriber.confirmed:
                token = str(subscriber.unsubscribe_token)
                confirm_url = f"{settings.SITE_URL}/subscribe/confirm/{token}/"
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
    subscriber.delete()
    return render(request, 'blog/subscribe_confirm.html', {'action': 'unsubscribed'})
```

- [ ] **Step 5: Write `blog/urls.py`**

```python
from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('tags/<slug:slug>/', views.tag, name='tag'),
    path('search/', views.search, name='search'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/confirm/<uuid:token>/', views.confirm_subscription, name='confirm_subscription'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),
]
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
pytest tests/test_views.py tests/test_forms.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add blog/views.py blog/urls.py blog/forms.py tests/test_views.py tests/test_forms.py
git commit -m "feat: add views, URLs, and forms"
```

---

## Task 5: Django Admin

**Files:**
- Modify: `blog/admin.py`
- Create: `blog/templatetags/__init__.py`
- Create: `blog/templatetags/blog_extras.py`

- [ ] **Step 1: Write `blog/templatetags/blog_extras.py`**

```python
from django import template
from blog.management.commands.sync_posts import render_markdown

register = template.Library()


@register.filter
def reading_time_label(minutes: int) -> str:
    return f'{minutes} min read'


@register.simple_tag
def md_preview(content_md: str) -> str:
    return render_markdown(content_md)
```

- [ ] **Step 2: Write `blog/admin.py`**

```python
from django.contrib import admin
from django.utils.html import format_html
from blog.models import Post, Tag, Subscriber, Comment
from blog.management.commands.sync_posts import render_markdown


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'published_at', 'comments_enabled', 'reading_time', 'tag_list']
    list_filter = ['status', 'tags', 'comments_enabled']
    search_fields = ['title', 'content_md']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['content_html_preview', 'reading_time']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'status', 'published_at', 'tags', 'comments_enabled')}),
        ('Content', {'fields': ('content_md', 'content_html_preview')}),
        ('Meta', {'fields': ('excerpt', 'reading_time', 'file_path')}),
    )

    def tag_list(self, obj):
        return ', '.join(t.name for t in obj.tags.all())
    tag_list.short_description = 'Tags'

    def content_html_preview(self, obj):
        if obj.content_md:
            html = render_markdown(obj.content_md)
            return format_html(
                '<div style="max-height:400px;overflow:auto;border:1px solid #ccc;padding:1em">{}</div>',
                format_html(html)
            )
        return '—'
    content_html_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        obj.content_html = render_markdown(obj.content_md)
        obj.reading_time = obj.compute_reading_time()
        super().save_model(request, obj, form, change)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'confirmed', 'created_at']
    list_filter = ['confirmed']
    readonly_fields = ['unsubscribe_token', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'post', 'approved', 'created_at']
    list_filter = ['approved', 'post']
    actions = ['approve_comments']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
```

- [ ] **Step 3: Create a superuser and verify admin works**

```bash
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/` — verify Post, Tag, Subscriber, Comment are visible and the markdown preview renders in the Post form.

- [ ] **Step 4: Commit**

```bash
git add blog/admin.py blog/templatetags/
git commit -m "feat: configure Django admin with markdown preview"
```

---

## Task 6: Templates and Static Files

**Files:**
- Create: `templates/base.html`
- Create: `templates/components/post_card.html`
- Create: `templates/blog/home.html`
- Create: `templates/blog/post_list.html`
- Create: `templates/blog/post_detail.html`
- Create: `templates/blog/tag.html`
- Create: `templates/blog/search.html`
- Create: `templates/blog/subscribe.html`
- Create: `templates/blog/subscribe_confirm.html`
- Create: `static/css/main.css`
- Create: `static/js/main.js`

- [ ] **Step 1: Create directories**

```bash
mkdir templates\components
mkdir templates\blog
mkdir static\css
mkdir static\js
```

- [ ] **Step 2: Write `static/css/main.css`**

```css
:root {
  --bg: #ffffff;
  --bg-secondary: #f8f9fa;
  --text: #1a1a2e;
  --text-muted: #6c757d;
  --accent: #0066cc;
  --accent-hover: #0052a3;
  --border: #dee2e6;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.08);
  --code-bg: #f4f4f4;
  --font-body: system-ui, -apple-system, sans-serif;
  --font-mono: 'Cascadia Code', 'Fira Code', monospace;
}

[data-theme="dark"] {
  --bg: #0d1117;
  --bg-secondary: #161b22;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --accent: #58a6ff;
  --accent-hover: #79bcff;
  --border: #30363d;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.4);
  --code-bg: #1e1e2e;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  transition: background 0.2s, color 0.2s;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); text-decoration: underline; }

/* Header */
header {
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  height: 56px;
  gap: 2rem;
}
.site-title { font-size: 1.2rem; font-weight: 700; color: var(--text); }
.site-title:hover { text-decoration: none; color: var(--accent); }
nav { display: flex; gap: 1.25rem; }
nav a { color: var(--text-muted); font-size: 0.95rem; }
nav a:hover { color: var(--accent); text-decoration: none; }
.header-actions { margin-left: auto; display: flex; gap: 0.75rem; align-items: center; }
.search-form input {
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  width: 200px;
}
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 1rem;
}

/* Layout */
.container { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }

/* Post card */
.post-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
  transition: box-shadow 0.2s;
}
.post-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
.post-card h2 { font-size: 1.2rem; margin-bottom: 0.5rem; }
.post-card h2 a { color: var(--text); }
.post-card h2 a:hover { color: var(--accent); text-decoration: none; }
.post-excerpt { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 0.75rem; }
.post-meta { font-size: 0.85rem; color: var(--text-muted); display: flex; gap: 1rem; flex-wrap: wrap; }
.tag-badge {
  display: inline-block;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.tag-badge:hover { color: var(--accent); text-decoration: none; }

/* Hero post */
.hero-post {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}
.hero-post h1 { font-size: 1.8rem; margin-bottom: 0.75rem; }

/* Post grid */
.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Article */
.article-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 2rem;
  align-items: start;
}
.article-content {
  max-width: 720px;
}
.article-content h1, .article-content h2, .article-content h3 {
  margin: 1.5rem 0 0.75rem;
}
.article-content p { margin-bottom: 1rem; }
.article-content ul, .article-content ol { margin: 0 0 1rem 1.5rem; }
.article-content pre {
  background: var(--code-bg);
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1rem;
  font-family: var(--font-mono);
  font-size: 0.9rem;
}
.article-content code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--code-bg);
  padding: 0.15em 0.3em;
  border-radius: 3px;
}
.article-content pre code { background: none; padding: 0; }

/* Sidebar */
.sidebar { position: sticky; top: 72px; }
.sidebar-section { margin-bottom: 2rem; }
.sidebar-section h3 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.75rem; }

/* Comments */
.comments-section { margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 2rem; }
.comment { border-bottom: 1px solid var(--border); padding: 1rem 0; }
.comment-meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem; }

/* Forms */
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.9rem; margin-bottom: 0.3rem; }
.form-group input, .form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.95rem;
}
.btn {
  display: inline-block;
  padding: 0.5rem 1.25rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}
.btn:hover { background: var(--accent-hover); color: white; text-decoration: none; }

/* Subscribe bar in footer */
.subscribe-bar {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  padding: 2rem 1.5rem;
  text-align: center;
}
.subscribe-bar h3 { margin-bottom: 0.75rem; }
.subscribe-inline { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; }
.subscribe-input {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  width: 280px;
}

footer { border-top: 1px solid var(--border); padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.9rem; }

/* Pagination */
.pagination { display: flex; gap: 0.5rem; justify-content: center; margin-top: 2rem; }
.pagination a, .pagination span {
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 0.9rem;
}
.pagination .current { background: var(--accent); color: white; border-color: var(--accent); }

/* Messages */
.messages { list-style: none; margin-bottom: 1rem; }
.messages li { padding: 0.75rem 1rem; border-radius: 6px; background: #d4edda; color: #155724; margin-bottom: 0.5rem; }

/* Responsive */
@media (max-width: 768px) {
  .article-layout { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .search-form input { width: 140px; }
}

/* Pygments syntax highlighting */
.highlight { background: var(--code-bg) !important; }
```

- [ ] **Step 3: Write `static/js/main.js`**

```javascript
(function () {
  const STORAGE_KEY = 'theme';
  const btn = document.getElementById('theme-toggle');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  const saved = localStorage.getItem(STORAGE_KEY);
  const preferred = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(preferred);

  if (btn) {
    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });
  }
})();
```

- [ ] **Step 4: Write `templates/base.html`**

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}MyBlog{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/main.css' %}" />
  <script src="{% static 'js/main.js' %}" defer></script>
</head>
<body>
  <header>
    <div class="header-inner">
      <a href="{% url 'blog:home' %}" class="site-title">MyBlog</a>
      <nav>
        <a href="{% url 'blog:post_list' %}">Статьи</a>
        <a href="{% url 'blog:subscribe' %}">Подписка</a>
      </nav>
      <div class="header-actions">
        <form class="search-form" method="get" action="{% url 'blog:search' %}">
          <input type="search" name="q" placeholder="Поиск..." value="{{ request.GET.q|default:'' }}" />
        </form>
        <button id="theme-toggle" class="theme-toggle" aria-label="Toggle theme">🌙</button>
      </div>
    </div>
  </header>

  <main>
    {% if messages %}
      <div class="container">
        <ul class="messages">
          {% for message in messages %}<li>{{ message }}</li>{% endfor %}
        </ul>
      </div>
    {% endif %}
    {% block content %}{% endblock %}
  </main>

  <div class="subscribe-bar">
    <h3>Подписаться на новые статьи</h3>
    <form class="subscribe-inline" method="post" action="{% url 'blog:subscribe' %}">
      {% csrf_token %}
      <input type="email" name="email" class="subscribe-input" placeholder="your@email.com" required />
      <button type="submit" class="btn">Подписаться</button>
    </form>
  </div>

  <footer>
    <p>&copy; {% now "Y" %} MyBlog · <a href="{% url 'blog:post_list' %}">Все статьи</a></p>
  </footer>
</body>
</html>
```

- [ ] **Step 5: Write `templates/components/post_card.html`**

```html
<article class="post-card">
  <h2><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h2>
  {% if post.excerpt %}<p class="post-excerpt">{{ post.excerpt }}</p>{% endif %}
  <div class="post-meta">
    <span>{{ post.published_at|date:"j F Y" }}</span>
    <span>{{ post.reading_time }} мин</span>
    {% for tag in post.tags.all %}
      <a href="{% url 'blog:tag' tag.slug %}" class="tag-badge">{{ tag.name }}</a>
    {% endfor %}
  </div>
</article>
```

- [ ] **Step 6: Write `templates/blog/home.html`**

```html
{% extends "base.html" %}
{% block title %}MyBlog — Главная{% endblock %}
{% block content %}
<div class="container">
  {% if latest_post %}
  <div class="hero-post">
    <h1><a href="{{ latest_post.get_absolute_url }}">{{ latest_post.title }}</a></h1>
    {% if latest_post.excerpt %}<p class="post-excerpt">{{ latest_post.excerpt }}</p>{% endif %}
    <div class="post-meta">
      <span>{{ latest_post.published_at|date:"j F Y" }}</span>
      <span>{{ latest_post.reading_time }} мин</span>
      {% for tag in latest_post.tags.all %}
        <a href="{% url 'blog:tag' tag.slug %}" class="tag-badge">{{ tag.name }}</a>
      {% endfor %}
    </div>
  </div>
  {% endif %}

  <div class="post-grid">
    {% for post in posts %}
      {% include "components/post_card.html" %}
    {% empty %}
      <p>Статей пока нет.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Write `templates/blog/post_list.html`**

```html
{% extends "base.html" %}
{% block title %}Все статьи — MyBlog{% endblock %}
{% block content %}
<div class="container">
  <h1 style="margin-bottom:1.5rem">Все статьи</h1>

  <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem">
    <a href="{% url 'blog:post_list' %}" class="tag-badge {% if not active_tag %}btn{% endif %}">Все</a>
    {% for tag in tags %}
      <a href="{% url 'blog:post_list' %}?tag={{ tag.slug }}"
         class="tag-badge {% if active_tag.slug == tag.slug %}btn{% endif %}">{{ tag.name }}</a>
    {% endfor %}
  </div>

  <div class="post-grid">
    {% for post in page_obj %}
      {% include "components/post_card.html" %}
    {% empty %}
      <p>Нет статей по этому тегу.</p>
    {% endfor %}
  </div>

  {% if page_obj.has_other_pages %}
  <div class="pagination">
    {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}{% if active_tag %}&tag={{ active_tag.slug }}{% endif %}">&larr;</a>
    {% endif %}
    <span class="current">{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
    {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}{% if active_tag %}&tag={{ active_tag.slug }}{% endif %}">&rarr;</a>
    {% endif %}
  </div>
  {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 8: Write `templates/blog/post_detail.html`**

```html
{% extends "base.html" %}
{% block title %}{{ post.title }} — MyBlog{% endblock %}
{% block content %}
<div class="container">
  <div class="article-layout">
    <div>
      <header style="margin-bottom:2rem">
        <h1 style="font-size:2rem;margin-bottom:0.5rem">{{ post.title }}</h1>
        <div class="post-meta">
          <span>{{ post.published_at|date:"j F Y" }}</span>
          <span>{{ post.reading_time }} мин</span>
          {% for tag in post.tags.all %}
            <a href="{% url 'blog:tag' tag.slug %}" class="tag-badge">{{ tag.name }}</a>
          {% endfor %}
        </div>
      </header>

      <article class="article-content">{{ post.content_html|safe }}</article>

      {% if post.comments_enabled %}
      <section class="comments-section">
        <h2 style="margin-bottom:1.5rem">Комментарии</h2>
        {% for comment in comments %}
          <div class="comment">
            <div class="comment-meta"><strong>{{ comment.author_name }}</strong> · {{ comment.created_at|date:"j F Y" }}</div>
            <p>{{ comment.body }}</p>
          </div>
        {% empty %}
          <p style="color:var(--text-muted)">Комментариев пока нет. Будьте первым!</p>
        {% endfor %}

        <h3 style="margin-top:2rem;margin-bottom:1rem">Оставить комментарий</h3>
        <form method="post">
          {% csrf_token %}
          {% for field in comment_form %}
          <div class="form-group">
            <label>{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}<p style="color:red;font-size:0.85rem">{{ field.errors.0 }}</p>{% endif %}
          </div>
          {% endfor %}
          <button type="submit" class="btn">Отправить</button>
        </form>
      </section>
      {% endif %}
    </div>

    <aside class="sidebar">
      {% if post.tags.all %}
      <div class="sidebar-section">
        <h3>Теги</h3>
        {% for tag in post.tags.all %}
          <a href="{% url 'blog:tag' tag.slug %}" class="tag-badge" style="margin-right:0.3rem;margin-bottom:0.3rem;display:inline-block">{{ tag.name }}</a>
        {% endfor %}
      </div>
      {% endif %}

      {% if related_posts %}
      <div class="sidebar-section">
        <h3>Похожие статьи</h3>
        {% for rp in related_posts %}
          <div style="margin-bottom:0.75rem">
            <a href="{{ rp.get_absolute_url }}" style="font-size:0.95rem;color:var(--text)">{{ rp.title }}</a>
            <div style="font-size:0.8rem;color:var(--text-muted)">{{ rp.published_at|date:"j F Y" }}</div>
          </div>
        {% endfor %}
      </div>
      {% endif %}
    </aside>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 9: Write remaining templates**

Create `templates/blog/tag.html`:

```html
{% extends "base.html" %}
{% block title %}#{{ tag.name }} — MyBlog{% endblock %}
{% block content %}
<div class="container">
  <h1 style="margin-bottom:1.5rem">Тег: #{{ tag.name }}</h1>
  <div class="post-grid">
    {% for post in posts %}{% include "components/post_card.html" %}{% empty %}<p>Нет статей.</p>{% endfor %}
  </div>
</div>
{% endblock %}
```

Create `templates/blog/search.html`:

```html
{% extends "base.html" %}
{% block title %}Поиск: {{ query }} — MyBlog{% endblock %}
{% block content %}
<div class="container">
  <h1 style="margin-bottom:1.5rem">Результаты поиска: «{{ query }}»</h1>
  <div class="post-grid">
    {% for post in results %}{% include "components/post_card.html" %}{% empty %}<p>Ничего не найдено.</p>{% endfor %}
  </div>
</div>
{% endblock %}
```

Create `templates/blog/subscribe.html`:

```html
{% extends "base.html" %}
{% block title %}Подписка — MyBlog{% endblock %}
{% block content %}
<div class="container" style="max-width:500px">
  <h1 style="margin-bottom:1.5rem">Подписаться на блог</h1>
  {% if submitted %}
    <p>Проверьте почту и подтвердите подписку.</p>
  {% else %}
    <form method="post">
      {% csrf_token %}
      <div class="form-group">
        <label>Email</label>
        {{ form.email }}
        {% if form.email.errors %}<p style="color:red;font-size:0.85rem">{{ form.email.errors.0 }}</p>{% endif %}
      </div>
      <button type="submit" class="btn">Подписаться</button>
    </form>
  {% endif %}
</div>
{% endblock %}
```

Create `templates/blog/subscribe_confirm.html`:

```html
{% extends "base.html" %}
{% block title %}{% if action == 'confirmed' %}Подтверждено{% else %}Отписка{% endif %} — MyBlog{% endblock %}
{% block content %}
<div class="container" style="max-width:500px;text-align:center;padding-top:3rem">
  {% if action == 'confirmed' %}
    <h1>Подписка подтверждена ✓</h1>
    <p style="margin-top:1rem;color:var(--text-muted)">Вы будете получать уведомления о новых статьях.</p>
  {% else %}
    <h1>Вы отписались</h1>
    <p style="margin-top:1rem;color:var(--text-muted)">Вы больше не будете получать письма.</p>
  {% endif %}
  <a href="{% url 'blog:home' %}" class="btn" style="margin-top:1.5rem;display:inline-block">На главную</a>
</div>
{% endblock %}
```

- [ ] **Step 10: Run all tests and smoke-test the site**

```bash
pytest -v
python manage.py sync_posts
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — verify home page loads with the sample post.

- [ ] **Step 11: Commit**

```bash
git add templates/ static/
git commit -m "feat: add templates and static files"
```

---

## Task 7: notify_subscribers Command

**Files:**
- Create: `blog/management/commands/notify_subscribers.py`

- [ ] **Step 1: Write `blog/management/commands/notify_subscribers.py`**

```python
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
```

- [ ] **Step 2: Test manually**

```bash
python manage.py notify_subscribers
```

Expected: `No new posts to notify about.` (since sample post is older, or time window issue) — this is fine, the command runs without errors.

- [ ] **Step 3: Commit**

```bash
git add blog/management/commands/notify_subscribers.py
git commit -m "feat: add notify_subscribers management command"
```

---

## Task 8: Deployment Configuration

**Files:**
- Create: `requirements.txt` (update)
- Create: `Procfile` (for reference)
- Create: `deploy.sh`

- [ ] **Step 1: Add gunicorn to requirements**

```bash
pip install gunicorn
pip freeze > requirements.txt
```

- [ ] **Step 2: Create `deploy.sh`**

```bash
#!/bin/bash
set -e

echo "==> Pulling latest code"
git pull

echo "==> Installing dependencies"
pip install -r requirements.txt

echo "==> Running migrations"
python manage.py migrate --settings=myblog.settings.production

echo "==> Syncing posts"
python manage.py sync_posts --settings=myblog.settings.production

echo "==> Collecting static files"
python manage.py collectstatic --noinput --settings=myblog.settings.production

echo "==> Notifying subscribers"
python manage.py notify_subscribers --settings=myblog.settings.production

echo "==> Reloading Gunicorn"
pkill -HUP gunicorn || true

echo "==> Done"
```

- [ ] **Step 3: Create sample nginx config `nginx.conf.example`**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- [ ] **Step 4: Run full test suite one final time**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 5: Final commit**

```bash
git add requirements.txt deploy.sh nginx.conf.example
git commit -m "feat: add deployment scripts and nginx config"
```

---

## Summary

After completing all tasks you will have:

- A working Django blog at `http://127.0.0.1:8000/`
- Markdown files in `content/posts/` sync to DB via `python manage.py sync_posts`
- Django admin at `/admin/` with markdown preview, tag management, comment moderation
- Full-text search (PostgreSQL) with SQLite fallback
- Email subscription with double opt-in and one-click unsubscribe
- Per-post comment toggle with moderation
- Light/dark mode UI with Tailwind-inspired custom CSS
- Deploy-ready with Gunicorn + WhiteNoise
