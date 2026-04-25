'use strict';

// ── Video Speed ──────────────────────────────────────────────────
const heroVideo = document.querySelector('.hero-video-wrap video');
if (heroVideo) {
  heroVideo.playbackRate = 0.5; // Mitad de la velocidad normal
}

// ── GSAP ─────────────────────────────────────────────────────────
gsap.registerPlugin(ScrollTrigger);

// Scroll reveals desactivados — spa.js maneja las animaciones de entrada por sección

// Active nav link is managed by spa.js

// ── Tab system (generic) ───────────────────────────────────────────
document.querySelectorAll('.tab-nav').forEach(nav => {
  nav.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.tab;
      const parent = nav.parentElement;
      const incoming = document.getElementById(id);
      if (!incoming || incoming.classList.contains('active')) return;

      nav.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      parent.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.toggle('active', p.id === id);
      });

      animateBars(incoming);
      animateTabCharts(incoming);
    });
  });
});

// ── Bar fill animation ─────────────────────────────────────────────
function animateBars(scope) {
  const root = scope || document;
  root.querySelectorAll('.hbar-fill[data-w]').forEach(bar => {
    if (bar._animated) return;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        gsap.to(bar, { width: bar.dataset.w + '%', duration: 1.1, ease:'power2.out' });
        bar._animated = true;
        io.disconnect();
      }
    }, { threshold: 0.1 });
    io.observe(bar);
  });
}
animateBars();

// ── Reanimar gráficas al cambiar de tab ───────────────────────────
function animateTabCharts(pane) {
  if (!pane || typeof Chart === 'undefined') return;
  setTimeout(() => {
    pane.querySelectorAll('canvas').forEach(canvas => {
      const chart = Chart.getChart(canvas);
      if (!chart) return;
      // Fit canvas to its visible container, then redraw
      chart.resize();
      chart.update('none');
    });
  }, 60);
}

// ── Chart.js defaults ──────────────────────────────────────────────
Chart.defaults.animation = {
  duration: 900,
  easing: 'easeOutQuart',
};
Chart.defaults.color = '#6B7A64';
Chart.defaults.borderColor = 'rgba(45,106,39,0.1)';
Chart.defaults.font.family = "'Inter', 'Space Grotesk', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(255,255,255,0.97)';
Chart.defaults.plugins.tooltip.titleColor = '#1A2018';
Chart.defaults.plugins.tooltip.bodyColor = '#3D4A38';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(45,106,39,0.2)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 8;
Chart.defaults.plugins.legend.labels.padding = 16;

// ── Unweighted vs Balanced ─────────────────────────────────────────
new Chart(document.getElementById('chart-uwvbal'), {
  type: 'bar',
  data: {
    labels: ['AUC', 'Brier Score', 'Log Loss'],
    datasets: [
      { label:'Unweighted (final)', data:[0.7955, 0.0744, 0.2665],
        backgroundColor:'rgba(74,140,63,0.65)', borderColor:'#4A8C3F', borderWidth:1.5, borderRadius:6 },
      { label:'Balanced', data:[0.7963, 0.1768, 0.5413],
        backgroundColor:'rgba(217,107,90,0.45)', borderColor:'#D96B5A', borderWidth:1.5, borderRadius:6 }
    ]
  },
  options: {
    responsive:true, maintainAspectRatio:true, aspectRatio:1.8,
    plugins:{ legend:{ position:'bottom', labels:{ font:{size:11} } } },
    scales:{
      x:{ grid:{ display:false }, ticks:{ font:{size:11} } },
      y:{ grid:{ color:'rgba(45,106,39,0.1)' }, ticks:{ font:{size:11} } }
    }
  }
});

// ── ROC Curve ──────────────────────────────────────────────────────
new Chart(document.getElementById('chart-roc'), {
  type: 'line',
  data: {
    datasets: [
      { label:'Modelo xG (AUC=0.7955)',
        data:[{x:0,y:0},{x:.02,y:.11},{x:.05,y:.26},{x:.09,y:.38},{x:.14,y:.50},{x:.20,y:.60},{x:.30,y:.71},{x:.40,y:.78},{x:.52,y:.84},{x:.64,y:.89},{x:.76,y:.93},{x:.88,y:.96},{x:1,y:1}],
        borderColor:'#6DB85C', backgroundColor:'rgba(74,140,63,0.1)', fill:true, tension:0.35, pointRadius:0, borderWidth:2.5 },
      { label:'Random Forest (AUC=0.825)',
        data:[{x:0,y:0},{x:.02,y:.14},{x:.05,y:.30},{x:.09,y:.44},{x:.14,y:.56},{x:.20,y:.66},{x:.30,y:.76},{x:.40,y:.83},{x:.52,y:.88},{x:.64,y:.92},{x:.76,y:.95},{x:.88,y:.98},{x:1,y:1}],
        borderColor:'#C5A059', backgroundColor:'transparent', fill:false, tension:0.35, pointRadius:0, borderWidth:2, borderDash:[4,2] },
      { label:'Naive (AUC=0.5)',
        data:[{x:0,y:0},{x:1,y:1}],
        borderColor:'rgba(122,130,118,0.3)', fill:false, pointRadius:0, borderDash:[6,3], borderWidth:1.5 }
    ]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.4,
    plugins:{ legend:{ position:'bottom', labels:{ font:{size:11} } } },
    scales:{
      x:{ type:'linear', min:0, max:1, title:{display:true,text:'False Positive Rate',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} },
      y:{ min:0, max:1, title:{display:true,text:'True Positive Rate',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} }
    }
  }
});

// ── AUC Compare M1 — loaded from model_compare.json ───────────────
// Built after modelCompareData is fetched (see bottom of file)

// ── M2B Compare — loaded from model_compare.json ──────────────────
// Built after modelCompareData is fetched (see bottom of file)

