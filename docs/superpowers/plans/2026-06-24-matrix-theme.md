# Matrix Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Переделать визуальный стиль блога KSR_BLOG в атмосферу фильма «Матрица» — чёрный фон, зелёные акценты, ASCII-декор, цифровой дождь в hero, при этом оставив текст статей читабельным.

**Architecture:** Изменения только в CSS, JS и шаблонах — модели, views и management commands не затрагиваются. Matrix-тёмная тема становится дефолтной; существующий переключатель сохраняет светлую тему как запасную. Цифровой дождь рендерится через `<canvas>` только в hero-блоке главной страницы с оптимизацией через `requestAnimationFrame` и `IntersectionObserver`.

**Tech Stack:** Django templates, CSS custom properties, vanilla JS Canvas API

---

## File Map

| Файл | Действие | Что меняется |
|------|----------|-------------|
| `static/css/main.css` | Modify | Полная замена CSS-переменных и стилей компонентов |
| `static/js/main.js` | Modify | Добавить digital rain + IntersectionObserver |
| `templates/base.html` | Modify | Навигация в терминальном стиле, footer |
| `templates/blog/home.html` | Modify | Hero с `<canvas>`, ASCII-метки |
| `templates/components/post_card.html` | Modify | Терминальный стиль карточек |
| `templates/blog/post_list.html` | Modify | Теги в стиле `[ tag ]`, заголовок страницы |
| `templates/blog/post_detail.html` | Modify | ASCII-рамка заголовка, breadcrumb, sidebar |

---

## Task 1: CSS — Matrix Color Variables & Base Styles

**Files:**
- Modify: `static/css/main.css`

- [ ] **Step 1: Заменить CSS-переменные и базовые стили**

Открыть `static/css/main.css` и полностью заменить содержимое на:

