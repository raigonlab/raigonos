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

// Select mode (bulk management): the "Select" button turns the list into
// selectable cards and reveals the bulk-action bar. Clicking a card
// toggles it instead of opening it; Escape or Cancel leaves the mode.
// Deleting still goes through a server-rendered confirmation page.
(function () {
  var toggle = document.querySelector('[data-dash-select-toggle]');
  if (!toggle) {
    return;
  }

  var target = document.querySelector('[data-dash-view-target]');
  var bar = document.querySelector('[data-dash-bulk-bar]');
  if (!target || !bar) {
    toggle.hidden = true;
    return;
  }

  var boxes = Array.prototype.slice.call(target.querySelectorAll('.dash-select-box'));
  var countEl = bar.querySelector('[data-dash-bulk-count]');
  var actionButtons = bar.querySelectorAll('[data-dash-bulk-action]');

  function selecting() {
    return target.classList.contains('is-selecting');
  }

  function sync() {
    var count = 0;
    boxes.forEach(function (box) {
      if (box.checked) {
        count += 1;
      }
      box.closest('li').classList.toggle('is-selected', box.checked);
    });
    countEl.textContent = count;
    actionButtons.forEach(function (btn) {
      btn.disabled = count === 0;
    });
  }

  function setSelecting(on) {
    target.classList.toggle('is-selecting', on);
    bar.hidden = !on;
    toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    toggle.classList.toggle('is-active', on);
    if (!on) {
      boxes.forEach(function (box) {
        box.checked = false;
      });
    }
    sync();
  }

  toggle.addEventListener('click', function () {
    setSelecting(!selecting());
  });

  bar.querySelector('[data-dash-select-cancel]').addEventListener('click', function () {
    setSelecting(false);
  });

  bar.querySelector('[data-dash-select-all]').addEventListener('click', function () {
    var all = boxes.every(function (box) {
      return box.checked;
    });
    boxes.forEach(function (box) {
      box.checked = !all;
    });
    sync();
  });

  target.addEventListener('click', function (event) {
    if (!selecting()) {
      return;
    }
    var item = event.target.closest('li');
    var box = item && item.querySelector(':scope > .dash-select-box');
    if (!box || event.target === box) {
      return;
    }
    event.preventDefault();
    box.checked = !box.checked;
    sync();
  });

  target.addEventListener('change', sync);

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && selecting()) {
      setSelecting(false);
    }
  });

  sync();
})();

// Overflow menus (<details data-dash-menu>): close on outside click or
// Escape, like a native menu.
(function () {
  var menus = document.querySelectorAll('[data-dash-menu]');

  if (!menus.length) {
    return;
  }

  function closeAll(except) {
    menus.forEach(function (menu) {
      if (menu !== except) {
        menu.removeAttribute('open');
      }
    });
  }

  document.addEventListener('click', function (event) {
    closeAll(event.target.closest('[data-dash-menu]'));
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeAll(null);
    }
  });
})();

// Artwork preview page: Escape follows the same link as the Collection
// breadcrumb (marked data-dash-escape-close), so keyboard users can
// leave without hunting for it -- even though this is a real page, not
// a modal.
(function () {
  var closeLink = document.querySelector('[data-dash-escape-close]');

  if (!closeLink) {
    return;
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      window.location.href = closeLink.href;
    }
  });
})();
