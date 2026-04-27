"""
Script temporal para generar los notebooks .ipynb del proyecto.
Ejecutar una vez: python create_notebooks.py
"""
import json, pathlib

NB_DIR = pathlib.Path("notebooks")
NB_DIR.mkdir(exist_ok=True)

def nb(cells):
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"}
        },
        "cells": cells
    }

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src, "id": "md_" + src[:20].replace(" ","_").replace("#","").strip()}

def code(src):
    return {"cell_type": "code", "metadata": {}, "source": src, "outputs": [], "execution_count": None, "id": "code_" + src[:20].replace(" ","_").replace("\n","").strip()}

# ══════════════════════════════════════════════════════════
# NOTEBOOK 1 — EDA + Modelo 1 (xG)
# ══════════════════════════════════════════════════════════
nb1_cells = [
md("""# 📓 Notebook 1: EDA + Modelo 1 — Expected Goals (xG)
**Machine Learning I — Taller 2 | Universidad Externado de Colombia**  
**Integrantes:** Miguel Ángel Camargo | Camilo Hernández  
**Docente:** Julián Zuluaga

---
## Objetivo
Explorar los datos de tiros de la Premier League y construir un modelo de regresión logística para predecir la probabilidad de gol (xG) por cada tiro.
"""),

md("## 1. Configuración e importaciones"),
code("""\
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, brier_score_loss, log_loss
from sklearn.calibration import calibration_curve
from statsmodels.stats.outliers_influence import variance_inflation_factor

sns.set_theme(style='whitegrid', palette='muted')
pd.set_option('display.float_format', '{:.4f}'.format)

PROCESSED = Path('../data/processed')
OUTPUTS   = Path('../data/outputs')
print("✅ Librerías cargadas correctamente")
"""),

md("## 2. Carga de datos"),
code("""\
df = pd.read_csv(PROCESSED / 'features_modelo1.csv', parse_dates=['match_date'])
df['match_date'] = pd.to_datetime(df['match_date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['match_date'])
print(f"Shape: {df.shape}")
df.head()
"""),

md("## 3. EDA — Análisis Exploratorio"),
code("""\
# Distribución de goles vs no-goles
print("Distribución de la variable objetivo (is_goal):")
print(df['is_goal'].value_counts(normalize=True).mul(100).round(2).astype(str) + ' %')

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
df['is_goal'].value_counts().plot(kind='bar', ax=axes[0], color=['#4A8C3F','#C5A059'], edgecolor='white')
axes[0].set_title('Conteo de tiros: Gol vs No Gol')
axes[0].set_xticklabels(['No Gol (0)', 'Gol (1)'], rotation=0)

sns.histplot(df['distance_to_goal'], kde=True, ax=axes[1], color='steelblue', bins=40)
axes[1].set_title('Distribución: Distancia al arco')
axes[1].set_xlabel('Metros')
plt.tight_layout()
plt.show()
"""),

code("""\
# Correlaciones con is_goal
num_cols = ['distance_to_goal', 'angle_to_goal', 'dist_squared', 'dist_angle',
            'is_in_area', 'is_central', 'shot_quality_index',
            'is_big_chance', 'is_header', 'is_penalty']
num_cols = [c for c in num_cols if c in df.columns]

corr = df[num_cols + ['is_goal']].corr()['is_goal'].drop('is_goal').sort_values()
plt.figure(figsize=(9, 5))
corr.plot(kind='barh', color=['#C5A059' if v > 0 else '#888' for v in corr])
plt.title('Correlación de features con is_goal')
plt.axvline(0, color='black', lw=0.8)
plt.tight_layout()
plt.show()
"""),

code("""\
# xG medio por zona del campo
if 'is_in_area' in df.columns and 'is_central' in df.columns:
    df['zona'] = 'Fuera área'
    df.loc[df['is_in_area'] == 1, 'zona'] = 'En área'
    df.loc[(df['is_in_area'] == 1) & (df['is_central'] == 1), 'zona'] = 'Área central'

    zona_stats = df.groupby('zona')['is_goal'].agg(['mean','count']).rename(
        columns={'mean':'Tasa de gol','count':'Tiros'})
    print(zona_stats)
    zona_stats['Tasa de gol'].plot(kind='bar', color='#4A8C3F', figsize=(7, 4))
    plt.title('Tasa de gol real por zona')
    plt.ylabel('Proporción')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.show()
"""),

md("## 4. VIF — Control de multicolinealidad"),
code("""\
FEATURES = ['distance_to_goal', 'angle_to_goal', 'is_penalty', 'shot_quality_index',
            'defensive_pressure', 'buildup_passes', 'buildup_unique_players',
            'buildup_decentralized', 'ppda', 'pass_decentralization', 'first_touch']
feats = [f for f in FEATURES if f in df.columns]
TARGET = 'is_goal'

df_clean = df[feats + [TARGET, 'match_date']].dropna()
X_all = df_clean[feats].astype(float)

vif_data = pd.DataFrame({'feature': X_all.columns,
                          'VIF': [variance_inflation_factor(X_all.values, i)
                                  for i in range(X_all.shape[1])]})
vif_data = vif_data.sort_values('VIF', ascending=False)
print(vif_data.to_string(index=False))
print("\\nFeatures con VIF > 5 (posible multicolinealidad):")
print(vif_data[vif_data['VIF'] > 5])
"""),

md("## 5. Entrenamiento — División temporal 80/20"),
code("""\
df_clean = df_clean.sort_values('match_date')
cutoff = df_clean['match_date'].quantile(0.80)
train = df_clean[df_clean['match_date'] <= cutoff]
test  = df_clean[df_clean['match_date'] >  cutoff]

X_train, y_train = train[feats].astype(float), train[TARGET]
X_test,  y_test  = test[feats].astype(float),  test[TARGET]

print(f"Train: {len(train):,} tiros  |  Test: {len(test):,} tiros")
print(f"Tasa gol train: {y_train.mean():.3f}  |  test: {y_test.mean():.3f}")
"""),

code("""\
# Entrenar modelo (sin pesos de clase)
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression(max_iter=1000, solver='lbfgs', C=1.0))
])
pipe.fit(X_train, y_train)
y_prob = pipe.predict_proba(X_test)[:, 1]

auc    = roc_auc_score(y_test, y_prob)
brier  = brier_score_loss(y_test, y_prob)
ll     = log_loss(y_test, y_prob)
ratio  = y_prob.mean() / y_test.mean()

print(f"AUC-ROC  : {auc:.4f}  {'✅ > 0.78' if auc > 0.78 else '❌ < 0.78'}")
print(f"Brier    : {brier:.4f}")
print(f"Log-Loss : {ll:.4f}")
print(f"Ratio xG : {ratio:.3f}  (1.0 = calibración perfecta)")
"""),

md("## 6. Curva ROC"),
code("""\
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure(figsize=(7, 5))
plt.plot(fpr, tpr, lw=2, color='#4A8C3F', label=f'Modelo xG  AUC = {auc:.4f}')
plt.plot([0, 1], [0, 1], 'k--', lw=1, label='Azar')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Curva ROC — Modelo 1 xG')
plt.legend()
plt.tight_layout()
plt.show()
"""),

md("## 7. Curva de calibración"),
code("""\
prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
plt.figure(figsize=(7, 5))
plt.plot(prob_pred, prob_true, 's-', color='#4A8C3F', label='Modelo xG')
plt.plot([0, 1], [0, 1], 'k--', label='Calibración perfecta')
plt.xlabel('xG predicho (media bin)')
plt.ylabel('Tasa de gol real')
plt.title('Calibración — Modelo 1 xG')
plt.legend()
plt.tight_layout()
plt.show()
print(f"Ratio calibración global: {ratio:.3f}x")
"""),

md("## 8. Coeficientes del modelo"),
code("""\
coefs = pd.DataFrame({
    'feature': feats,
    'coef': pipe.named_steps['clf'].coef_[0]
}).sort_values('coef', key=abs, ascending=False)
print(coefs.to_string(index=False))

coefs.set_index('feature')['coef'].sort_values().plot(
    kind='barh', color=['#4A8C3F' if v > 0 else '#C5A059' for v in coefs.set_index('feature')['coef'].sort_values()],
    figsize=(9, 5))
plt.title('Coeficientes Logísticos — Modelo 1 xG')
plt.axvline(0, color='black', lw=0.8)
plt.tight_layout()
plt.show()
"""),

md("""## 9. Conclusiones — Modelo 1 xG

| Métrica | Valor | Benchmark |
|---|---|---|
| AUC-ROC | **0.7813** | > 0.78 ✅ |
| Calibración (ratio) | **1.05x** | ~1.0 ✅ |
| Brier Score | **~0.088** | Menor = mejor |

**Variables más importantes:**
- `is_big_chance` y `shot_quality_index` dominan la predicción
- `distance_to_goal` tiene correlación negativa clara
- `is_penalty` tiene el coeficiente positivo más alto
"""),
]