```css
:root {
  --bg:           #050a05;
  --bg-secondary: #0a1a0a;
  --bg-nav:       #030803;
  --bg-code:      #000000;
  --text:         #c8ffc8;
  --text-muted:   rgba(0, 255, 65, 0.5);
  --text-dim:     rgba(0, 255, 65, 0.25);
  --accent:       #00ff41;
  --accent-glow:  #39ff14;
  --border:       rgba(0, 255, 65, 0.15);
  --border-hover: rgba(0, 255, 65, 0.4);
  --card-shadow:  none;
  --font-body:    system-ui, -apple-system, sans-serif;
  --font-mono:    'Courier New', 'Cascadia Code', monospace;
  --message-bg:   #0a1a0a;
  --message-text: #00ff41;
}

[data-theme="light"] {
  --bg:           #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-nav:       #ffffff;
  --bg-code:      #f4f4f4;
  --text:         #1a1a2e;
  --text-muted:   #6c757d;
  --text-dim:     #adb5bd;
  --accent:       #0066cc;
  --accent-glow:  #0052a3;
  --border:       #dee2e6;
  --border-hover: #adb5bd;
  --card-shadow:  0 2px 8px rgba(0,0,0,0.08);
  --font-body:    system-ui, -apple-system, sans-serif;
  --font-mono:    'Cascadia Code', 'Fira Code', monospace;
  --message-bg:   #d4edda;
  --message-text: #155724;
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
a:hover { color: var(--accent-glow); text-decoration: none; }

/* ── Header ── */
header {
  border-bottom: 1px solid var(--border);
  background: var(--bg-nav);
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
.site-title {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 4px;
  color: var(--accent);
  text-shadow: 0 0 10px var(--accent), 0 0 20px rgba(0,255,65,0.3);
}
.site-title:hover { color: var(--accent-glow); text-decoration: none; }
nav { display: flex; gap: 1.25rem; }
nav a {
  font-family: var(--font-mono);
  color: var(--text-muted);
  font-size: 0.9rem;
}
nav a::before { content: '['; }
nav a::after  { content: ']'; }
nav a:hover { color: var(--accent); }
.header-actions { margin-left: auto; display: flex; gap: 0.75rem; align-items: center; }
.search-form input {
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  padding: 0.3rem 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  width: 200px;
  border-radius: 0;
  outline: none;
}
.search-form input:focus { border-color: var(--accent); box-shadow: 0 0 6px rgba(0,255,65,0.3); }
.search-form input::placeholder { color: var(--text-dim); }
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  color: var(--accent);
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 0;
  font-size: 1rem;
  font-family: var(--font-mono);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.theme-toggle:hover { border-color: var(--accent); box-shadow: 0 0 6px rgba(0,255,65,0.3); }

/* ── Layout ── */
.container { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }

/* ── Hero block (home page) ── */
.hero-wrap {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}
.hero-canvas {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  opacity: 0.2;
  pointer-events: none;
}
.hero-content {
  position: relative;
  z-index: 2;
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}
.hero-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 3px;
  color: var(--text-dim);
  margin-bottom: 0.75rem;
}
.hero-title {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--accent-glow);
  text-shadow: 0 0 10px var(--accent-glow), 0 0 20px rgba(57,255,20,0.3);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}
.hero-meta {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.hero-meta::before { content: '> '; }
.hero-excerpt {
  color: var(--text);
  font-size: 1rem;
  line-height: 1.7;
  max-width: 640px;
  margin-bottom: 1.25rem;
}
.hero-read-link {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--accent);
  border: 1px solid var(--border);
  padding: 0.3rem 0.9rem;
}
.hero-read-link:hover { border-color: var(--accent); box-shadow: 0 0 8px rgba(0,255,65,0.3); color: var(--accent-glow); }

/* ── Post grid ── */
.archive-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 3px;
  color: var(--text-dim);
  margin-bottom: 1.25rem;
}
.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

/* ── Post card ── */
.post-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 0;
  padding: 1.25rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.post-card:hover { border-color: var(--border-hover); box-shadow: 0 0 12px rgba(0,255,65,0.1); }
.post-card-tag {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}
.post-card h2 { font-size: 1rem; margin-bottom: 0.5rem; font-family: var(--font-body); }
.post-card h2 a { color: var(--text); font-weight: 600; }
.post-card h2 a:hover { color: var(--accent); }
.post-excerpt { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem; line-height: 1.6; }
.post-meta {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}
.post-meta::before { content: '> '; color: var(--text-dim); }

/* ── Cover images ── */
.cover-image {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border: 1px solid var(--border);
  margin-bottom: 2rem;
  display: block;
}
.post-card-cover {
  width: calc(100% + 2.5rem);
  height: 160px;
  object-fit: cover;
  display: block;
  margin: -1.25rem -1.25rem 1rem -1.25rem;
  border-bottom: 1px solid var(--border);
}

/* ── Tag badges ── */
.tag-badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--accent);
  border: 1px solid var(--border);
  padding: 0.1rem 0.4rem;
}
.tag-badge::before { content: '[ '; }
.tag-badge::after  { content: ' ]'; }
.tag-badge:hover { border-color: var(--accent); color: var(--accent-glow); }

/* ── Tag filter bar ── */
.tag-filter { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.tag-filter-item {
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 0.15rem 0.1rem;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  user-select: none;
}
.tag-filter-item::before { content: '[ '; }
.tag-filter-item::after  { content: ' ]'; }
.tag-filter-item:hover { color: var(--accent); }
.tag-filter-item.active { color: var(--accent-glow); border-bottom-color: var(--accent); font-weight: 500; }

/* ── Article page ── */
.article-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 2rem;
  align-items: start;
}
.post-breadcrumb {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-bottom: 1.5rem;
}
.post-title-wrap {
  margin-bottom: 1.25rem;
}
.post-title-border {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 1px;
}
.post-title {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--accent-glow);
  text-shadow: 0 0 8px rgba(57,255,20,0.4);
  margin: 0.4rem 0;
  line-height: 1.3;
}
.article-content { max-width: 720px; }
.article-content h1, .article-content h2, .article-content h3 {
  font-family: var(--font-mono);
  color: var(--accent);
  margin: 1.75rem 0 0.75rem;
}
.article-content h1 { font-size: 1.4rem; }
.article-content h2 { font-size: 1.2rem; }
.article-content h3 { font-size: 1rem; }
.article-content p { margin-bottom: 1rem; line-height: 1.9; }
.article-content ul, .article-content ol { margin: 0 0 1rem 1.5rem; }
.article-content li { margin-bottom: 0.3rem; }
.article-content pre {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  padding: 1rem;
  overflow-x: auto;
  margin-bottom: 1.25rem;
  font-family: var(--font-mono);
  font-size: 0.88rem;
  line-height: 1.7;
  position: relative;
}
.article-content pre::before {
  content: '$ ';
  color: var(--text-dim);
  font-size: 0.75rem;
  display: block;
  margin-bottom: 0.5rem;
}
.article-content code {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--bg-secondary);
  color: var(--accent);
  padding: 0.1em 0.35em;
  border: 1px solid var(--border);
}
.article-content pre code { background: none; padding: 0; border: none; color: var(--accent); }

/* ── Sidebar ── */
.sidebar { position: sticky; top: 72px; }
.sidebar-section { margin-bottom: 2rem; }
.sidebar-section h3 {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 3px;
  color: var(--text-dim);
  margin-bottom: 0.75rem;
}
.sidebar-related-item { margin-bottom: 0.75rem; }
.sidebar-related-item a { font-size: 0.9rem; color: var(--text); }
.sidebar-related-item a:hover { color: var(--accent); }
.sidebar-related-date { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); }

/* ── Comments ── */
.comments-section { margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 2rem; }
.comments-section h2 {
  font-family: var(--font-mono);
  color: var(--accent);
  font-size: 1rem;
  letter-spacing: 2px;
  margin-bottom: 1.5rem;
}
.comment { border-bottom: 1px solid var(--border); padding: 1rem 0; }
.comment-meta { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }

/* ── Forms ── */
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.3rem; }
.form-group input, .form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.95rem;
  border-radius: 0;
  outline: none;
}
.form-group input:focus, .form-group textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 6px rgba(0,255,65,0.2);
}
.btn {
  display: inline-block;
  padding: 0.5rem 1.25rem;
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  transition: background 0.15s, box-shadow 0.15s;
}
.btn:hover { background: rgba(0,255,65,0.1); box-shadow: 0 0 10px rgba(0,255,65,0.3); color: var(--accent-glow); }

/* ── Subscribe bar ── */
.subscribe-bar {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  padding: 2rem 1.5rem;
  text-align: center;
}
.subscribe-bar h3 {
  font-family: var(--font-mono);
  color: var(--accent);
  font-size: 0.9rem;
  letter-spacing: 2px;
  margin-bottom: 0.75rem;
}
.subscribe-inline { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; }
.subscribe-input {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 0.9rem;
  width: 280px;
  border-radius: 0;
  outline: none;
}
.subscribe-input:focus { border-color: var(--accent); }
.subscribe-input::placeholder { color: var(--text-dim); }

/* ── Footer ── */
footer {
  border-top: 1px solid var(--border);
  padding: 1.25rem 1.5rem;
  text-align: center;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ── Pagination ── */
.pagination { display: flex; gap: 0.5rem; justify-content: center; margin-top: 2rem; }
.pagination a, .pagination span {
  font-family: var(--font-mono);
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  font-size: 0.85rem;
  color: var(--text-muted);
}
.pagination a:hover { border-color: var(--accent); color: var(--accent); }
.pagination .current { border-color: var(--accent); color: var(--accent); }

/* ── Messages ── */
.messages { list-style: none; margin-bottom: 1rem; }
.messages li {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  background: var(--message-bg);
  color: var(--message-text);
  font-family: var(--font-mono);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

/* ── Page headings ── */
.page-heading {
  font-family: var(--font-mono);
  font-size: 1rem;
  letter-spacing: 3px;
  color: var(--text-dim);
  margin-bottom: 1.5rem;
}

/* ── Pygments syntax highlighting ── */
.highlight { background: var(--bg-code) !important; border: 1px solid var(--border); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .article-layout { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .search-form input { width: 120px; }
  .hero-title { font-size: 1.3rem; }
}
```

