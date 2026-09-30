// Exhibition view for the public home: rows of published artworks drift
// across a dark room, softening near the edges. Tools live in the site
// menu (site-menu.js). No JS: falls back to the plain grid.
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
  var pauseButton = document.querySelector('[data-exhibition-pause]');
  var directionButton = document.querySelector('[data-exhibition-direction]');
  var fullscreenButton = document.querySelector('[data-exhibition-fullscreen]');
  var reducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Lane position (share of viewport), relative size, speed (px/s).
  var ROWS = [
    { y: 0.23, size: 1, speed: 20 },
    { y: 0.53, size: 0.85, speed: 15 },
    { y: 0.8, size: 1.05, speed: 24 }
  ];
  var ROWS_COMPACT = [
    { y: 0.3, size: 1, speed: 20 },
    { y: 0.7, size: 0.9, speed: 24 }
  ];

  // Depth-of-field tuning: reach and strength of the blur/fade/scale.
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

  function remember(store, key, value) {
    try {
      window[store].setItem('raigonos-home-' + key, value);
    } catch (err) {
      // Private mode etc. -- not fatal.
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

  // Cloudinary: request a screen-sized copy.
  function thumb(src) {
    return src.replace('/image/upload/', '/image/upload/w_700,q_auto,f_auto/');
  }

  // AI-assisted (Claude Code), directed by Railson Gonçalves: seamless
  // looping needed each lane's lap made wide enough to tile without a
  // gap or a visible jump, which is what the repeats/period math below
  // works out.
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

      // Split artwork across lanes once there's enough of it.
      if (works.length >= layout.length * 4) {
        pool = pool.filter(function (work, i) {
          return i % layout.length === rowIndex;
        });
      }

      // Repeat until one lap is wider than the screen.
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

      // Three laps, starting one back, so both sides stay filled.
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

  // AI-assisted (Claude Code), directed by Railson Gonçalves: the per-frame
  // loop -- frame-rate-independent easing, wrapping each lane after one
  // lap, and the depth-of-field falloff by distance from centre.
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
        // Sideways drifts left; vertical falls.
        row.target += (vertical ? 1 : -1) * row.speed * dt;
      }

      // Wrap after one lap; laps are identical so the jump is invisible.
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

  // Real links (work from any page); here they just switch view in place.
  document.querySelectorAll('[data-exhibition-open]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      show();
    });
  });

  document.querySelectorAll('[data-exhibition-close]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      hide();
    });
  });

  // Drag to move the rows; hover tilts them slightly.
  root.addEventListener('pointerdown', function (event) {
    if (event.button > 0) {
      return;
    }

    dragging = true;
    dragX = event.clientX;
    dragY = event.clientY;
    dragDistance = 0;
  });

  // AI-assisted (Claude Code), directed by Railson Gonçalves: drag delta
  // applies along whichever axis is active (rows vs. columns), scaled per
  // lane by its depth, so a drag moves the nearer lanes further.
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
      // A drag isn't a click on whatever it ends on.
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
    // Full-screens the whole page so the menu stays reachable.
    if (!doc.requestFullscreen) {
      fullscreenButton.hidden = true;
    } else {
      fullscreenButton.addEventListener('click', function () {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          doc.requestFullscreen();
        }
      });
    }
  }

  // Re-layout on real size changes (ignore mobile address-bar jitter).
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

  // Fade the chrome (logo, welcome line, site menu) after a few
  // seconds with no touch/pointer movement, so attention stays on the
  // art; any interaction brings it back immediately. See the matching
  // `html.is-exhibition.is-idle` rules in style.css.
  var IDLE_DELAY = 3000;
  var idleTimer;

  function scheduleIdle() {
    clearTimeout(idleTimer);
    doc.classList.remove('is-idle');
    idleTimer = setTimeout(function () {
      doc.classList.add('is-idle');
    }, IDLE_DELAY);
  }

  // Listens on the whole document, not just the exhibition stage --
  // `.site-menu` is a separate element elsewhere in the DOM (fixed
  // position, rendered on top of it), so a tap on the menu button
  // wouldn't otherwise reset the timer or un-fade the logo/welcome
  // line alongside it.
  ['pointermove', 'pointerdown', 'touchstart', 'touchmove', 'keydown'].forEach(function (evt) {
    document.addEventListener(evt, scheduleIdle, { passive: true });
  });

  scheduleIdle();

  setDirection(remembered('localStorage', 'direction') === 'vertical');

  // #grid / #exhibition in the URL wins over the remembered choice.
  var wanted = location.hash.replace('#', '') || remembered('sessionStorage', 'view');

  if (wanted !== 'grid') {
    show();
  } else {
    hide();
  }
})();
