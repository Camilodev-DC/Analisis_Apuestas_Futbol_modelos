'use strict';

/* ── SPA — Inmersión cinematográfica ───────────────────────────── */

(function initSPA() {
  const SECTION_IDS = ['hero','resumen','shotmap','xg-section','predictor','regresion','eda','comparacion','metodologia'];
  const NAV_LABELS  = ['Inicio','Resumen','Shot Map','xG','Predictor','Regresión','EDA','Comparación','Metodología'];

  const sections = SECTION_IDS.map(id => document.getElementById(id)).filter(Boolean);
  let current = 0;
  let busy    = false;

  const DUR_OUT  = 1.0;
  const DUR_IN   = 1.3;
  const DUR_HERO = 2.0;

  // ── Dots laterales ───────────────────────────────────────────
  const dotsWrap = document.createElement('nav');
  dotsWrap.className = 'spa-dots';
  sections.forEach((_, i) => {
    const d = document.createElement('button');
    d.className = 'spa-dot';
    d.title = NAV_LABELS[i];
    d.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(d);
  });
  document.body.appendChild(dotsWrap);
  const dots = dotsWrap.querySelectorAll('.spa-dot');

  // ── Botón siguiente ──────────────────────────────────────────
  const nextBtn = document.createElement('button');
  nextBtn.className = 'spa-next-btn';
  nextBtn.innerHTML = `<span class="spa-next-label"></span><svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 2v8M2 8l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  document.body.appendChild(nextBtn);
  nextBtn.addEventListener('click', () => goTo(current + 1));

  // ── Nav links ────────────────────────────────────────────────
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const idx = SECTION_IDS.indexOf(a.getAttribute('href').replace('#',''));
      if (idx !== -1) goTo(idx);
    });
  });
  document.querySelector('.nav-brand')?.addEventListener('click', () => goTo(0));

  // ── Teclado ──────────────────────────────────────────────────
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' || e.key === 'PageDown') { e.preventDefault(); goTo(current + 1); }
    if (e.key === 'ArrowUp'   || e.key === 'PageUp')   { e.preventDefault(); goTo(current - 1); }
  });

  // ── Rueda del mouse ──────────────────────────────────────────
  let wheelLocked = false;
  document.addEventListener('wheel', e => {
    const goDown = e.deltaY > 0;
    e.preventDefault();
    if (wheelLocked) return;
    wheelLocked = true;
    goTo(current + (goDown ? 1 : -1));
    const poll = setInterval(() => {
      if (!busy) { wheelLocked = false; clearInterval(poll); }
    }, 100);
  }, { passive: false });

  // ── Touch ────────────────────────────────────────────────────
  let ty = null;
  document.addEventListener('touchstart', e => { ty = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchend', e => {
    if (ty === null) return;
    const dy = ty - e.changedTouches[0].clientY;
    if (Math.abs(dy) > 50) goTo(current + (dy > 0 ? 1 : -1));
    ty = null;
  }, { passive: true });

  // ── Router ───────────────────────────────────────────────────
  function goTo(idx) {
    if (busy) return;
    if (idx < 0 || idx >= sections.length) return;
    if (idx === current) return;
    busy = true;
    if (current === 0) { heroExit(idx);      return; }
    if (idx     === 0) { heroEnter(current); return; }
    immersiveTransition(current, idx);
  }

  // ════════════════════════════════════════════════════════════
  // HERO → siguiente: contenido desaparece, nueva sección crece
  //                   desde el centro como un zoom-in
  // ════════════════════════════════════════════════════════════
  function heroExit(idx) {
    const heroSec     = sections[0];
    const heroContent = heroSec.querySelector('.hero-content');
    const heroOverlay = heroSec.querySelector('.hero-overlay');
    const ins         = sections[idx];

    gsap.set(ins, { opacity: 0, scale: 0.08, transformOrigin: 'center center' });
    prepareCards(ins);
    ins.classList.add('spa-active');

    const CONTENT_FADE = 0.2;  // contenido desaparece rápido
    const VIDEO_SOLO   = 1.7;  // video solo quieto
    const ZOOM_START   = CONTENT_FADE + VIDEO_SOLO;
    const GROW         = 1.4;

    const tl = gsap.timeline({
      onComplete: () => {
        if (heroContent) gsap.set(heroContent, { clearProps: 'all' });
        if (heroOverlay) gsap.set(heroOverlay,  { clearProps: 'all' });
        gsap.set(heroSec, { opacity: 0, scale: 1 });
        heroSec.classList.remove('spa-active');
        busy = false;
        animateChartsIn(ins);
      }
    });

    // Contenido y overlay desaparecen en 0.2s
    if (heroContent) tl.to(heroContent, { opacity: 0, duration: CONTENT_FADE, ease: 'power1.in' }, 0);
    if (heroOverlay) tl.to(heroOverlay, { opacity: 0, duration: CONTENT_FADE, ease: 'power1.in' }, 0);

    // Hero completo fade out justo antes del zoom
    tl.to(heroSec, { opacity: 0, duration: 0.5, ease: 'power1.inOut' }, ZOOM_START - 0.1);

    // Nueva sección crece desde el centro
    tl.to(ins, {
      opacity: 1, scale: 1,
      duration: GROW, ease: 'expo.out', transformOrigin: 'center center',
    }, ZOOM_START);

    addCardsToTimeline(tl, ins, ZOOM_START + GROW * 0.3);

    current = idx;
    updateUI();
  }

  // ════════════════════════════════════════════════════════════
  // Sección → HERO
  // ════════════════════════════════════════════════════════════
  function heroEnter(fromIdx) {
    const heroSec = sections[0];
    const out     = sections[fromIdx];

    gsap.set(heroSec, { opacity: 0, scale: 1, transformOrigin: 'center center' });
    heroSec.classList.add('spa-active');

    const tl = gsap.timeline({
      onComplete: () => {
        out.classList.remove('spa-active');
        gsap.set(out, { opacity: 0, scale: 1 });
        out.scrollTop = 0;
        busy = false;
      }
    });

    // Sección saliente se achica y desvanece
    tl.to(out, {
      opacity: 0, scale: 0.08,
      duration: DUR_OUT, ease: 'expo.in', transformOrigin: 'center center',
    }, 0);

    // Hero aparece con fade simple
    tl.to(heroSec, {
      opacity: 1, duration: DUR_IN * 0.6, ease: 'power1.out',
    }, DUR_OUT * 0.6);

    current = 0;
    updateUI();
  }

  // ════════════════════════════════════════════════════════════
  // Transición normal
  // ════════════════════════════════════════════════════════════
  function immersiveTransition(fromIdx, toIdx) {
    const out = sections[fromIdx];
    const ins = sections[toIdx];

    gsap.set(ins, {
      opacity: 0, z: -700, scale: 0.83, filter: 'blur(20px)',
      transformPerspective: 1400, transformOrigin: 'center center',
    });
    prepareCards(ins);
    ins.classList.add('spa-active');

    const insStart = DUR_OUT * 0.45;

    const tl = gsap.timeline({
      onComplete: () => {
        out.classList.remove('spa-active');
        gsap.set(out, { opacity: 0, z: 0, scale: 1, filter: 'none' });
        out.scrollTop = 0;
        busy = false;
        animateChartsIn(ins);
      }
    });

    tl.to(out, {
      opacity: 0, z: -350, scale: 0.90, filter: 'blur(10px)',
      duration: DUR_OUT, ease: 'power2.in', transformPerspective: 1400,
    }, 0);

    tl.to(ins, {
      opacity: 1, z: 0, scale: 1, filter: 'blur(0px)',
      duration: DUR_IN, ease: 'power2.out', transformPerspective: 1400,
    }, insStart);

    addCardsToTimeline(tl, ins, insStart + 0.15);

    current = toIdx;
    updateUI();
  }

  // ════════════════════════════════════════════════════════════
  // Cards — dentro del mismo timeline para sincronía exacta
  // ════════════════════════════════════════════════════════════
  function getCards(section) {
    return Array.from(section.querySelectorAll(
      '.card, .side-card, .predictor-card, .section-label, .section-title, .section-desc, .tl-item, .tab-nav'
    )).filter(el => {
      const pane = el.closest('.tab-pane');
      return !pane || pane.classList.contains('active');
    });
  }

  function prepareCards(section) {
    getCards(section).forEach(el => {
      gsap.set(el, { opacity: 0, z: -50, scale: 0.95, transformPerspective: 700 });
    });
  }

  // Añade los cards como tweens dentro del timeline existente
  // absoluteStart = posición en segundos desde el inicio del timeline
  function addCardsToTimeline(tl, section, absoluteStart) {
    getCards(section).forEach((el, i) => {
      tl.to(el, {
        opacity: 1,
        z: 0,
        scale: 1,
        duration: 0.65,
        ease: 'power3.out',
        transformPerspective: 700,
        clearProps: 'z,scale,transformPerspective',
      }, absoluteStart + i * 0.055);
    });
  }

  // ── Gráficas ─────────────────────────────────────────────────
  function animateChartsIn(section) {
    if (typeof Chart === 'undefined') return;
    // Para comparación, forzar rebuild si las gráficas no existen aún
    if (section.id === 'comparacion') {
      if (typeof buildCompM1 === 'function') buildCompM1();
      if (typeof buildCompM2 === 'function') buildCompM2();
      return;
    }
    setTimeout(() => {
      section.querySelectorAll('canvas').forEach(canvas => {
        const chart = Chart.getChart(canvas);
        if (!chart) return;
        chart.resize();
        chart.reset();
        chart.update('active');
      });
    }, 150);
  }

  // ── UI ───────────────────────────────────────────────────────
  function updateUI() {
    dots.forEach((d, i) => d.classList.toggle('active', i === current));
    document.querySelectorAll('.nav-links a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href').replace('#','') === SECTION_IDS[current]);
    });
    const isLast = current === sections.length - 1;
    nextBtn.classList.toggle('hidden', isLast);
    nextBtn.querySelector('.spa-next-label').textContent = isLast ? '' : NAV_LABELS[current + 1];
    history.replaceState(null, '', '#' + SECTION_IDS[current]);
  }

  // ── Init ─────────────────────────────────────────────────────
  const hash  = location.hash.replace('#','');
  const start = Math.max(0, SECTION_IDS.indexOf(hash));

  sections.forEach((s, i) => {
    if (i === start) {
      gsap.set(s, { opacity: 1, z: 0, scale: 1, filter: 'none' });
      s.classList.add('spa-active');
    } else {
      gsap.set(s, { opacity: 0, z: 0, scale: 1, filter: 'none' });
    }
  });

  current = start;
  updateUI();

  // Cards de la sección inicial
  const initTl = gsap.timeline();
  prepareCards(sections[start]);
  addCardsToTimeline(initTl, sections[start], 0.3);
})();