- [ ] **Step 2: Запустить тесты — убедиться что ничего не сломалось**

```bash
pytest
```

Ожидаемый результат: все тесты проходят (изменения только в CSS).

- [ ] **Step 3: Commit**

```bash
git add static/css/main.css
git commit -m "style: replace CSS with Matrix dark theme"
```

---

## Task 2: JS — Default Dark Theme + Digital Rain

**Files:**
- Modify: `static/js/main.js`

- [ ] **Step 1: Заменить main.js**

Открыть `static/js/main.js` и заменить содержимое на:

```javascript
// ── Theme toggle ──
(function () {
  var STORAGE_KEY = 'theme';
  var btn = document.getElementById('theme-toggle');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (btn) btn.textContent = theme === 'light' ? '🌙' : '◑';
  }

  // Matrix dark is default; light only if user explicitly chose it
  var saved = localStorage.getItem(STORAGE_KEY);
  applyTheme(saved === 'light' ? 'light' : 'dark');

  if (btn) {
    btn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      var next = current === 'light' ? 'dark' : 'light';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });
  }
})();

// ── Digital Rain (hero block on home page only) ──
(function () {
  var wrap = document.getElementById('hero-wrap');
  var canvas = document.getElementById('hero-canvas');
  if (!wrap || !canvas) return;

  var ctx = canvas.getContext('2d');
  var CHAR_SIZE = 13;
  var chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ01ABCDEF'.split('');
  var drops = [];
  var running = true;
  var lastTs = 0;
  var RAF_INTERVAL = 66; // ~15 FPS

  function resize() {
    canvas.width  = wrap.offsetWidth;
    canvas.height = wrap.offsetHeight;
    drops = Array(Math.floor(canvas.width / CHAR_SIZE)).fill(1);
  }

  function draw(ts) {
    requestAnimationFrame(draw);
    if (!running) return;
    if (ts - lastTs < RAF_INTERVAL) return;
    lastTs = ts;

    ctx.fillStyle = 'rgba(0, 0, 0, 0.06)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff41';
    ctx.font = CHAR_SIZE + 'px monospace';

    for (var i = 0; i < drops.length; i++) {
      var ch = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(ch, i * CHAR_SIZE, drops[i] * CHAR_SIZE);
      if (drops[i] * CHAR_SIZE > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  // Pause when hero is not visible
  var observer = new IntersectionObserver(function (entries) {
    running = entries[0].isIntersecting;
  });
  observer.observe(wrap);

  resize();
  window.addEventListener('resize', resize);
  requestAnimationFrame(draw);
})();

// ── Tag filter multi-select ──
(function () {
  var items = document.querySelectorAll('.tag-filter-item');
  if (!items.length) return;

  items.forEach(function (el) {
    el.addEventListener('click', function () {
      var slug = this.dataset.slug;
      var url = new URL(window.location.href);
      var selected = url.searchParams.getAll('tag');

      if (selected.includes(slug)) {
        url.searchParams.delete('tag');
        selected.filter(function (s) { return s !== slug; })
                .forEach(function (s) { url.searchParams.append('tag', s); });
      } else {
        url.searchParams.append('tag', slug);
      }
      url.searchParams.delete('page');
      window.location.href = url.toString();
    });
  });
})();
```

