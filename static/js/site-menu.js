// Top-right site menu: tools, views, theme and account links. Owns the
// light/dark theme (applied pre-paint by the inline script in base.html).
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

  // Closes on choice, except repeat-flip switches (data-keep-open).
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