// ── Confusion Matrix ───────────────────────────────────────────────
(function(){
  const el = document.getElementById('cm-container');
  if (!el) return;
  const cm = [[71,12,12],[19,8,13],[10,10,30]];
  const labs = ['H','D','A'];
  const tot = cm.flat().reduce((a,b)=>a+b,0);
  let h = '<div class="cm-wrap"><div class="cm-head"></div>';
  labs.forEach(l => { h += `<div class="cm-head">Real ${l}</div>`; });
  cm.forEach((row,i) => {
    h += `<div class="cm-row-lbl">Pred ${labs[i]}</div>`;
    row.forEach((v,j) => {
      const pct = ((v/tot)*100).toFixed(1);
      h += `<div class="cm-cell ${i===j?'cm-diag':'cm-off'}" title="${v} (${pct}%)">${v}</div>`;
    });
  });
  h += '</div>';
  el.innerHTML = h;
})();

// ── Coeficientes toggle ────────────────────────────────────────────
window.showCoef = function(cls) {
  document.getElementById('coef-H').style.display = cls==='H' ? 'block' : 'none';
  document.getElementById('coef-D').style.display = cls==='D' ? 'block' : 'none';
  document.getElementById('coef-h-btn').classList.toggle('active', cls==='H');
  document.getElementById('coef-d-btn').classList.toggle('active', cls==='D');
  animateBars(document.getElementById('coef-'+cls));
};

// ── FTR Donut ──────────────────────────────────────────────────────
new Chart(document.getElementById('chart-ftr'), {
  type:'doughnut',
  data:{
    labels:['Local (H) 42.3%','Empate (D) 26.1%','Visitante (A) 31.6%'],
    datasets:[{
      data:[123,76,92],
      backgroundColor:['rgba(74,140,63,0.78)','rgba(122,130,118,0.5)','rgba(197,160,89,0.78)'],
      borderColor:['#4A8C3F','#7A8078','#C5A059'],
      borderWidth:2, hoverOffset:8
    }]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.4,
    plugins:{
      legend:{ position:'bottom', labels:{ font:{size:11} } },
      tooltip:{ callbacks:{ label:i=>`${i.label}: ${i.raw} partidos` } }
    },
    cutout:'62%'
  }
});

// ── xG by zone bar ─────────────────────────────────────────────────
new Chart(document.getElementById('chart-xg-zone'), {
  type:'bar',
  data:{
    labels:['Pequeña área','Centro área','Área izq/der','Fuera área','Lejanía'],
    datasets:[{
      label:'xG medio (shot_quality_index)',
      data:[0.48, 0.31, 0.22, 0.12, 0.06],
      backgroundColor:['rgba(197,160,89,0.8)','rgba(74,140,63,0.72)','rgba(74,140,63,0.55)','rgba(74,140,63,0.35)','rgba(74,140,63,0.2)'],
      borderColor:['#C5A059','#4A8C3F','#4A8C3F','#4A8C3F','#4A8C3F'],
      borderWidth:1.5, borderRadius:6
    }]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.4,
    plugins:{ legend:{ display:false } },
    scales:{
      x:{ grid:{display:false}, ticks:{font:{size:11}} },
      y:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11}} }
    }
  }
});

// ── Team charts ────────────────────────────────────────────────────
let teamStatsData = [];
Promise.resolve(window.team_statsData)
  .then(data => {
    teamStatsData = data;

    // Populate team selects
    ['team-detail-sel','home-sel','away-sel','f-team'].forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      data.sort((a,b)=>a.team.localeCompare(b.team)).forEach(t => {
        const opt = new Option(t.team, t.team);
        if (id !== 'f-team') sel.add(opt.cloneNode(true));
        else sel.add(opt);
      });
    });

    // Default predictor
    const hs = document.getElementById('home-sel'), as_ = document.getElementById('away-sel');
    if (hs) hs.value = 'Liverpool';
    if (as_) as_.value = 'Arsenal';

    // Goals chart
    const top = [...data].sort((a,b)=>b.gf-a.gf).slice(0,10);
    new Chart(document.getElementById('chart-team-goals'), {
      type:'bar',
      data:{
        labels: top.map(t=>t.team),
        datasets:[{
          label:'Goles marcados',
          data: top.map(t=>t.gf),
          backgroundColor: top.map((_,i)=>i<3?'rgba(197,160,89,0.8)':'rgba(74,140,63,0.55)'),
          borderColor: top.map((_,i)=>i<3?'#C5A059':'#4A8C3F'),
          borderWidth:1.5, borderRadius:6
        }]
      },
      options:{
        responsive:true, maintainAspectRatio:true, aspectRatio:1.4, indexAxis:'y',
        plugins:{ legend:{display:false} },
        scales:{ x:{grid:{color:'rgba(45,106,39,0.1)'},ticks:{font:{size:11}}}, y:{grid:{display:false},ticks:{font:{size:11}}} }
      }
    });

    // Home wins chart
    const hw = [...data].sort((a,b)=>b.wins-a.wins).slice(0,10);
    new Chart(document.getElementById('chart-home-wins'), {
      type:'bar',
      data:{
        labels: hw.map(t=>t.team),
        datasets:[
          { label:'Victorias', data:hw.map(t=>t.wins), backgroundColor:'rgba(74,140,63,0.72)', borderColor:'#4A8C3F', borderWidth:1.5, borderRadius:4 },
          { label:'Empates', data:hw.map(t=>t.draws), backgroundColor:'rgba(122,130,118,0.42)', borderColor:'#7A8078', borderWidth:1.5, borderRadius:4 },
          { label:'Derrotas', data:hw.map(t=>t.losses), backgroundColor:'rgba(217,107,90,0.5)', borderColor:'#D96B5A', borderWidth:1.5, borderRadius:4 }
        ]
      },
      options:{
        responsive:true, maintainAspectRatio:true, aspectRatio:2.2,
        plugins:{ legend:{position:'bottom',labels:{font:{size:11}}} },
        scales:{
          x:{ stacked:false, grid:{display:false}, ticks:{font:{size:11}} },
          y:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11}} }
        }
      }
    });
  })
  .catch(e => console.warn('team_stats:', e));