- [ ] **Step 2: Запустить тесты**

```bash
pytest
```

Ожидаемый результат: все тесты проходят.

- [ ] **Step 3: Commit**

```bash
git add static/js/main.js
git commit -m "feat: add digital rain animation with IntersectionObserver optimization"
```

---

## Task 3: base.html — Terminal Navigation & Footer

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Заменить base.html**

Открыть `templates/base.html` и заменить содержимое на:

```html
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{% block title %}KSR_BLOG{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/main.css' %}" />
  <script src="{% static 'js/main.js' %}" defer></script>
</head>
<body>
  <header>
    <div class="header-inner">
      <a href="{% url 'blog:home' %}" class="site-title">KSR_BLOG</a>
      <nav>
        <a href="{% url 'blog:post_list' %}">posts</a>
        <a href="{% url 'blog:search' %}">search</a>
      </nav>
      <div class="header-actions">
        <a href="{% url 'blog:subscribe' %}" class="theme-toggle" aria-label="Подписаться" title="Подписаться">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        </a>
        <button id="theme-toggle" class="theme-toggle" aria-label="Toggle theme">◑</button>
      </div>
    </div>
  </header>

  <main>
    {% if messages %}
      <div class="container">
        <ul class="messages">
          {% for message in messages %}<li>&gt; {{ message }}</li>{% endfor %}
        </ul>
      </div>
    {% endif %}
    {% block content %}{% endblock %}
  </main>

  {% block subscribe_bar %}
  <div class="subscribe-bar">
    <h3>▓▒░ SUBSCRIBE ░▒▓</h3>
    <form class="subscribe-inline" method="post" action="{% url 'blog:subscribe' %}">
      {% csrf_token %}
      <input type="email" name="email" class="subscribe-input" placeholder="your@email.com" required />
      <button type="submit" class="btn">подписаться_</button>
    </form>
  </div>
  {% endblock %}

  <footer>
    <p>&#9608;&#9617; {% now "Y" %} KSR_BLOG &#9617;&#9608; &nbsp;·&nbsp; <a href="{% url 'blog:post_list' %}">все статьи</a></p>
  </footer>
</body>
</html>
```

