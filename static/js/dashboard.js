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