// Team detail on select
document.getElementById('team-detail-sel')?.addEventListener('change', function() {
  const t = teamStatsData.find(x => x.team === this.value);
  const el = document.getElementById('team-detail-stats');
  if (!t) { el.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;font-size:0.85rem;">Selecciona un equipo</div>'; return; }
  const pts = t.wins*3 + t.draws;
  const gd = t.gf - t.ga;
  el.innerHTML = `
    <div class="stat-row"><span class="label">Victorias</span><span class="value green">${t.wins}</span></div>
    <div class="stat-row"><span class="label">Empates</span><span class="value gold">${t.draws}</span></div>
    <div class="stat-row"><span class="label">Derrotas</span><span class="value red">${t.losses}</span></div>
    <div class="stat-row"><span class="label">Goles a favor</span><span class="value blue">${t.gf}</span></div>
    <div class="stat-row"><span class="label">Goles en contra</span><span class="value red">${t.ga}</span></div>
    <div class="stat-row"><span class="label">Diferencia de goles</span><span class="value ${gd>=0?'green':'red'}">${gd>=0?'+':''}${gd}</span></div>
    <div class="stat-row"><span class="label">Puntos estimados</span><span class="value gold mono">${pts}</span></div>
  `;
});

// ── Clustering chart ───────────────────────────────────────────────
let clusteringData = [];
let clusterChart = null;

Promise.resolve(window.clusteringData)
  .then(players => {
    clusteringData = players;
    const colorsHex = ['#6DB85C','#C5A059','#4A8C3F'];
    const colorsRgba = ['rgba(109,184,92,0.6)','rgba(197,160,89,0.6)','rgba(74,140,63,0.6)'];
    const names = ['Rematadores distancia','Atacantes interiores','Finalizadores área'];

    const ds = [0,1,2].map(c => ({
      label: names[c],
      data: players.filter(p=>p.cluster===c).map(p=>({x:p.pc1,y:p.pc2,name:p.name,team:p.team,goals:p.goals,xg:p.mean_xg,dist:p.mean_distance})),
      backgroundColor: colorsRgba[c],
      borderColor: colorsHex[c],
      borderWidth:1.5, pointRadius:5, pointHoverRadius:8
    }));

    const ctx = document.getElementById('chart-clustering');
    if (!ctx) return;
    clusterChart = new Chart(ctx, {
      type:'scatter',
      data:{ datasets:ds },
      options:{
        animation: false,
        responsive:true, maintainAspectRatio:true, aspectRatio:1.0,
        plugins:{
          legend:{ position:'bottom', labels:{font:{size:11}} },
          tooltip:{ callbacks:{ label:i=>`${i.raw.name} (${i.raw.team}) — Goals:${i.raw.goals} xG:${i.raw.xg}` } }
        },
        scales:{
          x:{ type:'linear', position:'bottom', title:{display:true,text:'PC1',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} },
          y:{ type:'linear', title:{display:true,text:'PC2',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} }
        },
        onClick(e, els) {
          if (els.length) {
            const idx = els[0].datasetIndex;
            showClusterProfile(idx);
          }
        }
      }
    });

    showClusterProfile(0);
  })
  .catch(e=>console.warn('clustering:', e));

// Cluster profiles
const PROFILES = [
  { name:'Rematadores de distancia', rate:'8.2%', dist:'21.0m', xg:'0.303', box:'Bajo', note:'Volumen alto, goles desde fuera del área, baja conversión.' },
  { name:'Atacantes interiores mixtos', rate:'10.8%', dist:'18.9m', xg:'0.358', box:'Medio', note:'Perfil equilibrado, entran bien al área, versatilidad ofensiva.' },
  { name:'Finalizadores de área', rate:'16.5%', dist:'14.2m', xg:'0.416', box:'Alto', note:'Máxima conversión, tiros de primer toque, cabezazos, alta xG.' }
];

window.showClusterProfile = function(c) {
  [0,1,2].forEach(i => document.getElementById('cp'+i)?.classList.toggle('active', i===c));
  const p = PROFILES[c];
  const el = document.getElementById('cluster-profile');
  if (!el) return;
  const cols = ['blue','green','gold'];
  el.innerHTML = `
    <div class="stat-row"><span class="label">Descripción</span><span class="value ${cols[c]}">${p.name}</span></div>
    <div class="stat-row"><span class="label">Goal rate</span><span class="value mono">${p.rate}</span></div>
    <div class="stat-row"><span class="label">Distancia media</span><span class="value mono">${p.dist}</span></div>
    <div class="stat-row"><span class="label">xG medio/tiro</span><span class="value mono">${p.xg}</span></div>
    <div class="stat-row"><span class="label">Box share</span><span class="value mono">${p.box}</span></div>
    <div style="margin-top:10px;padding:10px 14px;background:rgba(74,140,63,0.06);border:1px solid var(--border);border-radius:8px;font-size:0.8rem;color:var(--text-muted);">${p.note}</div>
  `;
  // Show top players of cluster (both sidebar panels)
  const top = clusteringData.filter(pl=>pl.cluster===c).sort((a,b)=>b.goals-a.goals).slice(0,8);
  const playerHtml = top.length ? top.map(pl=>`
    <div class="stat-row">
      <span class="label">${pl.name} <span style="opacity:0.5;font-size:0.75em">(${pl.team})</span></span>
      <span class="value mono">${pl.goals} goles · xG ${pl.mean_xg}</span>
    </div>`).join('') : '<div style="color:var(--text-muted);font-size:0.83rem;">Sin datos</div>';
  const pe = document.getElementById('cluster-players');
  if (pe) pe.innerHTML = playerHtml;
  const pi = document.getElementById('cluster-players-inline');
  if (pi) pi.innerHTML = `<div class="card-tag" style="margin-top:10px;">Top jugadores</div>${playerHtml}`;
};

// ── PITCH CANVAS — Shot Map ────────────────────────────────────────
const pitchCanvas = document.getElementById('pitch-canvas');
const pitchCtx = pitchCanvas?.getContext('2d');
const ptip = document.getElementById('ptip');
const W = 900, H = 580;

let shots = [], filterMode = 'all', teamFilter = '', xgMin = 0;

function px(x){ return (x/100)*W; }
function py(y){ return (y/100)*H; }

function drawPitch() {
  if (!pitchCtx) return;
  const ctx = pitchCtx;
  ctx.clearRect(0,0,W,H);

  // Grass stripes
  for (let i=0;i<10;i++){
    ctx.fillStyle = i%2===0 ? '#1B5E37' : '#1E6940';
    ctx.fillRect(px(i*10),0,px(10),H);
  }

  // Lines
  ctx.strokeStyle = 'rgba(255,255,255,0.88)';
  ctx.lineWidth = 1.8;

  const line = (x1,y1,x2,y2) => { ctx.beginPath(); ctx.moveTo(px(x1),py(y1)); ctx.lineTo(px(x2),py(y2)); ctx.stroke(); };

  // Border
  ctx.strokeRect(px(0),py(0),px(100),py(100));
  // Halfway
  line(50,0,50,100);
  // Centre circle
  ctx.beginPath(); ctx.arc(px(50),py(50),px(9.15),0,Math.PI*2); ctx.stroke();
  // Centre spot
  ctx.beginPath(); ctx.arc(px(50),py(50),3,0,Math.PI*2); ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.fill();
  // Penalty areas
  ctx.strokeRect(px(0),py(21.1),px(16.5),py(57.8));
  ctx.strokeRect(px(83.5),py(21.1),px(16.5),py(57.8));
  // 6-yard
  ctx.strokeRect(px(0),py(36.8),px(5.5),py(26.4));
  ctx.strokeRect(px(94.5),py(36.8),px(5.5),py(26.4));
  // Goals
  ctx.lineWidth = 3;
  ctx.strokeStyle = 'rgba(255,255,255,0.5)';
  ctx.strokeRect(px(-2),py(44.2),px(2),py(11.6));
  ctx.strokeRect(px(100),py(44.2),px(2),py(11.6));
  ctx.lineWidth = 1.8; ctx.strokeStyle = 'rgba(255,255,255,0.88)';
  // Penalty spots
  [11,89].forEach(x => { ctx.beginPath(); ctx.arc(px(x),py(50),2.5,0,Math.PI*2); ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.fill(); });
  // Penalty arcs
  ctx.save();
  ctx.beginPath(); ctx.rect(px(16.5),0,px(83.5-16.5),H); ctx.clip();
  ctx.beginPath(); ctx.arc(px(11),py(50),px(9.15),0,Math.PI*2); ctx.stroke();
  ctx.restore();
  ctx.save();
  ctx.beginPath(); ctx.rect(0,0,px(83.5),H); ctx.clip();
  ctx.beginPath(); ctx.arc(px(89),py(50),px(9.15),0,Math.PI*2); ctx.stroke();
  ctx.restore();
  // Corners
  [[0,0,-Math.PI/2,0],[0,100,0,Math.PI/2],[100,0,-Math.PI,Math.PI/2*-1],[100,100,Math.PI/2,Math.PI]].forEach(([cx,cy,sa,ea])=>{
    ctx.beginPath(); ctx.arc(px(cx),py(cy),px(1),sa,ea); ctx.stroke();
  });
}

function xgToColor(xg) {
  if (xg >= 0.4) return { r:217,g:107,b:90 };   // warm red
  if (xg >= 0.2) return { r:197,g:160,b:89 };   // gold
  return { r:109,g:184,b:92 };                   // light green
}

function drawShots(list) {
  if (!pitchCtx) return;
  list.forEach(s => {
    const r = 4 + s.xg * 26;
    const sx = px(s.x), sy = py(s.y);
    const c = xgToColor(s.xg);
    pitchCtx.beginPath();
    pitchCtx.arc(sx, sy, r, 0, Math.PI*2);
    pitchCtx.fillStyle = `rgba(${c.r},${c.g},${c.b},0.68)`;
    pitchCtx.fill();
    if (s.goal) {
      pitchCtx.beginPath();
      pitchCtx.arc(sx, sy, r+2.5, 0, Math.PI*2);
      pitchCtx.strokeStyle = 'rgba(255,255,255,0.95)';
      pitchCtx.lineWidth = 2.2;
      pitchCtx.stroke();
    }
  });
}

function getFiltered() {
  return shots.filter(s => {
    if (filterMode==='goals' && !s.goal) return false;
    if (filterMode==='nogoals' && s.goal) return false;
    if (teamFilter && s.team !== teamFilter) return false;
    if (s.xg < xgMin) return false;
    return true;
  });
}

function updateStats(list) {
  const goals = list.filter(s=>s.goal).length;
  const avgXg = list.length ? (list.reduce((a,s)=>a+s.xg,0)/list.length).toFixed(3) : '—';
  const rate = list.length ? ((goals/list.length)*100).toFixed(1)+'%' : '—';
  document.getElementById('stat-shots').textContent = list.length;
  document.getElementById('stat-goals').textContent = goals;
  document.getElementById('stat-xg').textContent = list.length ? avgXg : '—';
  document.getElementById('stat-rate').textContent = rate;
  document.getElementById('shot-count').textContent = `${list.length} tiros`;
}

function render() {
  drawPitch();
  const list = getFiltered();
  drawShots(list);
  updateStats(list);
}

Promise.resolve(window.shot_mapData)
  .then(data => {
    shots = data;
    // populate team filter
    const teams = [...new Set(data.map(s=>s.team).filter(Boolean))].sort();
    const sel = document.getElementById('f-team');
    teams.forEach(t => sel?.add(new Option(t, t)));
    render();
  })
  .catch(() => { drawPitch(); });

// Controls
['all','goals','nogoals'].forEach(mode => {
  document.getElementById('f-'+mode)?.addEventListener('click', () => {
    document.querySelectorAll('.pitch-controls .ctrl-btn[id^="f-"]').forEach(b=>b.classList.remove('active'));
    document.getElementById('f-'+mode)?.classList.add('active');
    filterMode = mode;
    render();
  });
});

document.getElementById('f-team')?.addEventListener('change', function() {
  teamFilter = this.value;
  render();
});

document.getElementById('xg-slider')?.addEventListener('input', function() {
  xgMin = parseFloat(this.value);
  document.getElementById('xg-val').textContent = xgMin.toFixed(2);
  render();
});

// Tooltip
if (pitchCanvas) {
  pitchCanvas.addEventListener('mousemove', e => {
    const rect = pitchCanvas.getBoundingClientRect();
    const sx = (e.clientX-rect.left)*(W/rect.width);
    const sy = (e.clientY-rect.top)*(H/rect.height);
    const list = getFiltered();
    let found = null;
    for (let i=list.length-1;i>=0;i--) {
      const s=list[i], r=4+s.xg*26+3;
      if (Math.hypot(px(s.x)-sx, py(s.y)-sy)<r) { found=s; break; }
    }
    if (found) {
      const c=xgToColor(found.xg);
      ptip.innerHTML = `<strong style="color:rgb(${c.r},${c.g},${c.b})">${found.player||'Jugador'}</strong> · ${found.team||''}<br>xG: <strong>${found.xg.toFixed(3)}</strong> · ${found.goal?'<span style="color:#6DB85C">⚽ GOL</span>':'No gol'}`;
      ptip.classList.add('vis');
      const wr = pitchCanvas.parentElement.getBoundingClientRect();
      ptip.style.left = (e.clientX-wr.left+14)+'px';
      ptip.style.top  = (e.clientY-wr.top-52)+'px';
    } else { ptip.classList.remove('vis'); }
  });
  pitchCanvas.addEventListener('mouseleave', ()=>ptip.classList.remove('vis'));
}



// ── MATCH PREDICTOR ────────────────────────────────────────────────
const M2B_COEF = {
  H:{ c:-3.732329, ph:6.576327, pd:2.200271, pfd:-0.297817, hs:0.585427 },
  D:{ c:-1.260906, ph:3.139686, pd:-3.541955, pfd:-0.340690, hs:0.606123 }
};

let teamsOdds = {};

Promise.resolve(window.matches_teamsData)
  .then(data => {
    data.forEach(t => { teamsOdds[t.team] = t; });
    ['home-sel','away-sel'].forEach(id => {
      const s = document.getElementById(id);
      if (!s) return;
      data.sort((a,b)=>a.team.localeCompare(b.team)).forEach(t=>s.add(new Option(t.team,t.team)));
    });
    const hs=document.getElementById('home-sel'), as_=document.getElementById('away-sel');
    if (hs) hs.value='Liverpool';
    if (as_) as_.value='Arsenal';
  });

function softmax3(a,b,c){ const ea=Math.exp(a),eb=Math.exp(b),ec=Math.exp(c),s=ea+eb+ec; return [ea/s,eb/s,ec/s]; }

document.getElementById('pred-btn')?.addEventListener('click', ()=>{
  const ht = document.getElementById('home-sel')?.value;
  const at = document.getElementById('away-sel')?.value;
  if (!ht || !at) return;
  if (ht===at) { alert('Elige equipos diferentes'); return; }

  const hd = teamsOdds[ht], ad = teamsOdds[at];
  if (!hd) return;

  const rawH=1/hd.b365h, rawD=1/hd.b365d, rawA=1/hd.b365a;
  const norm=rawH+rawD+rawA;
  const pH=rawH/norm, pD=rawD/norm;

  const lH = M2B_COEF.H.c + M2B_COEF.H.ph*pH + M2B_COEF.H.pd*pD;
  const lD = M2B_COEF.D.c + M2B_COEF.D.ph*pH + M2B_COEF.D.pd*pD;
  const [probH,probD,probA] = softmax3(lH,lD,0);

  const res = document.getElementById('pred-result');
  res.classList.add('vis');

  // Reset
  ['h','d','a'].forEach(k=>{ document.getElementById('bar-'+k).style.width='0%'; document.getElementById('pct-'+k).textContent='—'; });

  setTimeout(()=>{
    const fmt = v=>(v*100).toFixed(1)+'%';
    document.getElementById('bar-h').style.width = fmt(probH);
    document.getElementById('bar-d').style.width = fmt(probD);
    document.getElementById('bar-a').style.width = fmt(probA);
    document.getElementById('pct-h').textContent = fmt(probH);
    document.getElementById('pct-d').textContent = fmt(probD);
    document.getElementById('pct-a').textContent = fmt(probA);

    // Verdict
    const vEl = document.getElementById('pred-verdict');
    const maxP = Math.max(probH,probD,probA);
    let verdict, color;
    if (maxP===probH) { verdict=`Favorito: ${ht} (Local)`; color='#2D6A27'; }
    else if (maxP===probA) { verdict=`Favorito: ${at} (Visitante)`; color='#B8892A'; }
    else { verdict='Empate más probable'; color='#6B7A64'; }
    vEl.style.cssText=`display:block;background:rgba(45,106,39,0.07);border:1px solid rgba(45,106,39,0.18);border-radius:8px;color:${color};font-size:0.8rem;font-weight:700;padding:6px 10px;text-align:center;margin-top:6px;`;
    vEl.textContent=verdict;
  }, 60);
});

// ── Calibration chart (decile-based, from model stats) ─────────────
new Chart(document.getElementById('chart-calibration'), {
  type:'line',
  data:{
    labels:['0.0','0.05','0.10','0.15','0.20','0.30','0.40','0.50','0.60','0.80','1.0'],
    datasets:[
      { label:'Modelo xG', data:[0.0,0.038,0.088,0.131,0.192,0.278,0.371,0.452,0.551,0.718,0.921],
        borderColor:'#6DB85C', backgroundColor:'rgba(74,140,63,0.1)', fill:true, tension:0.3, pointRadius:4, borderWidth:2.5 },
      { label:'Perfecta', data:[0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,0.60,0.80,1.0],
        borderColor:'rgba(197,160,89,0.5)', fill:false, pointRadius:0, borderDash:[6,3], borderWidth:1.5 }
    ]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.5,
    plugins:{ legend:{ position:'bottom', labels:{ font:{size:11} } } },
    scales:{
      x:{ title:{display:true,text:'Probabilidad predicha',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} },
      y:{ min:0, max:1, title:{display:true,text:'Frecuencia real',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} }
    }
  }
});

// ── ROC All models ─────────────────────────────────────────────────
new Chart(document.getElementById('chart-roc-all'), {
  type:'line',
  data:{
    datasets:[
      { label:'RF (AUC=0.825)', data:[{x:0,y:0},{x:.02,y:.14},{x:.05,y:.30},{x:.09,y:.44},{x:.14,y:.56},{x:.20,y:.66},{x:.30,y:.76},{x:.40,y:.83},{x:.52,y:.88},{x:.64,y:.92},{x:.76,y:.95},{x:.88,y:.98},{x:1,y:1}], borderColor:'#C5A059', fill:false, tension:0.3, pointRadius:0, borderWidth:2.5 },
      { label:'Logistic (0.7955)', data:[{x:0,y:0},{x:.02,y:.11},{x:.05,y:.26},{x:.09,y:.38},{x:.14,y:.50},{x:.20,y:.60},{x:.30,y:.71},{x:.40,y:.78},{x:.52,y:.84},{x:.64,y:.89},{x:.76,y:.93},{x:.88,y:.96},{x:1,y:1}], borderColor:'#6DB85C', fill:false, tension:0.3, pointRadius:0, borderWidth:2 },
      { label:'MLP (0.7789)', data:[{x:0,y:0},{x:.02,y:.10},{x:.05,y:.23},{x:.09,y:.35},{x:.14,y:.47},{x:.20,y:.57},{x:.30,y:.68},{x:.40,y:.75},{x:.52,y:.81},{x:.64,y:.87},{x:.76,y:.92},{x:.88,y:.96},{x:1,y:1}], borderColor:'#4A8C3F', fill:false, tension:0.3, pointRadius:0, borderWidth:1.5, borderDash:[5,2] },
      { label:'SVM (0.7455)', data:[{x:0,y:0},{x:.02,y:.08},{x:.05,y:.19},{x:.09,y:.30},{x:.14,y:.41},{x:.20,y:.51},{x:.30,y:.63},{x:.40,y:.71},{x:.52,y:.78},{x:.64,y:.84},{x:.76,y:.90},{x:.88,y:.95},{x:1,y:1}], borderColor:'#D96B5A', fill:false, tension:0.3, pointRadius:0, borderWidth:1.5, borderDash:[3,3] },
      { label:'Naive', data:[{x:0,y:0},{x:1,y:1}], borderColor:'rgba(122,130,118,0.3)', fill:false, pointRadius:0, borderDash:[6,3], borderWidth:1 }
    ]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.4,
    plugins:{ legend:{ position:'bottom', labels:{ font:{size:11} } } },
    scales:{
      x:{ type:'linear', min:0, max:1, title:{display:true,text:'FPR',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} },
      y:{ min:0, max:1, title:{display:true,text:'TPR',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} }
    }
  }
});


// ── Silhouette chart ───────────────────────────────────────────────
new Chart(document.getElementById('chart-silhouette'), {
  type:'line',
  data:{
    labels:[2,3,4,5,6,7,8],
    datasets:[{ label:'Silhouette Score', data:[0.2818,0.2104,0.1876,0.1642,0.1534,0.1421,0.1308],
      borderColor:'#C5A059', backgroundColor:'rgba(197,160,89,0.1)', fill:true, tension:0.3,
      pointRadius:5, pointBackgroundColor:'#C5A059', borderWidth:2.5
    }]
  },
  options:{
    responsive:true, maintainAspectRatio:true, aspectRatio:1.8,
    plugins:{ legend:{display:false} },
    scales:{
      x:{ title:{display:true,text:'k (clusters)',font:{size:11}}, grid:{display:false} },
      y:{ title:{display:true,text:'Silhouette',font:{size:11}}, grid:{color:'rgba(45,106,39,0.1)'} }
    }
  }
});

// ── xG teams chart — from xg_teams.json ───────────────────────────
let xgTeamsData = [];
let xgTeamsChart = null;
let xgSortKey = 'goals';

function buildXgTeamsChart() {
  const data = [...xgTeamsData].sort((a,b)=>b[xgSortKey]-a[xgSortKey]);
  const labelMap = { goals:'Goles totales', mean_xg:'xG medio/tiro', n_shots:'Tiros totales', goal_rate:'Conversión' };
  const metricData = data.map(t => xgSortKey === 'goal_rate' ? +(t.goal_rate*100).toFixed(1) : t[xgSortKey]);
  const fmtCallback = v => xgSortKey === 'goal_rate' ? v.toFixed(1)+'%' : (xgSortKey === 'mean_xg' ? v.toFixed(4) : v);

  if (xgTeamsChart) {
    xgTeamsChart.data.labels = data.map(t=>t.team_name);
    xgTeamsChart.data.datasets[0].data = metricData;
    xgTeamsChart.data.datasets[0].label = labelMap[xgSortKey];
    xgTeamsChart.data.datasets[0].backgroundColor = data.map((_,i)=>i<3?'rgba(197,160,89,0.82)':i<10?'rgba(74,140,63,0.65)':'rgba(74,140,63,0.35)');
    xgTeamsChart.data.datasets[0].borderColor = data.map((_,i)=>i<3?'#C5A059':'#4A8C3F');
    xgTeamsChart.options.scales.x.ticks.callback = fmtCallback;
    xgTeamsChart.resize();
    xgTeamsChart.update('active');
    return;
  }
  xgTeamsChart = new Chart(document.getElementById('chart-xg-teams'), {
    type:'bar',
    data:{
      labels: data.map(t=>t.team_name),
      datasets:[{
        label: labelMap[xgSortKey],
        data: metricData,
        backgroundColor: data.map((_,i)=>i<3?'rgba(197,160,89,0.82)':i<10?'rgba(74,140,63,0.65)':'rgba(74,140,63,0.35)'),
        borderColor: data.map((_,i)=>i<3?'#C5A059':'#4A8C3F'),
        borderWidth:1.5, borderRadius:5
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:true, aspectRatio:1.6, indexAxis:'y',
      plugins:{ legend:{display:false},
        tooltip:{ callbacks:{ label: i => ` ${fmtCallback(i.raw)}` } }
      },
      scales:{
        x:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:10}, callback: fmtCallback} },
        y:{ grid:{display:false}, ticks:{font:{size:9}} }
      }
    }
  });
}

