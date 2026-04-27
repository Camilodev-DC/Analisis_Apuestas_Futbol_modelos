# ⚽ Premier League ML Predictor — Taller 2

> **Curso:** Machine Learning I (ML1-2026I)  
> **Universidad Externado de Colombia**  
> **Docente:** Julián Zuluaga

---

## 👥 Integrantes

| Nombre completo |
|---| 
| Miguel Ángel Camargo 
| Camilo Hernández 

---

## 🌐 Dashboard Desplegado

🔗 **URL:** https://analisis-apuestas-futbol-modelos.vercel.app/#hero

> El dashboard es completamente interactivo: incluye curvas ROC animadas, calibración, distribución de resultados y comparativos de accuracy vs Bet365.

---

## 📌 Descripción del Approach

### Objetivo
Superar el benchmark predictivo de **Bet365** en la Premier League 2024/25, usando modelos de regresión logística con ingeniería de variables avanzada.

### Pipeline general

```
data/raw/  →  Feature Engineering  →  Entrenamiento  →  Evaluación  →  Dashboard
```

### Modelos entrenados

| Modelo | Tipo | Target | Métrica principal |
|---|---|---|---|
| **Modelo 1 — xG** | Regresión logística | `is_goal` (por tiro) | AUC-ROC = **0.7813** |
| **Modelo 2A** | Regresión lineal | `total_goals` (por partido) | RMSE = 1.60, MAE = 1.27 |
| **Modelo 2B** | Clasificación multinomial | `FTR` (H/D/A) | Accuracy = **50.87%** vs Bet365 50.43% |

### Features más importantes

**Modelo 1 (xG por tiro):**
- `distance_to_goal`, `angle_to_goal` — geometría del tiro
- `is_big_chance` — indicador de gran oportunidad
- `shot_quality_index` — índice compuesto propio (big_chance + area + distancia)
- `defensive_pressure`, `buildup_passes` — variables de contexto originales

**Modelo 2B (clasificación FTR):**
- `implied_prob_h/d/a` — probabilidades implícitas de Bet365 (normalizadas)
- `xg_form_diff` — diferencial de xG en forma reciente (ventana 5 partidos)
- `points_form_diff` — diferencial de puntos en forma reciente
- `home_strength_rating` — rating de fortaleza del equipo local

---

## 📂 Estructura del Repositorio

```
Analisis_Apuestas_Futbol_modelos/
│
├── notebooks/
│   ├── 01_EDA_y_Modelo1_xG.ipynb          # EDA + Modelo xG (Expected Goals)
│   └── 02_EDA_y_Modelos2_Partido.ipynb    # EDA + Modelos de partido (2A y 2B)
│
├── scripts/                               # Pipeline modular de Python
│   ├── 01_build_features_modelo1.py
│   ├── 02_train_modelo1.py
│   ├── 03_build_features_modelo2.py
│   ├── 04_train_modelo2.py
│   ├── 05_bonus_modelos_avanzados.py
│   ├── 06_bonus_clustering.py
│   └── 07_inference_models.py
│
├── data/
│   ├── raw/                               # Datos crudos (no versionados — ver .gitignore)
│   ├── processed/                         # Features procesados
│   └── outputs/                           # Métricas JSON y CSVs de resultados
│
├── models/                                # Modelos entrenados (.joblib)
│   ├── modelo1_xg.joblib
│   ├── modelo2a_regresion.joblib
│   └── modelo2b_clasificacion.joblib
│
├── pagina_web/                            # Dashboard interactivo
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── graficas/                          # PNGs pre-renderizados
│
├── informes/                              # Documentación técnica por modelo
├── generate_charts.py                     # Script para regenerar gráficas estáticas
├── requirements.txt
└── README.md
```

---

## 🚀 Instrucciones para ejecutar los Notebooks

### 1. Clonar el repositorio

```bash
git clone https://github.com/Camilodev-DC/Analisis_Apuestas_Futbol_modelos.git
cd Analisis_Apuestas_Futbol_modelos
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Colocar los datos crudos

> ⚠️ Los datos crudos **no están versionados** por tamaño. Debes colocar los archivos en `data/raw/`:
> - `events.csv` — eventos de tiro por partido
> - `matches.csv` — resultados y cuotas Bet365

### 4. Ejecutar los notebooks

```bash
jupyter notebook
```

Abrir en este orden:
1. `notebooks/01_EDA_y_Modelo1_xG.ipynb`
2. `notebooks/02_EDA_y_Modelos2_Partido.ipynb`

### 5. (Opcional) Ejecutar el pipeline de scripts

```bash
# Desde la raíz del proyecto
python scripts/01_build_features_modelo1.py
python scripts/02_train_modelo1.py
python scripts/03_build_features_modelo2.py
python scripts/04_train_modelo2.py
python scripts/05_bonus_modelos_avanzados.py
python generate_charts.py
```

---

## 🎯 Resultados clave

### ¿Nuestro modelo le gana a Bet365?
**Sí.** Modelo 2B (Logístico Multinomial): **50.87%** de Accuracy vs Bet365: **50.43%**.  
La clave fue combinar probabilidades implícitas con `xg_form_diff`.

### ¿Qué tan confiable es el xG?
**AUC-ROC: 0.7813** (objetivo: > 0.78 ✅) y calibración ratio **1.05x** (casi perfecta).

---

*Taller 2 — Machine Learning I — Universidad Externado de Colombia*
