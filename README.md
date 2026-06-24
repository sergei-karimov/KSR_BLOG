# KSR Blog

Персональный блог на Django. Статьи пишутся в Markdown-файлах с YAML frontmatter и синхронизируются в базу данных командой `sync_posts`. Управление публикациями — через Django admin.

---

## Стек

- **Python 3.12+** / **Django 5.1**
- **PostgreSQL** (production) / **SQLite** (локально)
- **python-frontmatter** + **python-markdown** + **Pygments** — рендер статей
- **WhiteNoise** — раздача статики
- **Tailwind-inspired CSS** с тёмной темой
- **Gunicorn** + **Nginx** — деплой

---

## Быстрый старт

```bash
git clone https://github.com/sergei-karimov/KSR_BLOG.git
cd KSR_BLOG

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements-dev.txt

cp .env.example .env
# Заполните .env: SECRET_KEY, DJANGO_SETTINGS_MODULE=myblog.settings.local

python manage.py migrate
python manage.py createsuperuser
python manage.py sync_posts
python manage.py runserver
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Admin-панель: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## Структура проекта

```
KSR_BLOG/
├── content/
│   └── posts/              # Markdown-статьи
├── blog/                   # Django-приложение
│   ├── models.py           # Post, Tag, Subscriber, Comment
│   ├── views.py            # Все страницы
│   ├── admin.py            # Панель управления
│   ├── forms.py            # Формы подписки и комментариев
│   └── management/commands/
│       ├── sync_posts.py          # MD → БД
│       └── notify_subscribers.py  # Рассылка подписчикам
├── templates/              # HTML-шаблоны
├── static/
│   ├── css/main.css        # Стили (светлая + тёмная тема)
│   ├── js/main.js          # Переключатель темы
│   └── images/posts/       # Обложки статей
├── myblog/settings/
│   ├── base.py
│   ├── local.py            # SQLite, DEBUG=True
│   └── production.py       # PostgreSQL, HTTPS
├── tests/                  # 56 тестов, 100% покрытие
├── deploy.sh               # Скрипт деплоя
└── nginx.conf.example      # Пример конфига Nginx
```

---

## Написание статей

Создайте файл в `content/posts/` с YAML frontmatter:

```markdown
---
title: "Заголовок статьи"
date: 2026-06-24
tags: [python, django]
status: published        # published | draft
comments: true           # true | false
excerpt: "Краткое описание для карточки."
cover: "my-image.jpg"    # файл из static/images/posts/ (необязательно)
---

Текст статьи в Markdown...
```

Затем загрузите в БД:

```bash
python manage.py sync_posts
```

> **Важно:** сохраняйте файлы в кодировке **UTF-8** (без BOM). Если используете Windows Notepad — выбирайте «UTF-8» в диалоге сохранения.

---

## Обложка статьи

Положите изображение в `static/images/posts/` и укажите имя файла в frontmatter:

```yaml
cover: "my-cover.jpg"
```

Поддерживаются также внешние URL:

```yaml
cover: "https://example.com/image.jpg"
```

---

## Функциональность

| Раздел | Описание |
|--------|----------|
| `/` | Главная: последняя статья + сетка карточек |
| `/posts/` | Список статей с мультитег-фильтром |
| `/posts/<slug>/` | Статья с комментариями и похожими материалами |
| `/search/?q=` | Полнотекстовый поиск (PostgreSQL) / icontains (SQLite) |
| `/subscribe/` | Подписка на новые статьи (double opt-in) |
| `/admin/` | Управление статьями, тегами, подписчиками, комментариями |

**Тёмная тема** переключается кнопкой в хедере, настройка сохраняется в `localStorage`.

---

## Django Admin

- **Статьи** — превью Markdown прямо в форме редактирования, управление тегами, черновики, переключатель комментариев
- **Комментарии** — модерация с массовым одобрением
- **Подписчики** — список с фильтром по статусу подтверждения

---

## Управляющие команды

```bash
# Синхронизировать статьи из MD-файлов в БД
python manage.py sync_posts

# Отправить письма подписчикам о новых статьях (за последние 24 часа)
python manage.py notify_subscribers

# Настраиваемый период
python manage.py notify_subscribers --hours=48
```

---

## Тесты

```bash
# Запустить тесты
pytest

# С покрытием кода
pytest --cov=blog --cov-report=term-missing
```

56 тестов, покрытие **100%**.

---

## Деплой на VPS

### 1. Подготовка сервера

```bash
# Установить PostgreSQL, Nginx, Python
sudo apt install postgresql nginx python3-venv

# Создать БД
sudo -u postgres createdb ksr_blog
sudo -u postgres createuser ksr_blog
```

### 2. Клонировать и настроить

```bash
git clone https://github.com/sergei-karimov/KSR_BLOG.git /var/www/ksr_blog
cd /var/www/ksr_blog

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Заполнить .env: SECRET_KEY, DB_*, EMAIL_*, SITE_URL, DJANGO_SETTINGS_MODULE=myblog.settings.production
```

### 3. Первый запуск

```bash
python manage.py migrate --settings=myblog.settings.production
python manage.py createsuperuser --settings=myblog.settings.production
python manage.py sync_posts --settings=myblog.settings.production
python manage.py collectstatic --noinput --settings=myblog.settings.production
```

### 4. Gunicorn

```bash
gunicorn myblog.wsgi:application --bind 127.0.0.1:8000 --workers 3 --daemon
```

### 5. Nginx

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/ksr_blog
# Отредактируйте server_name и пути к SSL-сертификатам
sudo ln -s /etc/nginx/sites-available/ksr_blog /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 6. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com
```

### 7. Последующие деплои

```bash
bash deploy.sh
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `127.0.0.1,localhost` |
| `DJANGO_SETTINGS_MODULE` | Модуль настроек | `myblog.settings.local` |
| `DB_NAME` | Имя БД (prod) | — |
| `DB_USER` | Пользователь БД (prod) | — |
| `DB_PASSWORD` | Пароль БД (prod) | — |
| `DB_HOST` | Хост БД | `localhost` |
| `EMAIL_HOST` | SMTP-сервер | — |
| `EMAIL_HOST_USER` | SMTP логин | — |
| `EMAIL_HOST_PASSWORD` | SMTP пароль | — |
| `DEFAULT_FROM_EMAIL` | Адрес отправителя | `blog@example.com` |
| `SITE_URL` | Полный URL сайта | `http://localhost:8000` |

---

## Лицензия

MIT
