// Public home: the artist's published work as an "exhibition in motion".
// Rows of artworks drift slowly past in a dark, mostly empty room; the
// ones far from the centre soften, fade and shrink a little, like objects
// at different depths. Drag, swipe or scroll to move things along, or just
// stay and look. Without JavaScript the plain grid underneath is shown.
(function () {
  var root = document.querySelector('[data-exhibition]');
  var dataEl = document.getElementById('exhibition-data');

  if (!root || !dataEl) {
    return;
  }

  var works;

  try {
    works = JSON.parse(dataEl.textContent);
  } catch (err) {
    return;
  }

  if (!works.length) {
    return;
  }

  var doc = document.documentElement;
  var stage = root.querySelector('.ex-stage');
  var pauseButton = root.querySelector('[data-exhibition-pause]');
  var fullscreenButton = root.querySelector('[data-exhibition-fullscreen]');
  var progress = root.querySelector('.ex-progress-fill');
  var reducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Vertical position (share of the viewport height), relative size and
  // drift speed (px per second) of each row. Rows share a direction but
  // not a speed, so they slide against each other.
  var ROWS = [
    { y: 0.23, size: 1, speed: 20 },
    { y: 0.53, size: 0.85, speed: 15 },
    { y: 0.8, size: 1.05, speed: 24 }
  ];
  var ROWS_COMPACT = [
    { y: 0.3, size: 1, speed: 20 },
    { y: 0.7, size: 0.9, speed: 24 }
  ];

  // Depth-of-field: how far from the centre (share of the width) the
  // effect reaches, and how strong it gets at the edges.
  var REACH = 0.55;
  var BLUR = 1.9;
  var FADE = 0.55;
  var SCALE = 0.12;
  var EASE = 0.08;

  var rows = [];
  var running = false;
  var paused = false;
  var last = 0;
  var viewW = 0;
  var viewH = 0;
  var mouseX = 0;
  var mouseTarget = 0;
  var dragging = false;
  var dragX = 0;
  var dragDistance = 0;
  var suppressClick = false;

  function remember(view) {
    try {
      sessionStorage.setItem('raigonos-home-view', view);
    } catch (err) {
      // Private mode etc.: the choice just isn't remembered.
    }
  }

  function remembered() {
    try {
      return sessionStorage.getItem('raigonos-home-view');
    } catch (err) {
      return null;
    }
  }

  function shuffle(list) {
    for (var i = list.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var swap = list[i];
      list[i] = list[j];
      list[j] = swap;
    }

    return list;
  }

  // On Cloudinary, ask for a screen-sized copy instead of the original.
  function thumb(src) {
    return src.replace('/image/upload/', '/image/upload/w_700,q_auto,f_auto/');
  }

  function build() {
    stage.innerHTML = '';
    rows = [];
    viewW = root.clientWidth;
    viewH = root.clientHeight;

    var layout = viewH < 560 ? ROWS_COMPACT : ROWS;
    var slot = Math.max(viewW * 0.38, 260);
    var baseHeight = Math.min(Math.max(viewH * 0.165, 96), 190);

    layout.forEach(function (config, rowIndex) {
      var pool = shuffle(works.slice());

      // With plenty of work, each row shows its own share, so the same
      // piece is not on screen twice. With little, every row shows all.
      if (works.length >= layout.length * 4) {
        pool = pool.filter(function (work, i) {
          return i % layout.length === rowIndex;
        });
      }

      // Repeat the row's sequence until one lap is wider than the screen.
      var repeats = Math.max(1, Math.ceil((viewW * 1.5) / (pool.length * slot)));
      var count = pool.length * repeats;
      var period = count * slot;
      var heights = [];
      var el = document.createElement('div');
      var cards = [];

      for (var n = 0; n < count; n++) {
        heights.push(Math.round(baseHeight * config.size * (0.85 + Math.random() * 0.3)));
      }

      el.className = 'ex-row';
      el.style.top = (config.y * 100) + '%';
      // Three identical laps, starting one lap to the left, so there is
      // always artwork on both sides of the visible window.
      el.style.left = (-period) + 'px';

      for (var copy = 0; copy < 3; copy++) {
        for (var i = 0; i < count; i++) {
          var work = pool[i % pool.length];
          var link = document.createElement('a');
          var img = new Image();

          link.className = 'ex-card';
          link.href = work.url;
          link.style.width = slot + 'px';

          img.src = thumb(work.src);
          img.alt = work.title;
          img.draggable = false;
          img.decoding = 'async';
          img.style.height = heights[i] + 'px';
          img.style.maxWidth = Math.round(slot * 0.7) + 'px';

          link.appendChild(img);
          el.appendChild(link);
          cards.push({ el: link, index: copy * count + i });
        }
      }

      stage.appendChild(el);

      var start = -Math.random() * period;

      rows.push({
        el: el,
        cards: cards,
        slot: slot,
        period: period,
        speed: config.speed,
        depth: 1 - rowIndex * 0.12,
        offset: start,
        target: start
      });
    });
  }

  function frame(now) {
    if (!running) {
      return;
    }

    var dt = Math.min(now - last, 64) / 1000;
    var ease = 1 - Math.pow(1 - EASE, dt * 60);
    var center = viewW / 2;
    var reach = viewW * REACH;

    last = now;
    mouseX += (mouseTarget - mouseX) * ease;

    rows.forEach(function (row, rowIndex) {
      if (!paused && !reducedMotion && !dragging) {
        row.target -= row.speed * dt;
      }

      // Keep one lap's worth of travel; the laps are identical, so the
      // jump is invisible.
      while (row.target <= -row.period) {
        row.target += row.period;
        row.offset += row.period;
      }

      while (row.target > 0) {
        row.target -= row.period;
        row.offset -= row.period;
      }

      row.offset += (row.target - row.offset) * ease;

      var shift = row.offset - mouseX * 18 * (rowIndex + 1);

      row.el.style.transform = 'translate3d(' + shift.toFixed(2) + 'px,0,0) translateY(-50%)';

      row.cards.forEach(function (card) {
        var x = card.index * row.slot + row.slot / 2 - row.period + shift;

        if (x < -row.slot || x > viewW + row.slot) {
          return;
        }

        var t = Math.min(1, Math.abs(x - center) / reach);

        card.el.style.opacity = (1 - t * FADE).toFixed(2);
        card.el.style.filter = 'blur(' + (t * BLUR).toFixed(1) + 'px)';
        card.el.style.transform = 'scale(' + (1 + (1 - t) * SCALE).toFixed(3) + ')';
        card.el.style.zIndex = Math.round((1 - t) * 10);
      });
    });

    if (progress && rows.length) {
      var lap = rows[0];
      var position = ((-lap.offset % lap.period) + lap.period) % lap.period;

      progress.style.width = ((position / lap.period) * 100).toFixed(1) + '%';
    }

    requestAnimationFrame(frame);
  }

  function start() {
    if (running) {
      return;
    }

    build();
    running = true;
    last = performance.now();
    requestAnimationFrame(frame);
  }

  function stop() {
    running = false;
  }

  function show() {
    doc.classList.add('is-exhibition');
    remember('exhibition');
    start();
  }

  function hide() {
    doc.classList.remove('is-exhibition');
    remember('grid');
    stop();

    if (document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen();
    }
  }

  document.querySelectorAll('[data-exhibition-open]').forEach(function (button) {
    button.hidden = false;
    button.addEventListener('click', show);
  });

  root.querySelectorAll('[data-exhibition-close]').forEach(function (button) {
    button.addEventListener('click', hide);
  });

  // Pointer: drag to move the rows, hover to tilt them very slightly.
  root.addEventListener('pointerdown', function (event) {
    if (event.target.closest('[data-exhibition-ui]') || event.button > 0) {
      return;
    }

    dragging = true;
    dragX = event.clientX;
    dragDistance = 0;
  });

  window.addEventListener('pointermove', function (event) {
    if (viewW) {
      mouseTarget = event.clientX / viewW - 0.5;
    }

    if (!dragging) {
      return;
    }

    var dx = event.clientX - dragX;

    dragX = event.clientX;
    dragDistance += Math.abs(dx);
    rows.forEach(function (row) {
      row.target += dx * row.depth;
    });
  });

  window.addEventListener('pointerup', function () {
    if (dragging && dragDistance > 6) {
      // A drag is not a click on whichever artwork the pointer ended on.
      suppressClick = true;
      setTimeout(function () {
        suppressClick = false;
      }, 50);
    }

    dragging = false;
  });

  root.addEventListener('click', function (event) {
    if (suppressClick) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);

  root.addEventListener('wheel', function (event) {
    var delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;

    event.preventDefault();
    rows.forEach(function (row) {
      row.target -= delta * 0.5 * row.depth;
    });
  }, { passive: false });

  if (pauseButton) {
    pauseButton.addEventListener('click', function () {
      paused = !paused;
      pauseButton.classList.toggle('is-paused', paused);
      pauseButton.setAttribute('aria-label', paused ? 'Resume drift' : 'Pause drift');
    });
  }

  if (fullscreenButton) {
    if (!root.requestFullscreen) {
      fullscreenButton.hidden = true;
    } else {
      fullscreenButton.addEventListener('click', function () {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          root.requestFullscreen();
        }
      });
    }
  }

  // Slots are sized from the viewport, so lay the rows out again when it
  // changes (ignoring the small height jitter of mobile address bars).
  var resizeTimer;

  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (!running) {
        return;
      }

      if (Math.abs(root.clientWidth - viewW) > 1 || Math.abs(root.clientHeight - viewH) > 80) {
        build();
      }
    }, 250);
  });

  if (remembered() !== 'grid') {
    show();
  }
})();
