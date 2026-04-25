"""
generate_charts.py
Genera las 3 graficas estaticas (Dona, xG por Zona, Calibracion)
con los mismos datos y colores exactos que el codigo JS.
"""

import matplotlib
matplotlib.use('Agg')  # sin GUI
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── Ruta de salida ─────────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(__file__), 'pagina_web', 'graficas')
os.makedirs(OUT, exist_ok=True)

# ── Colores exactos del JS ─────────────────────────────────────────
GREEN      = (74/255,  140/255,  63/255,  0.85)
GRAY       = (122/255, 130/255, 118/255,  0.55)
GOLD       = (197/255, 160/255,  89/255,  0.85)
GREEN_LINE = '#6DB85C'
GOLD_LINE  = '#C5A059'
GRID_COLOR = (45/255, 106/255, 39/255, 0.12)

BG = 'white'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
})

# ══════════════════════════════════════════════════════════════════════
# 1. DONA — Distribucion FTR
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(5.8, 4.2), facecolor=BG)
ax.set_facecolor(BG)

data   = [123, 76, 92]
labels = ['Local (H)  42.3 %', 'Empate (D)  26.1 %', 'Visitante (A)  31.6 %']
colors = [GREEN, GRAY, GOLD]
border = ['#4A8C3F', '#7A8078', '#C5A059']

wedges, texts = ax.pie(
    data,
    labels=None,
    colors=colors,
    startangle=90,
    wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2),
    counterclock=False,
)
for w, bc in zip(wedges, border):
    w.set_edgecolor(bc)

ax.legend(
    wedges, labels,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.08),
    ncol=1,
    frameon=False,
    fontsize=10.5,
)
ax.set_title('Distribución FTR — 291 partidos', fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'Dona.png'), dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✅  Dona.png generada')

# ══════════════════════════════════════════════════════════════════════
# 2. BARRAS — xG por Zona del Campo
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(5.8, 4.2), facecolor=BG)
ax.set_facecolor(BG)

zonas  = ['Pequeña\nárea', 'Centro\nárea', 'Área\nizq/der', 'Fuera\nárea', 'Lejanía']
xg_val = [0.48, 0.31, 0.22, 0.12, 0.06]
bar_colors = [
    (197/255, 160/255,  89/255, 0.85),
    ( 74/255, 140/255,  63/255, 0.75),
    ( 74/255, 140/255,  63/255, 0.58),
    ( 74/255, 140/255,  63/255, 0.38),
    ( 74/255, 140/255,  63/255, 0.22),
]
edge_colors = ['#C5A059', '#4A8C3F', '#4A8C3F', '#4A8C3F', '#4A8C3F']

bars = ax.bar(zonas, xg_val, color=bar_colors, edgecolor=edge_colors,
              linewidth=1.4, width=0.55)

# etiquetas encima de cada barra
for bar, val in zip(bars, xg_val):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.008,
            f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='600')

ax.set_ylabel('xG medio', fontsize=10)
ax.set_title('xG por Zona del Campo\n(Shot Quality Index promedio)', fontsize=12, fontweight='bold')
ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
ax.set_axisbelow(True)
ax.spines['left'].set_color('#cccccc')
ax.spines['bottom'].set_color('#cccccc')
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=9, colors='#666666')
ax.set_ylim(0, 0.58)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'shot quality index.png'), dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✅  shot quality index.png generada')

# ══════════════════════════════════════════════════════════════════════
# 3. LINEA — Curva de Calibracion
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(5.8, 4.2), facecolor=BG)
ax.set_facecolor(BG)

x_labels = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80, 1.0]
modelo_xg = [0.0, 0.038, 0.088, 0.131, 0.192, 0.278, 0.371, 0.452, 0.551, 0.718, 0.921]
perfecta  = [0,   0.05,  0.10,  0.15,  0.20,  0.30,  0.40,  0.50,  0.60,  0.80,  1.0]

ax.fill_between(x_labels, modelo_xg, alpha=0.12, color=GREEN_LINE)
ax.plot(x_labels, modelo_xg, color=GREEN_LINE, linewidth=2.5,
        marker='o', markersize=4.5, label='Modelo xG', zorder=3)
ax.plot(x_labels, perfecta, color=GOLD_LINE, linewidth=1.5,
        linestyle='--', alpha=0.6, label='Calibración perfecta')

ax.set_xlabel('Probabilidad predicha', fontsize=10)
ax.set_ylabel('Frecuencia real', fontsize=10)
ax.set_title('Curva de Calibración por Decil de xG', fontsize=12, fontweight='bold')
ax.legend(loc='upper left', frameon=False, fontsize=10)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
ax.xaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
ax.set_axisbelow(True)
ax.spines['left'].set_color('#cccccc')
ax.spines['bottom'].set_color('#cccccc')
ax.tick_params(labelsize=9, colors='#555555')
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'calibracion.png'), dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✅  calibracion.png generada')

print('\n🎯 Las 3 imagenes fueron guardadas en pagina_web/graficas/')
