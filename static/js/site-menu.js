// Public site menu: the one button, always top-right, that opens tools,
// views, theme and account links. Also owns the light/dark theme, which
// applies to every public gallery page (the saved choice is applied by a
// tiny inline script in base.html before first paint).
(function () {
  var menu = document.querySelector('[data-site-menu]');

  if (!menu) {
    return;
  }

  var toggle = menu.querySelector('[data-site-menu-toggle]');
  var panel = menu.querySelector('.site-menu-panel');
  var themeButton = menu.querySelector('[data-site-theme-toggle]');
  var doc = document.documentElement;

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    menu.classList.toggle('is-open', open);
  }

  toggle.addEventListener('click', function () {
    setOpen(panel.hidden);
  });

  // Choosing something closes the menu, except the switches you flip
  // repeatedly (data-keep-open) while watching the effect.
  panel.addEventListener('click', function (event) {
    if (event.target.closest('a, button') && !event.target.closest('[data-keep-open]')) {
      setOpen(false);
    }
  });

  document.addEventListener('click', function (event) {
    if (!menu.contains(event.target)) {
      setOpen(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !panel.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });

  function syncThemeLabel() {
    var light = doc.getAttribute('data-site-theme') === 'light';

    if (themeButton) {
      themeButton.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
    }
  }

  if (themeButton) {
    themeButton.addEventListener('click', function () {
      var next = doc.getAttribute('data-site-theme') === 'light' ? 'dark' : 'light';

      if (next === 'light') {
        doc.setAttribute('data-site-theme', 'light');
      } else {
        doc.removeAttribute('data-site-theme');
      }

      try {
        localStorage.setItem('raigonos-theme', next);
      } catch (err) {
        // The choice just isn't remembered.
      }

      syncThemeLabel();
    });
  }

  syncThemeLabel();
})();
