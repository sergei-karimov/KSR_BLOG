# Matrix Theme Design Spec

**Date:** 2026-06-24  
**Status:** Approved

---

## Summary

Визуальный редизайн блога KSR_BLOG в стиле фильма «Матрица». Цель — создать уникальную хакерско-терминальную атмосферу, не жертвуя читабельностью статей.

---

## Design Decisions

| Вопрос | Решение |
|--------|---------|
| Интенсивность стиля | Hacker Terminal — ASCII-декор, терминальные символы, моноширинный шрифт в UI |
| Текст статей | Читабельный (светло-зелёный `#c8ffc8` / system-ui), Matrix-эстетика только в UI вокруг |
| Анимация в hero | Цифровой дождь (оптимизированный, ~15 FPS, только на главной) |
| Тема | Matrix-тёмная по умолчанию; светлая тема сохраняется как запасная |

---

## Color Palette

```
--bg:           #050a05   /* основной фон */
--bg-nav:       #030803   /* фон навигации */
--bg-card:      #0a1a0a   /* фон карточек и блоков */
--bg-code:      #000000   /* фон блоков кода */
--accent:       #00ff41   /* основной Matrix-зелёный */
--accent-glow:  #39ff14   /* яркий зелёный для заголовков + glow */
--text:         #c8ffc8   /* основной читабельный текст статей */
--text-muted:   #00ff4180 /* второстепенный текст, мета-данные */
--text-dim:     #00ff4140 /* декоративные элементы, разделители */
--border:       #00ff4125 /* границы блоков */
--border-hover: #00ff4160 /* границы при hover */
--code-accent:  #39ff14   /* выделения внутри кода */
```

---

## Typography

- **UI элементы** (навигация, мета, теги, декор): `'Courier New', monospace`
- **Основной текст статей**: `system-ui, sans-serif` — для читабельности
- **Блоки кода**: `'Courier New', monospace` с зелёной подсветкой
- **Заголовки**: `'Courier New', monospace` + `text-shadow: 0 0 8px var(--accent-glow)`

---

## Components

### Navigation Bar
- Фон `--bg-nav`, нижняя граница `1px solid --border`
- Логотип: `KSR_BLOG` с `letter-spacing: 4px` и green glow
- Ссылки в стиле `[posts]` `[search]`
- Кнопки подписки и темы: `border: 1px solid --border`, квадратные

### Hero Block (главная страница)
- Анимированный цифровой дождь (`<canvas>`) на фоне, `opacity: 0.2`
- Canvas: размер берётся из `container.offsetWidth/Height` во избежание растяжения символов
- Рендер через `requestAnimationFrame` с throttle 66ms (~15 FPS)
- Пауза через `IntersectionObserver` когда блок вне viewport
- Заголовок статьи с `text-shadow` glow
- ASCII-метка `▓▒░ LATEST_TRANSMISSION ░▒▓`

### Post Cards (сетка архива)
- Фон `--bg-card`, граница `1px solid --border`
- Тег мелким шрифтом сверху `[ tag ]`
- Заголовок `--text` (читабельный), дата `--text-muted`
- Hover: граница `--border-hover`

### Post Detail Page
- Breadcrumb: `> / posts / slug /` в `--text-dim`
- ASCII-рамка вокруг заголовка: `╔═ POST ═...╗` / `╚══...╝`
- Cover image с `border: 1px solid --border`
- Мета-блок: дата и время чтения с `>` префиксом
- Теги: `border: 1px solid` квадратные бейджи
- Основной текст: `--text` / `system-ui` / `line-height: 1.9`
- Блоки кода: чёрный фон, `border-left: 3px solid --accent`, заголовок `$ python3`

### Tag Filter (страница /posts/)
- Теги в стиле `[ tag ]` вместо pill-badges
- Активный тег: `color: --accent-glow`, подчёркивание `border-bottom`

### Footer
- Минимальный, `--text-dim`, ASCII-разделитель сверху
- Строка подписки в терминальном стиле

---

## Digital Rain Implementation

```javascript
// canvas берёт реальные пиксельные размеры контейнера
canvas.width = container.offsetWidth;
canvas.height = container.offsetHeight;

// throttle до ~15 FPS
if (timestamp - last < 66) { requestAnimationFrame(draw); return; }

// IntersectionObserver для паузы вне viewport
const observer = new IntersectionObserver(([e]) => {
  running = e.isIntersecting;
});
observer.observe(heroWrap);
```

Символы: смесь катаканы (`アイウエオ...`) и `01ABCDEF`.  
Размер символа: `13px` — совпадает с шагом сетки столбцов.

---

## Light Theme (запасная)

Переключатель остаётся. Светлая тема переопределяет CSS-переменные на стандартные светлые значения. Matrix-тёмная — `[data-theme="dark"]` по умолчанию (или `prefers-color-scheme: dark`).

---

## Files to Change

| Файл | Что меняется |
|------|-------------|
| `static/css/main.css` | Полная замена цветовых переменных и компонентов |
| `static/js/main.js` | Добавить digital rain + IntersectionObserver |
| `templates/base.html` | Навигация в терминальном стиле |
| `templates/blog/home.html` | Hero с canvas дождём, ASCII-метки |
| `templates/blog/post_list.html` | Теги в стиле `[ tag ]` |
| `templates/blog/post_detail.html` | ASCII-рамка заголовка, breadcrumb |
| `templates/components/post_card.html` | Стиль карточек |

---

## Out of Scope

- Изменение моделей, views, management commands — только CSS/JS/шаблоны
- Светлая тема не редизайнится — остаётся как есть
- Шрифты подключаются через системные стеки, без Google Fonts
