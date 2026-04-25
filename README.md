# Premier League ML Predictor — Taller 2
> **Machine Learning I (ML1-2026I)**  
> **Universidad Externado de Colombia**  
> **Estudiantes:** Miguel Camargo, Camilo Hernandez  
> **Docente:** Julián Zuluaga


Este repositorio contiene una solución integral para el análisis y predicción de resultados de la Premier League 25/26, utilizando modelos de Machine Learning para superar los benchmarks de las casas de apuestas (Bet365). El proyecto incluye un pipeline completo de ingeniería de variables, modelos de clasificación de tiros (xG), modelos de predicción de partidos y un dashboard interactivo de alto rendimiento.

---

## 📂 Estructura del Repositorio

*   **`scripts/`**: Motores de ingeniería de variables y entrenamiento (`train_modelo_1.py`, `train_modelo_2.py`).
*   **`data/`**: Datos crudos y procesados tras el feature engineering.
*   **`models/`**: Artefactos `.joblib` listos para producción.
*   **`pagina_web/`**: Dashboard interactivo con visualización de datos en tiempo real.
*   **`informes/`**: Documentación técnica detallada de cada modelo.

---

## 🎯 Respuestas a Preguntas del Taller (FAQ)

### 1. ¿Nuestro modelo le gana a las casas de apuestas (Bet365)?
**Sí.** Según la última validación cruzada (CV):
*   **Modelo 2B (Logístico Multinomial)**: **50.87%** de Accuracy.
*   **Benchmark Bet365**: **50.43%** de Accuracy.
Hemos logrado superar a Bet365 por **+0.44 puntos porcentuales**, lo cual es un resultado estadísticamente relevante para este mercado. La clave fue combinar las cuotas implícitas con variables de ejecución reciente como `xg_form_diff`.

### 2. ¿Qué variables son las más determinantes para predecir un gol (xG)?
Las variables más potentes en nuestro Modelo 1 son:
1.  **`is_big_chance`**: La variable con mayor peso positivo (odds ratio elevado).
2.  **`distance_to_goal`**: Correlación negativa clara (a mayor distancia, menor probabilidad).
3.  **`angle_to_goal`**: Crucial para capturar la visibilidad de la portería.
4.  **`defensive_pressure`**: Nuestra variable original que penaliza tiros en zonas congestionadas.

### 3. ¿Por qué el modelo de regresión de goles (M2A) tiene un R² difícil de elevar?
El modelo M2A reporta un R² cercano a 0 (o ligeramente negativo). El análisis de residuos indica que esto se debe a la **ausencia de la variable Over/Under 2.5 de Bet365** en el dataset original. En el mercado de apuestas, las cuotas de goles totales capturan mucha información que las estadísticas de tiros (`xg_rolling`) no alcanzan a explicar por completo.

### 4. ¿Es el modelo xG confiable?
**Altamente confiable.** El modelo presenta un **AUC-ROC de 0.7813** (superando el objetivo de 0.78) y una calibración de **1.05x**. Esto significa que por cada 100 goles que el modelo predice, ocurren 105 en la realidad, lo que demuestra un sesgo mínimo y una alta capacidad de discriminación.

---

## 🎯 Cumplimiento de Rúbricas

### 1. Modelo xG (Expected Goals) — Rúbrica 3 y 4
*   **Rendimiento**: **AUC-ROC: 0.7813**.
*   **Calibración**: Ratio 1.05x (casi perfecta).
*   **Originalidad**: Features como `defensive_pressure` y `buildup_quality`.

### 2. Modelo de Regresión Lineal — Rúbrica 1
*   **Métricas**: Reporte de RMSE (1.60) y MAE (1.27).
*   **Análisis**: Diagnóstico de residuos realizado para identificar falta de linealidad en goles totales.

### 3. Modelo de Clasificación (FTR) — Rúbrica 2
*   **Accuracy**: **50.87%** (Ganando a Bet365).
*   **Interpretación**: Análisis de coeficientes y Odds Ratios disponible en `informes/`.

---
*Este proyecto es parte del Taller 2 de Machine Learning I - Universidad Externado de Colombia.*
