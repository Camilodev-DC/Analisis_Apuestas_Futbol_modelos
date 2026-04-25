'use strict';

/* ── 3D Animations Module ──────────────────────────────────────── */

// ── Three.js Hero Background (floating particles only — no ball)
(function initThreeHero() {
  if (typeof THREE === 'undefined') return;

  const container = document.getElementById('threejs-hero');
  if (!container) return;

  const heroSection = document.querySelector('.hero') || document.body;
  const W = heroSection.clientWidth || window.innerWidth;
  const H = heroSection.clientHeight || window.innerHeight;

  const renderer = new THREE.WebGLRenderer({ canvas: container, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(W, H);
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 200);
  camera.position.set(0, 0, 40);

  // ── Floating data particles (small spheres)
  const particleCount = 60;
  const particles = [];
  for (let i = 0; i < particleCount; i++) {
    const size = Math.random() * 0.3 + 0.08;
    const geo = new THREE.SphereGeometry(size, 6, 6);
    const colors = [0x2D6A27, 0x4A8C3F, 0xB8892A, 0x6DB85C, 0xD4A84E];
    const mat = new THREE.MeshBasicMaterial({
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: Math.random() * 0.5 + 0.3,
      transparent: true,
    });
    const mesh = new THREE.Mesh(geo, mat);
    const r = Math.random() * 28 + 8;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;
    mesh.position.set(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      r * Math.cos(phi) - 20
    );
    mesh._speed = (Math.random() - 0.5) * 0.008;
    mesh._offset = Math.random() * Math.PI * 2;
    mesh._radius = r;
    mesh._theta = theta;
    mesh._phi = phi;
    scene.add(mesh);
    particles.push(mesh);
  }

  // ── Mouse parallax
  let mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', e => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  // ── Resize
  window.addEventListener('resize', () => {
    const w = heroSection.clientWidth || window.innerWidth;
    const h = heroSection.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });

  let t = 0;
  function animate() {
    requestAnimationFrame(animate);
    t += 0.01;

    // Drift particles
    particles.forEach(p => {
      p._theta += p._speed;
      p.position.x = p._radius * Math.sin(p._phi) * Math.cos(p._theta);
      p.position.y = p._radius * Math.sin(p._phi) * Math.sin(p._theta) + Math.sin(t * 0.5 + p._offset) * 1.5;
      p.material.opacity = 0.25 + Math.sin(t + p._offset) * 0.2;
    });

    // Parallax camera
    camera.position.x += (mouseX * 3 - camera.position.x) * 0.04;
    camera.position.y += (-mouseY * 2 - camera.position.y) * 0.04;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }
  animate();
})();

// ── Mouse-tracking 3D card tilt ───────────────────────────────────
// Uses GSAP for both move and reset so the transition is always smooth
(function initCardTilt() {
  const cards = document.querySelectorAll('.card, .predictor-card, .side-card');

  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = (e.clientX - cx) / (rect.width / 2);
      const dy = (e.clientY - cy) / (rect.height / 2);

      gsap.to(card, {
        rotateX: dy * -7,
        rotateY: dx * 7,
        z: 8,
        duration: 0.15,
        ease: 'power1.out',
        transformPerspective: 800,
        overwrite: 'auto',
      });
    });

    card.addEventListener('mouseleave', () => {
      gsap.to(card, {
        rotateX: 0,
        rotateY: 0,
        z: 0,
        duration: 0.55,
        ease: 'elastic.out(1, 0.6)',
        transformPerspective: 800,
        overwrite: 'auto',
      });
    });
  });
})();

// ── Floating data number counters (3D flip on scroll) ─────────────
(function init3DCounters() {
  const bigs = document.querySelectorAll('.card-big, .side-num');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const el = e.target;
        el.style.animation = 'none';
        el.offsetHeight; // reflow
        el.style.animation = 'flip3dIn 0.6s cubic-bezier(.23,1,.32,1) both';
        io.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  bigs.forEach(el => io.observe(el));
})();

// Scroll parallax desactivado — navegación SPA sin scroll entre secciones

// ── 3D hover on nav links ─────────────────────────────────────────
(function initNavHover3D() {
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.addEventListener('mouseenter', () => {
      gsap.to(a, { rotateX: -10, z: 4, duration: 0.2, ease: 'power2.out', transformPerspective: 200 });
    });
    a.addEventListener('mouseleave', () => {
      gsap.to(a, { rotateX: 0, z: 0, duration: 0.35, ease: 'power2.out', transformPerspective: 200 });
    });
  });
})();

// ── 3D rotating section label on intersection ─────────────────────
(function initSectionLabel3D() {
  const labels = document.querySelectorAll('.section-label');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const el = e.target;
        gsap.fromTo(el,
          { rotateX: -30, opacity: 0, transformPerspective: 400 },
          { rotateX: 0, opacity: 1, duration: 0.7, ease: 'power3.out' }
        );
        io.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  labels.forEach(el => {
    el.style.opacity = '0';
    io.observe(el);
  });
})();

// ── KPI chip 3D tilt on hover ─────────────────────────────────────
(function initKpiShimmer() {
  document.querySelectorAll('.kpi-chip').forEach(chip => {
    chip.addEventListener('mouseenter', () => {
      gsap.to(chip, {
        rotateY: 8,
        rotateX: -4,
        z: 20,
        duration: 0.4,
        ease: 'power2.out',
        transformPerspective: 600,
        overwrite: 'auto',
      });
    });
    chip.addEventListener('mouseleave', () => {
      gsap.to(chip, {
        rotateY: 0,
        rotateX: 0,
        z: 0,
        duration: 0.55,
        ease: 'elastic.out(1, 0.6)',
        transformPerspective: 600,
        overwrite: 'auto',
      });
    });
  });
})();

// ── 3D flip for tab buttons ───────────────────────────────────────
(function initTabFlip3D() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      gsap.fromTo(this,
        { rotateX: -20, transformPerspective: 400 },
        { rotateX: 0, duration: 0.35, ease: 'power2.out' }
      );
    });
  });
})();

// ── Scroll-driven depth effect on cards ──────────────────────────
(function initScrollDepth3D() {
  const cardsAll = document.querySelectorAll('.grid-3 .card, .grid-4 .card');
  if (!cardsAll.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        gsap.fromTo(e.target,
          {
            transformPerspective: 800,
            rotateX: 20,
            rotateY: i % 2 === 0 ? -8 : 8,
            opacity: 0,
            z: -40,
          },
          {
            rotateX: 0,
            rotateY: 0,
            opacity: 1,
            z: 0,
            duration: 0.8,
            delay: (i % 4) * 0.1,
            ease: 'power3.out',
          }
        );
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  cardsAll.forEach(c => {
    c.style.opacity = '0';
    io.observe(c);
  });
})();

// ── Ripple 3D effect on pred-btn click ───────────────────────────
(function initPredBtn3D() {
  const btn = document.getElementById('pred-btn');
  if (!btn) return;

  btn.addEventListener('click', function() {
    gsap.fromTo(this,
      { rotateX: 10, scale: 0.96, transformPerspective: 400 },
      { rotateX: 0, scale: 1, duration: 0.5, ease: 'elastic.out(1,0.5)' }
    );
  });
})();
