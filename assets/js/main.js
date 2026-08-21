/* Lateral Repairs — preloader, nav, scroll animations, 3D hero (Three.js), tilt cards */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ================= Preloader ================= */
  var loader = document.getElementById('loader');
  function hideLoader() {
    if (loader) loader.classList.add('done');
  }
  if (document.readyState === 'complete') hideLoader();
  else window.addEventListener('load', hideLoader);
  // Safety net: never trap the user behind the loader
  setTimeout(hideLoader, 3500);

  /* ================= Sticky nav + scroll progress ================= */
  var nav = document.getElementById('nav');
  var progressBar = document.getElementById('progressBar');
  function onScroll() {
    var y = window.scrollY;
    if (nav) nav.classList.toggle('scrolled', y > 24);
    if (progressBar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progressBar.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ================= Hero logo → nav dock =================
     The brand mark lives in the nav (its final resting place). On load it is
     transformed out into the hero slot; as you scroll it eases back to its
     natural nav position, so it lands pixel-perfect (transform: none). */
  (function () {
    var mark = document.querySelector('.nav__logo .brand__mark');
    var slot = document.getElementById('heroLogoSlot');
    if (!mark || !slot || reduce) return;

    var root = document.documentElement;
    var from = null;

    function measure() {
      var prev = mark.style.transform;
      mark.style.transform = 'none';
      var m = mark.getBoundingClientRect();
      var s = slot.getBoundingClientRect();
      mark.style.transform = prev;
      if (!m.width || !s.width) { from = null; return; }
      // slot position is taken in document space so measuring works at any scroll offset
      var slotTop = s.top + window.scrollY;
      from = {
        scale: s.width / m.width,
        x: (s.left + s.width / 2) - (m.left + m.width / 2),
        y: (slotTop + s.height / 2) - (m.top + m.height / 2)
      };
    }

    function render() {
      ticking = false;
      if (!from) return;
      var travel = Math.max(1, window.innerHeight * 0.5);
      var p = Math.min(Math.max(window.scrollY / travel, 0), 1);
      var k = Math.pow(1 - p, 3); // easeOutCubic remainder: 1 = in hero, 0 = docked
      if (k < 0.002) {
        mark.style.transform = ''; // fully docked — hand hover styling back to CSS
        root.classList.remove('logo-flying');
        return;
      }
      root.classList.add('logo-flying');
      mark.style.transform =
        'translate3d(' + (from.x * k).toFixed(2) + 'px,' + (from.y * k).toFixed(2) + 'px,0)' +
        ' scale(' + (1 + (from.scale - 1) * k).toFixed(4) + ')';
    }

    var ticking = false;
    function onScrollLogo() {
      if (!ticking) { ticking = true; requestAnimationFrame(render); }
    }
    function remeasure() { measure(); render(); }

    measure();
    render();
    window.addEventListener('scroll', onScrollLogo, { passive: true });
    window.addEventListener('resize', remeasure);
    window.addEventListener('load', remeasure);
  })();

  /* ================= Mobile menu ================= */
  var burger = document.getElementById('burger');
  var navLinksWrap = document.getElementById('navLinks');
  if (burger && navLinksWrap) {
    burger.addEventListener('click', function () {
      var open = navLinksWrap.classList.toggle('open');
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
    });
    navLinksWrap.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navLinksWrap.classList.remove('open');
        burger.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ================= Scroll-spy ================= */
  var spyLinks = Array.prototype.slice.call(document.querySelectorAll('.nav__links a[href^="#"]'));
  var spySections = spyLinks
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean);
  if ('IntersectionObserver' in window && spySections.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        spyLinks.forEach(function (a) {
          a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id);
        });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    spySections.forEach(function (s) { spy.observe(s); });
  }

  /* ================= Reveal on scroll ================= */
  var revealEls = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ================= Count-up stats ================= */
  function countUp(el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    var suffix = el.getAttribute('data-suffix') || '';
    var start = null;
    var dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var nums = document.querySelectorAll('.num[data-count]');
  if (!reduce && 'IntersectionObserver' in window) {
    var nio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          countUp(e.target);
          nio.unobserve(e.target);
        }
      });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { nio.observe(el); });
  }

  /* ================= 3D tilt cards ================= */
  var fineInput = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!reduce && fineInput) {
    document.querySelectorAll('.tilt').forEach(function (card) {
      var MAX = 7;
      card.addEventListener('mousemove', function (ev) {
        var r = card.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width;
        var py = (ev.clientY - r.top) / r.height;
        var rx = (0.5 - py) * MAX;
        var ry = (px - 0.5) * MAX;
        card.style.transform =
          'perspective(900px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg) translateY(-4px)';
        // drive the cursor-follow glow on product cards
        card.style.setProperty('--gx', (px * 100).toFixed(1) + '%');
        card.style.setProperty('--gy', (py * 100).toFixed(1) + '%');
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = '';
      });
    });

    /* phone mockup: gentle 3D sway following the cursor over the app card */
    var phone = document.getElementById('phone');
    var appCard = document.querySelector('.app__card');
    if (phone && appCard) {
      appCard.addEventListener('mousemove', function (ev) {
        var r = appCard.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width - 0.5;
        var py = (ev.clientY - r.top) / r.height - 0.5;
        phone.style.transform =
          'perspective(1000px) rotateY(' + (px * 14).toFixed(2) + 'deg) rotateX(' + (-py * 10).toFixed(2) + 'deg)';
      });
      appCard.addEventListener('mouseleave', function () {
        phone.style.transform = '';
      });
    }
  }

  /* ================= Cookie consent =================
     No tracking cookies are used. The only stored entry is the visitor's own
     choice; third-party content (YouTube) loads only after opt-in. */
  var CONSENT_KEY = 'lr-consent-v1';
  function getConsent() {
    try { return JSON.parse(localStorage.getItem(CONSENT_KEY)); } catch (e) { return null; }
  }
  function setConsent(thirdParty) {
    try { localStorage.setItem(CONSENT_KEY, JSON.stringify({ thirdParty: !!thirdParty, ts: Date.now() })); } catch (e) {}
  }
  var banner = document.getElementById('consent');
  function showBanner() { if (banner) banner.hidden = false; }
  function hideBanner() { if (banner) banner.hidden = true; }
  if (banner) {
    if (!getConsent()) showBanner();
    var acceptBtn = document.getElementById('consentAccept');
    var necessaryBtn = document.getElementById('consentNecessary');
    if (acceptBtn) acceptBtn.addEventListener('click', function () { setConsent(true); hideBanner(); });
    if (necessaryBtn) necessaryBtn.addEventListener('click', function () { setConsent(false); hideBanner(); });
  }
  var cookieSettings = document.getElementById('cookieSettings');
  if (cookieSettings) cookieSettings.addEventListener('click', function () {
    showBanner();
    banner.scrollIntoView({ block: 'end', behavior: reduce ? 'auto' : 'smooth' });
  });

  /* ================= Consent-gated YouTube embed ================= */
  document.querySelectorAll('.video-poster[data-yt]').forEach(function (poster) {
    function embed() {
      var id = poster.getAttribute('data-yt');
      var iframe = document.createElement('iframe');
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      iframe.title = 'Lateral Repairs company video';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;
      poster.replaceWith(iframe);
    }
    function play() {
      var c = getConsent();
      if (c && c.thirdParty) { embed(); return; }
      if (poster.querySelector('.video-consent')) return; // prompt already shown
      var ask = document.createElement('div');
      ask.className = 'video-consent';
      ask.innerHTML =
        '<p>Playing the video loads it from <b>YouTube (Google)</b>, which may set cookies and process your IP address. See our <a href="cookies.html">Cookie Policy</a>.</p>';
      var allow = document.createElement('button');
      allow.type = 'button'; allow.className = 'btn btn-primary';
      allow.textContent = 'Allow & play';
      allow.addEventListener('click', function (e) {
        e.stopPropagation();
        setConsent(true); hideBanner(); embed();
      });
      ask.appendChild(allow);
      poster.appendChild(ask);
    }
    poster.addEventListener('click', play);
    poster.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); }
    });
  });

  /* ================= Footer year ================= */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  /* ================= Contact form (prototype) ================= */
  var form = document.querySelector('.form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.textContent = 'Thanks — we’ll be in touch!';
        btn.disabled = true;
      }
    });
  }

  /* ================= 3D hero — particle pipe tunnel (Three.js) =================
     A camera travels through a tunnel of pink particle rings — the inside of a
     freshly relined pipe. Falls back to the CSS gradient backdrop when WebGL or
     the Three.js CDN script is unavailable. */
  function initHero3D() {
    var canvas = document.getElementById('pipe3d');
    if (!canvas || reduce || typeof THREE === 'undefined') return;

    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    } catch (err) {
      return; // no WebGL — CSS backdrop stays
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    var scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070608, 0.05);

    var camera = new THREE.PerspectiveCamera(72, 1, 0.1, 100);
    camera.position.set(0, 0, 0);

    var PINK = new THREE.Color(0xe6007e);
    var PINK_LIGHT = new THREE.Color(0xff4fb0);

    /* particle rings forming the pipe wall */
    var RINGS = 48;
    var PER_RING = 42;
    var RADIUS = 4.2;
    var SPACING = 1.4;
    var DEPTH = RINGS * SPACING;

    var count = RINGS * PER_RING;
    var positions = new Float32Array(count * 3);
    var colors = new Float32Array(count * 3);
    var c = new THREE.Color();
    for (var i = 0; i < RINGS; i++) {
      for (var j = 0; j < PER_RING; j++) {
        var k = (i * PER_RING + j) * 3;
        var a = (j / PER_RING) * Math.PI * 2 + i * 0.12;
        positions[k] = Math.cos(a) * RADIUS;
        positions[k + 1] = Math.sin(a) * RADIUS;
        positions[k + 2] = -i * SPACING;
        c.copy(PINK).lerp(PINK_LIGHT, Math.random() * 0.8);
        colors[k] = c.r; colors[k + 1] = c.g; colors[k + 2] = c.b;
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    var mat = new THREE.PointsMaterial({
      size: 0.085,
      vertexColors: true,
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true
    });
    var points = new THREE.Points(geo, mat);
    scene.add(points);

    /* faint wireframe pipe shell for structure */
    var tubeGeo = new THREE.CylinderGeometry(RADIUS + 0.35, RADIUS + 0.35, DEPTH, 28, RINGS, true);
    var tubeMat = new THREE.MeshBasicMaterial({
      color: 0xe6007e,
      wireframe: true,
      transparent: true,
      opacity: 0.05
    });
    var tube = new THREE.Mesh(tubeGeo, tubeMat);
    tube.rotation.x = Math.PI / 2;
    tube.position.z = -DEPTH / 2;
    scene.add(tube);

    /* floating dust drifting through the pipe */
    var DUST = 260;
    var dustPos = new Float32Array(DUST * 3);
    for (var d = 0; d < DUST; d++) {
      dustPos[d * 3] = (Math.random() - 0.5) * RADIUS * 1.6;
      dustPos[d * 3 + 1] = (Math.random() - 0.5) * RADIUS * 1.6;
      dustPos[d * 3 + 2] = -Math.random() * DEPTH;
    }
    var dustGeo = new THREE.BufferGeometry();
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    var dustMat = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.03,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    var dust = new THREE.Points(dustGeo, dustMat);
    scene.add(dust);

    /* sizing */
    var hero = canvas.parentElement;
    function resize() {
      var w = hero.clientWidth, h = hero.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', resize);
    resize();

    /* mouse parallax */
    var mx = 0, my = 0, tx = 0, ty = 0;
    window.addEventListener('pointermove', function (e) {
      tx = (e.clientX / window.innerWidth - 0.5) * 2;
      ty = (e.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });

    /* render only while the hero is on screen */
    var visible = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
      }).observe(hero);
    }

    var clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      if (!visible || document.hidden) return;
      var t = clock.getElapsedTime();

      mx += (tx - mx) * 0.04;
      my += (ty - my) * 0.04;

      /* drift forward through the tunnel and recycle rings behind the camera */
      var travel = (t * 1.1) % SPACING;
      points.position.z = travel;
      dust.position.z = (t * 0.6) % SPACING;
      tube.position.z = -DEPTH / 2 + travel;

      points.rotation.z = t * 0.05;
      camera.position.x = mx * 0.7;
      camera.position.y = -my * 0.5 + Math.sin(t * 0.4) * 0.15;
      camera.lookAt(mx * 0.4, -my * 0.3, -6);

      renderer.render(scene, camera);
    }
    animate();
  }

  /* Three.js loads with `defer` after this file; wait for the window load. */
  if (typeof THREE !== 'undefined') initHero3D();
  else window.addEventListener('load', initHero3D);
})();