window.sortXgTeams = function(key) {
  xgSortKey = key;
  ['goals','mean_xg','n_shots','goal_rate'].forEach(k => {
    document.getElementById('xg-sort-'+k)?.classList.toggle('active', k===key);
  });
  buildXgTeamsChart();
};

Promise.resolve(window.xg_teamsData)
  .then(data => {
    xgTeamsData = data;
    const tEl = (id, v) => { const e=document.getElementById(id); if(e) e.textContent=v; };
    const topXg = [...data].sort((a,b)=>b.mean_xg-a.mean_xg)[0];
    const topShots = [...data].sort((a,b)=>b.n_shots-a.n_shots)[0];
    const topRate = [...data].sort((a,b)=>b.goal_rate-a.goal_rate)[0];
    tEl('top-xg-team', topXg?.team_name||'—');
    tEl('top-xg-val', `xG medio: ${topXg?.mean_xg?.toFixed(4)||'—'}`);
    tEl('top-shots-team', topShots?.team_name||'—');
    tEl('top-shots-val', `${topShots?.n_shots||'—'} tiros totales`);
    tEl('top-rate-team', topRate?.team_name||'—');
    tEl('top-rate-val', `${((topRate?.goal_rate||0)*100).toFixed(1)}% conversión`);
    buildXgTeamsChart();
  })
  .catch(e=>console.warn('xg_teams:', e));

