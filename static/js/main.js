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
