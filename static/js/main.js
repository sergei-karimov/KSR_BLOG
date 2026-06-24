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

// Tag filter multi-select
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