// ── Model Comparison — load from model_compare.json ────────────────
let modelCompareData = null;
let compM1Chart = null, compM2Chart = null;
let compM1AllMode = false, compM2AllMode = false;
let compM1Metric = 'auc', compM2Metric = 'accuracy';

const MODEL_COLORS = {
  random_forest:       { bg:'rgba(197,160,89,0.75)', bd:'#C5A059' },
  logistic_unweighted: { bg:'rgba(74,140,63,0.72)',  bd:'#4A8C3F' },
  logistic_multinomial:{ bg:'rgba(74,140,63,0.72)',  bd:'#4A8C3F' },
  logistic_balanced:   { bg:'rgba(109,184,92,0.55)', bd:'#6DB85C' },
  mlp:                 { bg:'rgba(197,160,89,0.45)', bd:'#C5A059' },
  svm_rbf:             { bg:'rgba(217,107,90,0.55)', bd:'#D96B5A' },
};
const MODEL_LABELS = {
  random_forest:'Random Forest', logistic_unweighted:'Logistic (uw)',
  logistic_balanced:'Logistic (bal)', mlp:'MLP', svm_rbf:'SVM RBF',
  logistic_multinomial:'Logistic Multiclass'
};
const METRIC_LABELS = { auc:'AUC-ROC', brier:'Brier Score', log_loss:'Log Loss', accuracy:'Accuracy', f1_macro:'F1-Macro' };
const METRIC_FMT = { auc: v=>v.toFixed(4), brier: v=>v.toFixed(4), log_loss: v=>v.toFixed(4), accuracy: v=>(v*100).toFixed(1)+'%', f1_macro: v=>v.toFixed(4) };
const METRIC_HIGHER_BETTER = { auc:true, brier:false, log_loss:false, accuracy:true, f1_macro:true };

