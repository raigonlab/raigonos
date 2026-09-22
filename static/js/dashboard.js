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

// Grid/List view toggle, shared by the Collections and All Artworks
// pages. Preference remembered per browser via localStorage; the
// matching inline script (_view_init_script.html) applies a saved
// "grid" choice before first paint so there's no layout flash.
(function () {
  var VIEW_KEY = 'dash-view';
  var group = document.querySelector('[data-dash-view-toggle]');
  var target = document.querySelector('[data-dash-view-target]');

  if (!group || !target) {
    return;
  }

  var buttons = group.querySelectorAll('[data-dash-view]');

  function apply(view) {
    target.setAttribute('data-view', view);
    buttons.forEach(function (btn) {
      var active = btn.getAttribute('data-dash-view') === view;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  var stored = null;
  try {
    stored = localStorage.getItem(VIEW_KEY);
  } catch (e) {}

  apply(stored === 'grid' ? 'grid' : 'list');

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var view = btn.getAttribute('data-dash-view');
      apply(view);
      try {
        localStorage.setItem(VIEW_KEY, view);
      } catch (e) {}
    });
  });
})();

// Artwork lightbox: opens a large view of an Artwork's image with
// Prev/Next navigation across every [data-dash-lightbox-trigger] on the
// page (in DOM order), so the owner can flip through their work without
// leaving the dashboard.
(function () {
  var triggers = Array.prototype.slice.call(
    document.querySelectorAll('[data-dash-lightbox-trigger]')
  );
  var lightbox = document.querySelector('[data-dash-lightbox]');

  if (!triggers.length || !lightbox) {
    return;
  }

  var image = lightbox.querySelector('[data-dash-lightbox-image]');
  var caption = lightbox.querySelector('[data-dash-lightbox-caption]');
  var closeBtn = lightbox.querySelector('[data-dash-lightbox-close]');
  var prevBtn = lightbox.querySelector('[data-dash-lightbox-prev]');
  var nextBtn = lightbox.querySelector('[data-dash-lightbox-next]');
  var currentIndex = 0;
  var lastFocused = null;

  function show(index) {
    currentIndex = (index + triggers.length) % triggers.length;
    var trigger = triggers[currentIndex];
    image.src = trigger.getAttribute('data-image');
    var title = trigger.getAttribute('data-title') || '';
    image.alt = title;
    caption.textContent = title;
  }

  function open(index) {
    lastFocused = document.activeElement;
    show(index);
    lightbox.hidden = false;
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }

  function close() {
    lightbox.hidden = true;
    document.body.style.overflow = '';
    image.src = '';
    if (lastFocused) {
      lastFocused.focus();
    }
  }

  triggers.forEach(function (trigger, index) {
    trigger.addEventListener('click', function () {
      open(index);
    });
  });

  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', function () {
    show(currentIndex - 1);
  });
  nextBtn.addEventListener('click', function () {
    show(currentIndex + 1);
  });

  lightbox.addEventListener('click', function (event) {
    if (event.target === lightbox) {
      close();
    }
  });

  document.addEventListener('keydown', function (event) {
    if (lightbox.hidden) {
      return;
    }
    if (event.key === 'Escape') {
      close();
    } else if (event.key === 'ArrowLeft') {
      show(currentIndex - 1);
    } else if (event.key === 'ArrowRight') {
      show(currentIndex + 1);
    }
  });
})();