- [ ] **Step 2: Запустить тесты**

```bash
pytest
```

Ожидаемый результат: все тесты проходят.

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "style: terminal-style navigation and footer for Matrix theme"
```

---

## Task 4: home.html — Hero with Digital Rain Canvas

**Files:**
- Modify: `templates/blog/home.html`

- [ ] **Step 1: Заменить home.html**

Открыть `templates/blog/home.html` и заменить содержимое на:

```html
{% extends "base.html" %}
{% load blog_extras %}
{% block title %}KSR_BLOG — Главная{% endblock %}
{% block content %}

{% if latest_post %}
<div class="hero-wrap" id="hero-wrap">
  <canvas class="hero-canvas" id="hero-canvas"></canvas>
  <div class="hero-content">
    <div class="hero-label">▓▒░ LATEST_TRANSMISSION ░▒▓</div>
    {% if latest_post.cover %}{% cover_url latest_post.cover as hero_img %}
    <a href="{{ latest_post.get_absolute_url }}">
      <img src="{{ hero_img }}" alt="{{ latest_post.title }}" class="cover-image" style="max-height:280px;margin-bottom:1.25rem" />
    </a>
    {% endif %}
    <h1 class="hero-title">
      <a href="{{ latest_post.get_absolute_url }}" style="color:inherit;text-decoration:none">{{ latest_post.title }}</a>
    </h1>
    <div class="hero-meta">{{ latest_post.published_at|date:"Y-m-d" }} &nbsp;·&nbsp; {{ latest_post.reading_time }} min read</div>
    {% if latest_post.excerpt %}<p class="hero-excerpt">{{ latest_post.excerpt }}</p>{% endif %}
    <a href="{{ latest_post.get_absolute_url }}" class="hero-read-link">читать →_</a>
  </div>
</div>
{% endif %}

<div class="container">
  {% if posts %}
  <div class="archive-label">░ ARCHIVE ░</div>
  <div class="post-grid">
    {% for post in posts %}
      {% include "components/post_card.html" %}
    {% endfor %}
  </div>
  {% else %}
  <p style="font-family:var(--font-mono);color:var(--text-muted)">&gt; Статей пока нет._</p>
  {% endif %}
</div>

{% endblock %}
```

- [ ] **Step 2: Запустить тесты**

```bash
pytest tests/test_views.py -v
```

Ожидаемый результат: все view-тесты проходят.

- [ ] **Step 3: Запустить сервер и проверить визуально**

```bash
python manage.py runserver
```

Открыть `http://127.0.0.1:8000` — должен быть виден зелёный цифровой дождь в hero.

- [ ] **Step 4: Commit**