function buildCompM1() {
  if (!modelCompareData) return;
  const all = modelCompareData.modelo1.filter((d,i,a)=>a.findIndex(x=>x.model===d.model)===i); // dedupe
  let rows;
  if (compM1AllMode) {
    rows = all;
  } else {
    const va = document.getElementById('comp-m1-a')?.value;
    const vb = document.getElementById('comp-m1-b')?.value;
    rows = all.filter(d => d.model===va || d.model===vb);
  }
  const labels = rows.map(d=>MODEL_LABELS[d.model]||d.model);
  const values = rows.map(d=>d[compM1Metric]||0);
  const bgs = rows.map(d=>(MODEL_COLORS[d.model]||{bg:'rgba(74,140,63,0.5)'}).bg);
  const bds = rows.map(d=>(MODEL_COLORS[d.model]||{bd:'#4A8C3F'}).bd);
  const config = {
    type:'bar',
    data:{ labels, datasets:[{ label:METRIC_LABELS[compM1Metric], data:values,
      backgroundColor:bgs, borderColor:bds, borderWidth:1.5, borderRadius:8 }] },
    options:{
      responsive:true, maintainAspectRatio:false, indexAxis:'y',
      plugins:{ legend:{display:false},
        tooltip:{ callbacks:{ label: i => ` ${METRIC_FMT[compM1Metric](i.raw)}` } } },
      scales:{
        x:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11}, callback:v=>METRIC_FMT[compM1Metric](v)} },
        y:{ grid:{display:false}, ticks:{font:{size:11}} }
      }
    }
  };
  if (compM1Chart) { compM1Chart.destroy(); }
  compM1Chart = new Chart(document.getElementById('chart-comp-m1'), config);
  // Winner badge
  const hiB = METRIC_HIGHER_BETTER[compM1Metric];
  const best = rows.reduce((a,b)=> hiB ? (b[compM1Metric]>a[compM1Metric]?b:a) : (b[compM1Metric]<a[compM1Metric]?b:a));
  const we = document.getElementById('comp-m1-winner');
  if (we) we.innerHTML = `<div class="winner-badge">🏆 Mejor: ${MODEL_LABELS[best.model]||best.model} — ${METRIC_LABELS[compM1Metric]}: ${METRIC_FMT[compM1Metric](best[compM1Metric])}</div>`;
}