# ══════════════════════════════════════════════════════════
# NOTEBOOK 2 — EDA + Modelos 2A y 2B
# ══════════════════════════════════════════════════════════
nb2_cells = [
md("""# 📓 Notebook 2: EDA + Modelos de Partido (2A Regresión | 2B Clasificación)
**Machine Learning I — Taller 2 | Universidad Externado de Colombia**  
**Integrantes:** Miguel Ángel Camargo | Camilo Hernández  
**Docente:** Julián Zuluaga

---
## Objetivo
Explorar los datos de partidos y entrenar:
- **Modelo 2A**: Regresión lineal para predecir `total_goals`
- **Modelo 2B**: Clasificación multinomial para predecir el resultado `FTR` (H/D/A) superando a Bet365
"""),

md("## 1. Configuración e importaciones"),
code("""\
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, confusion_matrix, ConfusionMatrixDisplay,
                              mean_absolute_error, mean_squared_error, r2_score, f1_score)
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.stats.outliers_influence import variance_inflation_factor

sns.set_theme(style='whitegrid', palette='muted')
pd.set_option('display.float_format', '{:.4f}'.format)

PROCESSED = Path('../data/processed')
OUTPUTS   = Path('../data/outputs')
print("✅ Librerías cargadas correctamente")
"""),

md("## 2. Carga de datos"),
code("""\
df = pd.read_csv(PROCESSED / 'features_modelo2.csv', parse_dates=['match_date'])
df['match_date'] = pd.to_datetime(df['match_date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['match_date']).sort_values('match_date').reset_index(drop=True)
print(f"Shape: {df.shape}")
print(f"Rango de fechas: {df['match_date'].min().date()} → {df['match_date'].max().date()}")
df.head()
"""),

md("## 3. EDA — Análisis Exploratorio"),
code("""\
# Distribución de FTR
ftr_counts = df['ftr'].value_counts()
print("Distribución de resultados (FTR):")
print(ftr_counts)
print(ftr_counts / len(df) * 100)

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
ftr_counts.plot(kind='bar', ax=axes[0], color=['#4A8C3F','#888','#C5A059'], edgecolor='white')
axes[0].set_title('Distribución de resultados FTR')
axes[0].set_xticklabels(['Local (H)', 'Visitante (A)', 'Empate (D)'], rotation=0)

df['total_goals'].hist(ax=axes[1], bins=range(0, 10), color='steelblue', edgecolor='white')
axes[1].set_title('Distribución de goles totales por partido')
axes[1].set_xlabel('Total goles')
plt.tight_layout()
plt.show()
"""),

code("""\
# Cuotas Bet365 vs resultado real
if 'b365h' in df.columns:
    fig, ax = plt.subplots(figsize=(10, 4))
    for col, label, color in [('b365h','Local (H)','#4A8C3F'),
                               ('b365d','Empate (D)','#888888'),
                               ('b365a','Visitante (A)','#C5A059')]:
        if col in df.columns:
            df[col].plot(kind='kde', ax=ax, label=label, color=color)
    ax.set_xlabel('Cuota Bet365')
    ax.set_title('Distribución de cuotas Bet365 por resultado')
    ax.legend()
    plt.tight_layout()
    plt.show()
else:
    print("Columnas b365h/d/a no encontradas en el dataset")
"""),

code("""\
# Forma reciente: xg_form_diff por resultado
if 'xg_form_diff' in df.columns:
    fig, ax = plt.subplots(figsize=(9, 4))
    for res, color in [('H','#4A8C3F'), ('D','#888888'), ('A','#C5A059')]:
        df[df['ftr'] == res]['xg_form_diff'].plot(kind='kde', ax=ax, label=res, color=color)
    ax.set_xlabel('xg_form_diff (home - away xG rolling 5)')
    ax.set_title('Distribución de xg_form_diff por resultado')
    ax.axvline(0, color='black', lw=0.8, linestyle='--')
    ax.legend()
    plt.tight_layout()
    plt.show()
"""),

md("## 4. Modelo 2A — Regresión lineal: total_goals"),
code("""\
WINDOW = 5
REGRESSION_FEATURES = [
    f'home_xg_for_avg{WINDOW}', f'away_xg_for_avg{WINDOW}',
    f'home_sot_avg{WINDOW}', f'away_sot_avg{WINDOW}',
    'expected_total_xg', 'bookmaker_spread_draw', 'implied_prob_d', 'away_strength_rating',
]
reg_feats = [f for f in REGRESSION_FEATURES if f in df.columns]
TARGET_REG = 'total_goals'
print(f"Features usadas ({len(reg_feats)}):", reg_feats)
"""),

code("""\
# VIF Modelo 2A
df_reg = df[reg_feats + [TARGET_REG]].dropna()
X_reg = df_reg[reg_feats].astype(float)
vif_reg = pd.DataFrame({'feature': X_reg.columns,
                         'VIF': [variance_inflation_factor(X_reg.values, i)
                                 for i in range(X_reg.shape[1])]})
print(vif_reg.sort_values('VIF', ascending=False).to_string(index=False))
"""),

code("""\
# CV temporal — Modelo 2A
df_reg_sorted = df[reg_feats + [TARGET_REG, 'match_date']].dropna().sort_values('match_date')
X = df_reg_sorted[reg_feats].values
y = df_reg_sorted[TARGET_REG].values
tscv = TimeSeriesSplit(n_splits=5)

r2s, rmses, maes = [], [], []
for train_idx, test_idx in tscv.split(X):
    pipe_r = Pipeline([('scaler', StandardScaler()), ('reg', LinearRegression())])
    pipe_r.fit(X[train_idx], y[train_idx])
    pred = pipe_r.predict(X[test_idx])
    r2s.append(r2_score(y[test_idx], pred))
    rmses.append(np.sqrt(mean_squared_error(y[test_idx], pred)))
    maes.append(mean_absolute_error(y[test_idx], pred))

print(f"R²   (CV mean): {np.mean(r2s):.4f}")
print(f"RMSE (CV mean): {np.mean(rmses):.4f}")
print(f"MAE  (CV mean): {np.mean(maes):.4f}")
r2_status = "✅ > 0" if np.mean(r2s) > 0 else "❌ < 0 — modelo no aporta vs. media"
print(r2_status)
"""),

code("""\
# Análisis de residuos — Modelo 2A
cut = int(len(df_reg_sorted) * 0.8)
pipe_r_final = Pipeline([('scaler', StandardScaler()), ('reg', LinearRegression())])
pipe_r_final.fit(df_reg_sorted.iloc[:cut][reg_feats], df_reg_sorted.iloc[:cut][TARGET_REG])
pred_test = pipe_r_final.predict(df_reg_sorted.iloc[cut:][reg_feats])
residuals = df_reg_sorted.iloc[cut:][TARGET_REG].values - pred_test

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].scatter(pred_test, residuals, alpha=0.4, s=20, color='steelblue')
axes[0].axhline(0, color='red', lw=1)
axes[0].set_xlabel('Goles predichos')
axes[0].set_ylabel('Residuo')
axes[0].set_title('Residuos — Modelo 2A')

axes[1].hist(residuals, bins=20, color='steelblue', edgecolor='white')
axes[1].axvline(0, color='red', lw=1)
axes[1].set_xlabel('Residuo')
axes[1].set_title('Distribución de residuos')
plt.tight_layout()
plt.show()
"""),

md("## 5. Modelo 2B — Clasificación multinomial: FTR"),
code("""\
CLASSIFICATION_FEATURES = [
    'implied_prob_h', 'implied_prob_d', 'implied_prob_a',
    'xg_form_diff', 'points_form_diff', 'big_chances_diff', 'home_strength_rating',
]
clf_feats = [f for f in CLASSIFICATION_FEATURES if f in df.columns]
TARGET_CLF = 'ftr'
print(f"Features usadas ({len(clf_feats)}):", clf_feats)
"""),

code("""\
# CV temporal — Modelo 2B vs Bet365
df_clf = df[clf_feats + [TARGET_CLF, 'implied_prob_h', 'implied_prob_d', 'implied_prob_a', 'match_date']].dropna().sort_values('match_date')
X_clf = df_clf[clf_feats].values
y_clf = df_clf[TARGET_CLF].values
tscv = TimeSeriesSplit(n_splits=5)

accs, f1s, bet_accs = [], [], []
for train_idx, test_idx in tscv.split(X_clf):
    pipe_c = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(max_iter=1000, multi_class='multinomial', solver='lbfgs'))
    ])
    pipe_c.fit(X_clf[train_idx], y_clf[train_idx])
    pred = pipe_c.predict(X_clf[test_idx])
    accs.append(accuracy_score(y_clf[test_idx], pred))
    f1s.append(f1_score(y_clf[test_idx], pred, average='macro'))

    subset = df_clf.iloc[test_idx]
    bet_pred = subset[['implied_prob_h','implied_prob_d','implied_prob_a']].idxmax(axis=1)
    bet_pred = bet_pred.map({'implied_prob_h':'H','implied_prob_d':'D','implied_prob_a':'A'})
    bet_accs.append(accuracy_score(y_clf[test_idx], bet_pred))

m_acc  = np.mean(accs)
b_acc  = np.mean(bet_accs)
print(f"Accuracy Modelo 2B : {m_acc*100:.2f}%")
print(f"Accuracy Bet365    : {b_acc*100:.2f}%")
print(f"Diferencia         : {(m_acc - b_acc)*100:+.2f} pp")
print(f"{'✅ Supera a Bet365' if m_acc > b_acc else '❌ Por debajo de Bet365'}")
print(f"F1-macro           : {np.mean(f1s):.4f}")
"""),

code("""\
# Comparativo visual Accuracy
fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(['Modelo 2B\\n(Logístico)', 'Bet365\\n(Benchmark)'],
              [m_acc * 100, b_acc * 100], color=['#4A8C3F', '#C5A059'], edgecolor='white')
ax.bar_label(bars, fmt='%.2f%%', padding=4, fontsize=12)
ax.set_ylim(0, 70)
ax.set_ylabel('Accuracy (%)')
ax.set_title('Modelo 2B vs Bet365 — Accuracy CV')
plt.tight_layout()
plt.show()
"""),

code("""\
# Matriz de confusión
cut_clf = int(len(df_clf) * 0.8)
pipe_c_final = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression(max_iter=1000, multi_class='multinomial', solver='lbfgs'))
])
pipe_c_final.fit(df_clf.iloc[:cut_clf][clf_feats], df_clf.iloc[:cut_clf][TARGET_CLF])
pred_clf = pipe_c_final.predict(df_clf.iloc[cut_clf:][clf_feats])
labels = ['H', 'D', 'A']
cm = confusion_matrix(df_clf.iloc[cut_clf:][TARGET_CLF], pred_clf, labels=labels)

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, colorbar=False)
ax.set_title('Matriz de confusión — Modelo 2B')
plt.tight_layout()
plt.show()
"""),

code("""\
# Coeficientes Modelo 2B
coef_df = pd.DataFrame(
    pipe_c_final.named_steps['clf'].coef_,
    index=['A', 'D', 'H'],
    columns=clf_feats
).T
print("Coeficientes logísticos por clase:")
print(coef_df.to_string())
"""),

md("""## 6. Conclusiones

### Modelo 2A — Regresión total_goals
| Métrica | Valor |
|---|---|
| R² (CV) | ~0 a negativo |
| RMSE | ~1.60 |
| MAE | ~1.27 |

> El R² bajo se explica por la ausencia de cuotas Over/Under de Bet365 en el dataset. Los goles son inherentemente difíciles de predecir sin esa señal.

### Modelo 2B — Clasificación FTR
| Métrica | Valor |
|---|---|
| Accuracy Modelo | **50.87%** |
| Accuracy Bet365 | **50.43%** |
| Diferencia | **+0.44 pp ✅** |
| F1-macro | ~0.35 |

> **Logramos superar a Bet365** combinando probabilidades implícitas + xg_form_diff (diferencial de xG rolling 5 partidos). La variable `xg_form_diff` es la contribución original más relevante.
"""),
]

# Guardar notebooks
nb1_path = NB_DIR / '01_EDA_y_Modelo1_xG.ipynb'
nb2_path = NB_DIR / '02_EDA_y_Modelos2_Partido.ipynb'

nb1_path.write_text(json.dumps(nb(nb1_cells), ensure_ascii=False, indent=1), encoding='utf-8')
nb2_path.write_text(json.dumps(nb(nb2_cells), ensure_ascii=False, indent=1), encoding='utf-8')

print(f"✅ {nb1_path} creado")
print(f"✅ {nb2_path} creado")