```bash
git add templates/blog/home.html
git commit -m "style: Matrix hero block with digital rain canvas on home page"
```

---

## Task 5: post_card.html — Terminal Card Style

**Files:**
- Modify: `templates/components/post_card.html`

- [ ] **Step 1: Заменить post_card.html**

Открыть `templates/components/post_card.html` и заменить содержимое на:

```html
{% load blog_extras %}
<article class="post-card">
  {% if post.cover %}{% cover_url post.cover as img_url %}
  <a href="{{ post.get_absolute_url }}"><img src="{{ img_url }}" alt="{{ post.title }}" class="post-card-cover" /></a>
  {% endif %}
  {% if post.tags.all %}
  <div class="post-card-tag">{% for tag in post.tags.all %}[ {{ tag.name }} ]{% if not forloop.last %} {% endif %}{% endfor %}</div>
  {% endif %}
  <h2><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h2>
  {% if post.excerpt %}<p class="post-excerpt">{{ post.excerpt }}</p>{% endif %}
  <div class="post-meta">
    <span>{{ post.published_at|date:"Y-m-d" }}</span>
    <span>{{ post.reading_time|reading_time_label }}</span>
  </div>
</article>
```

- [ ] **Step 2: Запустить тесты**

```bash
pytest
```

Ожидаемый результат: все тесты проходят.

- [ ] **Step 3: Commit**

```bash
git add templates/components/post_card.html
git commit -m "style: terminal-style post cards for Matrix theme"
```

---

## Task 6: post_list.html — Archive Page

**Files:**
- Modify: `templates/blog/post_list.html`

- [ ] **Step 1: Заменить post_list.html**

Открыть `templates/blog/post_list.html` и заменить содержимое на:

```html
{% extends "base.html" %}
{% block title %}Все статьи — KSR_BLOG{% endblock %}
{% block content %}
<div class="container">
  <div class="page-heading">░ ARCHIVE ░</div>

  {% if tags %}
  <div class="tag-filter" id="tag-filter">
    {% for tag in tags %}
      <span class="tag-filter-item {% if tag.slug in selected_slugs %}active{% endif %}"
            data-slug="{{ tag.slug }}">
        {{ tag.name }}{% if tag.slug in selected_slugs %} ×{% endif %}
      </span>
    {% endfor %}
  </div>
  {% endif %}

  <div class="post-grid">
    {% for post in page_obj %}
      {% include "components/post_card.html" %}
    {% empty %}
      <p style="font-family:var(--font-mono);color:var(--text-muted)">&gt; Нет статей по этому тегу._</p>
    {% endfor %}
  </div>

  {% if page_obj.has_other_pages %}
  <div class="pagination">
    {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}{% for slug in selected_slugs %}&tag={{ slug }}{% endfor %}">&larr;</a>
    {% endif %}
    <span class="current">{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
    {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}{% for slug in selected_slugs %}&tag={{ slug }}{% endfor %}">&rarr;</a>
    {% endif %}
  </div>
  {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 2: Запустить тесты**

```bash
pytest tests/test_views.py -v
```

Ожидаемый результат: все тесты проходят.

- [ ] **Step 3: Commit**

```bash
git add templates/blog/post_list.html
git commit -m "style: Matrix archive page with terminal tag filter"
```

---

## Task 7: post_detail.html — Article Page with ASCII Frame

**Files:**
- Modify: `templates/blog/post_detail.html`

- [ ] **Step 1: Заменить post_detail.html**

Открыть `templates/blog/post_detail.html` и заменить содержимое на:

```html
{% extends "base.html" %}
{% load blog_extras %}
{% block title %}{{ post.title }} — KSR_BLOG{% endblock %}
{% block content %}
<div class="container">
  <div class="article-layout">
    <div>
      <div class="post-breadcrumb">&gt; / posts / {{ post.slug }} /</div>

      {% if post.cover %}{% cover_url post.cover as img_url %}
      <img src="{{ img_url }}" alt="{{ post.title }}" class="cover-image" />
      {% endif %}

      <div class="post-title-wrap">
        <div class="post-title-border">╔═ POST {% for i in "═══════════════════════════════" %}═{% endfor %}╗</div>
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-title-border">╚{% for i in "═══════════════════════════════════" %}═{% endfor %}╝</div>
      </div>

      <div class="post-meta" style="margin-bottom:1rem">
        <span>{{ post.published_at|date:"Y-m-d" }}</span>
        <span>{{ post.reading_time|reading_time_label }}</span>
        {% for tag in post.tags.all %}
          <a href="{% url 'blog:post_list' %}?tag={{ tag.slug }}" class="tag-badge">{{ tag.name }}</a>
        {% endfor %}
      </div>

      {# content_html is rendered server-side from author-controlled Markdown — no user HTML passthrough #}
      <article class="article-content">{{ post.content_html|safe }}</article>

      {% if post.comments_enabled %}
      <section class="comments-section">
        <h2>░ КОММЕНТАРИИ ░</h2>
        {% for comment in comments %}
          <div class="comment">
            <div class="comment-meta">&gt; {{ comment.author_name }} · {{ comment.created_at|date:"Y-m-d" }}</div>
            <p>{{ comment.body }}</p>
          </div>
        {% empty %}
          <p style="font-family:var(--font-mono);color:var(--text-muted)">&gt; Комментариев пока нет._</p>
        {% endfor %}

        <h3 style="font-family:var(--font-mono);color:var(--accent);font-size:0.9rem;letter-spacing:2px;margin-top:2rem;margin-bottom:1rem">░ ОСТАВИТЬ КОММЕНТАРИЙ ░</h3>
        <form method="post">
          {% csrf_token %}
          {% for field in comment_form %}
          <div class="form-group">
            <label>{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}<p style="color:#ff4444;font-family:var(--font-mono);font-size:0.8rem">&gt; {{ field.errors.0 }}</p>{% endif %}
          </div>
          {% endfor %}
          <button type="submit" class="btn">отправить_</button>
        </form>
      </section>
      {% endif %}
    </div>

    <aside class="sidebar">
      {% if post.tags.all %}
      <div class="sidebar-section">
        <h3>░ ТЕГИ ░</h3>
        {% for tag in post.tags.all %}
          <a href="{% url 'blog:post_list' %}?tag={{ tag.slug }}" class="tag-badge" style="margin-right:0.3rem;margin-bottom:0.5rem;display:inline-block">{{ tag.name }}</a>
        {% endfor %}
      </div>
      {% endif %}

      {% if related_posts %}
      <div class="sidebar-section">
        <h3>░ ПОХОЖИЕ ░</h3>
        {% for rp in related_posts %}
          <div class="sidebar-related-item">
            <a href="{{ rp.get_absolute_url }}">{{ rp.title }}</a>
            <div class="sidebar-related-date">{{ rp.published_at|date:"Y-m-d" }}</div>
          </div>
        {% endfor %}
      </div>
      {% endif %}
    </aside>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Запустить все тесты**

```bash
pytest
```

Ожидаемый результат: все тесты проходят.

- [ ] **Step 3: Запустить сервер и проверить визуально**

```bash
python manage.py runserver
```

Проверить:
- Главная страница: цифровой дождь в hero, карточки статей
- `/posts/` — фильтр тегов, сетка карточек
- Страница статьи — ASCII-рамка заголовка, читабельный текст, блоки кода
- Переключатель темы — светлая тема работает как запасная

- [ ] **Step 4: Commit**

```bash
git add templates/blog/post_detail.html
git commit -m "style: Matrix article page with ASCII title frame and terminal UI"
```

---

## Task 8: Final QA & Push

- [ ] **Step 1: Запустить полный тест-сьют с покрытием**

```bash
pytest --cov=blog --cov-report=term-missing
```

Ожидаемый результат: все тесты проходят, покрытие 100%.

- [ ] **Step 2: Проверить светлую тему**

Открыть `http://127.0.0.1:8000`, нажать кнопку `◑` — сайт должен переключиться в светлую тему. Повторное нажатие — обратно в Matrix.

- [ ] **Step 3: Push**

```bash
git push
```
