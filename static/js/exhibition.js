// Public home: the artist's published work as an "exhibition in motion".
// Rows of artworks drift slowly past in a dark, mostly empty room; the
// ones far from the centre soften, fade and shrink a little, like objects
// at different depths. Drag, swipe or scroll to move things along, or just
// stay and look. A small tools pill switches the drift on and off, flips
// the theme, and turns the rows into columns that fall top to bottom.
// Without JavaScript the plain grid underneath is shown.
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
  var themeButton = root.querySelector('[data-exhibition-theme]');
  var directionButton = root.querySelector('[data-exhibition-direction]');
  var fullscreenButton = root.querySelector('[data-exhibition-fullscreen]');
  var reducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Position of each lane across the screen (share of the viewport height
  // for rows, of the width for columns), relative size and drift speed
  // (px per second). Lanes share a direction but not a speed, so they
  // slide against each other.
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
  var vertical = false;
  var mouseX = 0;
  var mouseY = 0;
  var mouseTargetX = 0;
  var mouseTargetY = 0;
  var dragging = false;
  var dragX = 0;
  var dragY = 0;
  var dragDistance = 0;
  var suppressClick = false;

  // Small per-viewer conveniences; the page works the same without them.
  function remember(store, key, value) {
    try {
      window[store].setItem('raigonos-home-' + key, value);
    } catch (err) {
      // Private mode etc.: the choice just isn't remembered.
    }
  }

  function remembered(store, key) {
    try {
      return window[store].getItem('raigonos-home-' + key);
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

    var layout;

    if (vertical) {
      layout = viewW < 520 ? ROWS_COMPACT : ROWS;
    } else {
      layout = viewH < 560 ? ROWS_COMPACT : ROWS;
    }

    var span = vertical ? viewH : viewW;
    var lane = vertical ? viewW * (layout.length > 2 ? 0.28 : 0.4) : 0;
    var slot = Math.max(span * (vertical ? 0.4 : 0.38), 260);
    var baseHeight = Math.min(Math.max(viewH * 0.165, 96), 190);

    layout.forEach(function (config, rowIndex) {
      var pool = shuffle(works.slice());

      // With plenty of work, each lane shows its own share, so the same
      // piece is not on screen twice. With little, every lane shows all.
      if (works.length >= layout.length * 4) {
        pool = pool.filter(function (work, i) {
          return i % layout.length === rowIndex;
        });
      }

      // Repeat the lane's sequence until one lap is longer than the screen.
      var repeats = Math.max(1, Math.ceil((span * 1.5) / (pool.length * slot)));
      var count = pool.length * repeats;
      var period = count * slot;
      var heights = [];
      var el = document.createElement('div');
      var cards = [];

      for (var n = 0; n < count; n++) {
        heights.push(Math.round(baseHeight * config.size * (0.85 + Math.random() * 0.3)));
      }

      el.className = 'ex-row' + (vertical ? ' is-vertical' : '');

      // Three identical laps, starting one lap back, so there is always
      // artwork on both sides of the visible window.
      if (vertical) {
        el.style.left = (config.y * 100) + '%';
        el.style.top = (-period) + 'px';
        el.style.width = lane + 'px';
      } else {
        el.style.top = (config.y * 100) + '%';
        el.style.left = (-period) + 'px';
      }

      for (var copy = 0; copy < 3; copy++) {
        for (var i = 0; i < count; i++) {
          var work = pool[i % pool.length];
          var link = document.createElement('a');
          var img = new Image();

          link.className = 'ex-card';
          link.href = work.url;

          if (vertical) {
            link.style.width = lane + 'px';
            link.style.height = slot + 'px';
          } else {
            link.style.width = slot + 'px';
          }

          img.src = thumb(work.src);
          img.alt = work.title;
          img.draggable = false;
          img.decoding = 'async';
          img.style.height = heights[i] + 'px';
          img.style.maxWidth = Math.round((vertical ? lane : slot) * 0.7) + 'px';

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
    var span = vertical ? viewH : viewW;
    var center = span / 2;
    var reach = span * REACH;

    last = now;
    mouseX += (mouseTargetX - mouseX) * ease;
    mouseY += (mouseTargetY - mouseY) * ease;

    rows.forEach(function (row, rowIndex) {
      if (!paused && !reducedMotion && !dragging) {
        // Sideways drift goes left; the vertical one falls downwards.
        row.target += (vertical ? 1 : -1) * row.speed * dt;
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

      var tilt = (vertical ? mouseY : mouseX) * 18 * (rowIndex + 1);
      var shift = row.offset - tilt;

      row.el.style.transform = vertical ?
        'translate3d(0,' + shift.toFixed(2) + 'px,0) translateX(-50%)' :
        'translate3d(' + shift.toFixed(2) + 'px,0,0) translateY(-50%)';

      row.cards.forEach(function (card) {
        var x = card.index * row.slot + row.slot / 2 - row.period + shift;

        if (x < -row.slot || x > span + row.slot) {
          return;
        }

        var t = Math.min(1, Math.abs(x - center) / reach);

        card.el.style.opacity = (1 - t * FADE).toFixed(2);
        card.el.style.filter = 'blur(' + (t * BLUR).toFixed(1) + 'px)';
        card.el.style.transform = 'scale(' + (1 + (1 - t) * SCALE).toFixed(3) + ')';
        card.el.style.zIndex = Math.round((1 - t) * 10);
      });
    });

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
    remember('sessionStorage', 'view', 'exhibition');
    start();
  }

  function hide() {
    doc.classList.remove('is-exhibition');
    remember('sessionStorage', 'view', 'grid');
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
    dragY = event.clientY;
    dragDistance = 0;
  });

  window.addEventListener('pointermove', function (event) {
    if (viewW && viewH) {
      mouseTargetX = event.clientX / viewW - 0.5;
      mouseTargetY = event.clientY / viewH - 0.5;
    }

    if (!dragging) {
      return;
    }

    var moved = vertical ? event.clientY - dragY : event.clientX - dragX;

    dragX = event.clientX;
    dragY = event.clientY;
    dragDistance += Math.abs(moved);
    rows.forEach(function (row) {
      row.target += moved * row.depth;
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

  function setTheme(theme) {
    if (theme === 'light') {
      doc.setAttribute('data-home-theme', 'light');
    } else {
      doc.removeAttribute('data-home-theme');
    }

    if (themeButton) {
      themeButton.setAttribute(
        'aria-label',
        theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'
      );
    }
  }

  function setDirection(isVertical) {
    vertical = isVertical;

    if (directionButton) {
      directionButton.classList.toggle('is-vertical', vertical);
      directionButton.setAttribute(
        'aria-label',
        vertical ? 'Drift sideways' : 'Drift top to bottom'
      );
    }
  }

  if (themeButton) {
    themeButton.addEventListener('click', function () {
      var next = doc.getAttribute('data-home-theme') === 'light' ? 'dark' : 'light';

      setTheme(next);
      remember('localStorage', 'theme', next);
    });
  }

  if (directionButton) {
    directionButton.addEventListener('click', function () {
      setDirection(!vertical);
      remember('localStorage', 'direction', vertical ? 'vertical' : 'horizontal');

      if (running) {
        build();
      }
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

  setTheme(remembered('localStorage', 'theme'));
  setDirection(remembered('localStorage', 'direction') === 'vertical');

  if (remembered('sessionStorage', 'view') !== 'grid') {
    show();
  }
})();