function buildCompM2() {
  if (!modelCompareData) return;
  const all = modelCompareData.modelo2b;
  let rows;
  if (compM2AllMode) {
    rows = all;
  } else {
    const va = document.getElementById('comp-m2-a')?.value;
    const vb = document.getElementById('comp-m2-b')?.value;
    rows = all.filter(d => d.model===va || d.model===vb);
  }
  // Include Bet365 as reference line for accuracy
  const showBet = compM2Metric === 'accuracy';
  const labels = rows.map(d=>MODEL_LABELS[d.model]||d.model);
  const values = rows.map(d=>d[compM2Metric]||0);
  const bgs = rows.map(d=>(MODEL_COLORS[d.model]||{bg:'rgba(74,140,63,0.5)'}).bg);
  const bds = rows.map(d=>(MODEL_COLORS[d.model]||{bd:'#4A8C3F'}).bd);
  const datasets = [{ label:METRIC_LABELS[compM2Metric], data:values, backgroundColor:bgs, borderColor:bds, borderWidth:1.5, borderRadius:8 }];
  if (showBet) {
    const bet365 = modelCompareData.modelo2b[0]?.bet365_accuracy || 0.5043;
    datasets.push({ type:'line', label:'Bet365', data:new Array(labels.length).fill(bet365),
      borderColor:'rgba(197,160,89,0.7)', borderDash:[6,3], pointRadius:0, fill:false, borderWidth:2 });
  }
  const config = {
    type:'bar',
    data:{ labels, datasets },
    options:{
      responsive:true, maintainAspectRatio:false, indexAxis:'y',
      plugins:{ legend:{ display:showBet, position:'bottom', labels:{font:{size:11}} },
        tooltip:{ callbacks:{ label: i => ` ${METRIC_FMT[compM2Metric](i.raw)}` } } },
      scales:{
        x:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11}, callback:v=>METRIC_FMT[compM2Metric](v)} },
        y:{ grid:{display:false}, ticks:{font:{size:11}} }
      }
    }
  };
  if (compM2Chart) { compM2Chart.destroy(); }
  compM2Chart = new Chart(document.getElementById('chart-comp-m2'), config);
  const hiB = METRIC_HIGHER_BETTER[compM2Metric];
  const best = rows.reduce((a,b)=> hiB ? (b[compM2Metric]>a[compM2Metric]?b:a) : (b[compM2Metric]<a[compM2Metric]?b:a));
  const we = document.getElementById('comp-m2-winner');
  if (we) we.innerHTML = `<div class="winner-badge">🏆 Mejor: ${MODEL_LABELS[best.model]||best.model} — ${METRIC_LABELS[compM2Metric]}: ${METRIC_FMT[compM2Metric](best[compM2Metric])}</div>`;
}

