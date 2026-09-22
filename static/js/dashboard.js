// Dashboard shell: toggles the off-canvas sidebar on small screens.
// Only loaded on dashboard pages (see dashboard_base.html extra_js block).
(function () {
  var shell = document.querySelector('.dash');
  var toggle = document.querySelector('[data-dash-toggle]');
  var closers = document.querySelectorAll('[data-dash-close]');

  if (!shell || !toggle) {
    return;
  }

  function setOpen(open) {
    shell.classList.toggle('dash-sidebar-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  toggle.addEventListener('click', function () {
    setOpen(!shell.classList.contains('dash-sidebar-open'));
  });

  closers.forEach(function (el) {
    el.addEventListener('click', function () {
      setOpen(false);
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      setOpen(false);
    }
  });
})();

// Light/dark theme toggle. Default is light (cream); dark is an opt-in
// preference remembered per browser via localStorage. The matching
// inline script in dashboard_base.html applies a saved "dark" choice
// before first paint so there's no flash of the wrong theme.
(function () {
  var THEME_KEY = 'dash-theme';
  var toggle = document.querySelector('[data-dash-theme-toggle]');

  if (!toggle) {
    return;
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-dash-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-dash-theme');
    }
  }

  var stored = null;
  try {
    stored = localStorage.getItem(THEME_KEY);
  } catch (e) {}

  toggle.checked = stored === 'dark';

  toggle.addEventListener('change', function () {
    var theme = toggle.checked ? 'dark' : 'light';
    applyTheme(theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {}
  });
})();
