# MyBlog — Design Spec
**Date:** 2026-06-23  
**Status:** Approved

---

## Overview

A personal blog built with Python Django. Articles are authored as Markdown files with YAML frontmatter, stored in the repository. Django reads and syncs them into a PostgreSQL database. The author manages metadata (tags, publish status, comments toggle) via Django admin.

---

## Architecture

### Repository Structure

```
MyBlog/
├── content/
│   └── posts/          # Markdown article files
├── blog/               # Django app (models, views, admin, management commands)
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── manage.py
├── requirements.txt
└── .env.example
```

### Key Layers

1. **Content layer** — `.md` files with YAML frontmatter in `content/posts/`
2. **Sync layer** — `sync_posts` management command parses MD files and upserts into DB; runs on deploy
3. **Data layer** — PostgreSQL on production, SQLite locally
4. **Presentation layer** — Django views render HTML; static files served via WhiteNoise

### Frontmatter Schema

```yaml
---
title: "Article Title"
date: 2026-06-23
tags: [python, django]
status: published       # published | draft
comments: true          # true | false
excerpt: "Optional short description shown in post cards"
---
Article body in Markdown...
```

---

## Data Models

### Post
| Field | Type | Notes |
|-------|------|-------|
| slug | SlugField (unique) | derived from filename |
| title | CharField | from frontmatter |
| content_md | TextField | raw Markdown |
| content_html | TextField | rendered HTML, cached |
| excerpt | TextField | from frontmatter or auto-generated |
| status | CharField | `published` / `draft` |
| comments_enabled | BooleanField | per-post toggle |
| file_path | CharField | relative path to source MD file |
| created_at | DateTimeField | auto |
| published_at | DateTimeField | from frontmatter `date` |
| reading_time | IntegerField | computed in minutes |

### Tag
| Field | Type |
|-------|------|
| name | CharField (unique) |
| slug | SlugField (unique) |

### PostTag (M2M through table)
| Field | Type |
|-------|------|
| post | FK → Post |
| tag | FK → Tag |

### Subscriber
| Field | Type | Notes |
|-------|------|-------|
| email | EmailField (unique) | |
| confirmed | BooleanField | double opt-in |
| created_at | DateTimeField | |
| unsubscribe_token | UUIDField | unique, used in unsubscribe link |

### Comment
| Field | Type | Notes |
|-------|------|-------|
| post | FK → Post | |
| author_name | CharField | |
| email | EmailField | not shown publicly |
| body | TextField | |
| approved | BooleanField | moderated in admin |
| created_at | DateTimeField | |

---

## URL Structure

| URL | View | Description |
|-----|------|-------------|
| `/` | HomeView | Latest posts + search bar |
| `/posts/` | PostListView | All published posts, filterable by tag |
| `/posts/<slug>/` | PostDetailView | Single article |
| `/tags/<slug>/` | TagView | Posts filtered by tag |
| `/search/?q=` | SearchView | Full-text search results |
| `/subscribe/` | SubscribeView | Email subscription form |
| `/subscribe/confirm/<token>/` | ConfirmSubscriptionView | Email confirmation link |
| `/unsubscribe/<token>/` | UnsubscribeView | One-click unsubscribe |

---

## Django Admin

- **Post:** list with status/tag filters, inline tag editor, live MD→HTML preview panel, comments_enabled toggle
- **Tag:** simple CRUD
- **Subscriber:** list with confirmed filter, bulk delete
- **Comment:** list with approved filter, bulk approve/delete

---

## Search

Full-text search using PostgreSQL `tsvector` on `title` + `content_md`. Index created via migration. `SearchView` returns ranked results with keyword highlighted in excerpts.

For local development (SQLite), falls back to `icontains` on title and content.

---

## Subscriptions & Notifications

**Subscription flow:**
1. User submits email via `/subscribe/` form
2. Confirmation email sent with unique token link
3. User clicks link → `confirmed = True`

**New post notification:**
- Management command `notify_subscribers` sends email to all confirmed subscribers
- Called manually or as part of deploy pipeline after `sync_posts`
- Email contains article title, excerpt, and link
- Footer includes one-click unsubscribe link

**Email backend:** SMTP (configurable via `EMAIL_*` env vars). Compatible with SendGrid, Mailgun, etc.

---

## Comments

- Per-post toggle via `comments_enabled` field (set in frontmatter or overridden in admin)
- Comments require admin approval before appearing publicly (`approved = False` by default)
- No authentication required to post a comment (name + email + body)
- Comments section hidden entirely when `comments_enabled = False`

---

## UI & Frontend

**Stack:** Django templates + Tailwind CSS (CDN for development, build step for production) + vanilla JS only where needed (dark mode toggle, search debounce).

**Color scheme:** Light mode default with dark mode toggle. CSS custom properties (`--color-*`) for theming. Toggle state persisted in `localStorage`.

**Typography:** System font stack; article body max-width ~720px for readability.

**Syntax highlighting:** Pygments (server-side, zero client JS).

### Page Layouts

**Home (`/`):**
- Fixed header: blog name + nav links + search icon
- Hero card: latest published post (large)
- Post grid: next 6 posts as cards (title, excerpt, tags, date, reading time)
- Footer: nav links + email subscription form

**Post list (`/posts/`):**
- Tag filter bar at top
- Paginated post cards (10 per page)

**Post detail (`/posts/<slug>/`):**
- Article with full typography styles
- Sidebar (desktop): tag list, related posts (same tags)
- Comments section below article (if enabled)

**Search results (`/search/`):**
- Query echoed at top
- Result list with highlighted excerpt

**Responsive:** mobile-first; sidebar collapses below article on small screens.

---

## Deployment

**Target:** VPS (DigitalOcean / Hetzner / Azure VM)

**Stack:**
- Gunicorn as WSGI server
- Nginx as reverse proxy + SSL termination (Let's Encrypt)
- PostgreSQL
- WhiteNoise for static files

**Environment variables (`.env`):**
`SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `EMAIL_*`

**Deploy steps:**
1. `git pull`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py sync_posts`
5. `python manage.py collectstatic --noinput`
6. `python manage.py notify_subscribers` (only when new posts exist)
7. Gunicorn reload

---

## Out of Scope

- User authentication (single-author, admin-only)
- REST API
- CMS or WYSIWYG editor
- Multiple authors