window.toggleCompM1All = function() {
  compM1AllMode = !compM1AllMode;
  const btn = document.getElementById('comp-m1-all-btn');
  if (btn) btn.classList.toggle('active', compM1AllMode);
  buildCompM1();
};
window.toggleCompM2All = function() {
  compM2AllMode = !compM2AllMode;
  const btn = document.getElementById('comp-m2-all-btn');
  if (btn) btn.classList.toggle('active', compM2AllMode);
  buildCompM2();
};

// Metric tab buttons
document.querySelectorAll('[data-m1-metric]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-m1-metric]').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    compM1Metric = btn.dataset.m1Metric;
    buildCompM1();
  });
});
document.querySelectorAll('[data-m2-metric]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-m2-metric]').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    compM2Metric = btn.dataset.m2Metric;
    buildCompM2();
  });
});

// VS selectors
['comp-m1-a','comp-m1-b'].forEach(id => {
  document.getElementById(id)?.addEventListener('change', buildCompM1);
});
['comp-m2-a','comp-m2-b'].forEach(id => {
  document.getElementById(id)?.addEventListener('change', buildCompM2);
});

Promise.resolve(window.model_compareData)
  .then(data => {
    modelCompareData = data;

    // AUC compare in xg-bonus tab (from real data)
    const m1 = data.modelo1.filter((d,i,a)=>a.findIndex(x=>x.model===d.model)===i);
    const aucSorted = [...m1].sort((a,b)=>b.auc-a.auc);
    new Chart(document.getElementById('chart-auc-compare'), {
      type:'bar',
      data:{
        labels: aucSorted.map(d=>MODEL_LABELS[d.model]||d.model),
        datasets:[{ label:'AUC-ROC',
          data: aucSorted.map(d=>d.auc),
          backgroundColor: aucSorted.map(d=>(MODEL_COLORS[d.model]||{bg:'rgba(74,140,63,0.5)'}).bg),
          borderColor: aucSorted.map(d=>(MODEL_COLORS[d.model]||{bd:'#4A8C3F'}).bd),
          borderWidth:1.5, borderRadius:6
        }]
      },
      options:{
        animation: false,
        responsive:true, maintainAspectRatio:true, aspectRatio:1.5, indexAxis:'y',
        plugins:{ legend:{display:false} },
        scales:{
          x:{ min:0.70, max:0.84, grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11},callback:v=>v.toFixed(3)} },
          y:{ grid:{display:false}, ticks:{font:{size:11}} }
        }
      }
    });

    // M2B compare in predictor tab
    const m2 = data.modelo2b;
    const bet365 = m2[0]?.bet365_accuracy || 0.5043;
    new Chart(document.getElementById('chart-m2b'), {
      type:'bar',
      data:{
        labels: [...m2.map(d=>MODEL_LABELS[d.model]||d.model), 'Bet365'],
        datasets:[{ label:'Accuracy',
          data: [...m2.map(d=>d.accuracy), bet365],
          backgroundColor:[...m2.map(d=>(MODEL_COLORS[d.model]||{bg:'rgba(74,140,63,0.5)'}).bg), 'rgba(197,160,89,0.55)'],
          borderColor:[...m2.map(d=>(MODEL_COLORS[d.model]||{bd:'#4A8C3F'}).bd), '#C5A059'],
          borderWidth:1.5, borderRadius:6
        }]
      },
      options:{
        animation: false,
        responsive:true, maintainAspectRatio:true, aspectRatio:2, indexAxis:'y',
        plugins:{ legend:{display:false} },
        scales:{
          x:{ grid:{color:'rgba(45,106,39,0.1)'}, ticks:{font:{size:11},callback:v=>(v*100).toFixed(1)+'%'} },
          y:{ grid:{display:false}, ticks:{font:{size:11}} }
        }
      }
    });

    // M1 bonus table
    const tbl = document.getElementById('m1-bonus-table');
    if (tbl) {
      tbl.innerHTML = aucSorted.map(d=>`
        <div class="stat-row">
          <span class="label">${MODEL_LABELS[d.model]||d.model}</span>
          <span class="value mono" style="color:${d.model==='random_forest'?'var(--accent-gold)':d.model.includes('unweighted')?'var(--accent-cyan)':'var(--text-secondary)'}">
            AUC ${d.auc.toFixed(4)} · Brier ${d.brier.toFixed(4)}
          </span>
        </div>`).join('');
    }

    buildCompM1();
    buildCompM2();
  })
  .catch(e=>console.warn('model_compare:', e));
