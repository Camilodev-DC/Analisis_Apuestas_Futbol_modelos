# Resumen del Proyecto — ML Premier League 25/26
> **Curso:** Machine Learning I (ML1-2026I) — Universidad Externado de Colombia  
> **Docente:** Julián Zuluaga  
> **Taller:** Taller 2 — *¿Puedes Predecir el Fútbol Mejor que las Casas de Apuestas?*  
> **Fecha de corte:** 22 de abril 2026

---

## 1. Estado del Pipeline

```
events.csv ──[xG por tiro]──▶ Modelo 1 (xG logístico)
                                       │
                               xg_per_match rolling
                                       │
matches.csv ──[feature eng]──▶ Modelo 2A (regresión total_goals)
                              ▶ Modelo 2B (logística ftr: H/D/A)
                                       │
                               pagina_web/ (contenido listo, UI pendiente)
```

---

## 2. Lo que está bien — No tocar

### Modelo 1 — xG (Expected Goals)
| Aspecto | Estado | Detalle |
|---|---|---|
| **AUC-ROC** | ✅ **0.7813** | Supera el benchmark del taller (0.78) |
| **Calibración** | ✅ Excelente | xG medio predicho 11.18% vs tasa real 10.62% (1.05x) |
| **Leakage** | ✅ Sin leakage | Split temporal por `match_date`, sin usar stats post-tiro |
| **VIF** | ✅ OK | Máximo VIF = 4.15 (por debajo del umbral crítico de 5) |
| **Variante elegida** | ✅ Correcta | `unweighted` descartó `balanced` que inflaba xG 3.7x |
| **Features originales** | ✅ 6 originales | `defensive_pressure`, `buildup_passes`, `buildup_unique_players`, `buildup_decentralized`, `ppda`, `pass_decentralization` |

**Features del modelo 1 actuales (8):**
`distance_to_goal`, `angle_to_goal`, `is_big_chance`, `defensive_pressure`, `buildup_passes`, `buildup_unique_players`, `buildup_decentralized`, `first_touch`

---

### Modelo 2 — Predictor de Partido
| Aspecto | Estado | Detalle |
|---|---|---|
| **Validación temporal** | ✅ Correcta | `TimeSeriesSplit` con 5 folds, sin mezclar futuro con pasado |
| **Sin leakage** | ✅ Cumple | Solo usa información pre-partido (rolling averages, odds, árbitro) |
| **Benchmarking** | ✅ Implementado | Comparación directa vs Bet365 en cada fold |
| **Features construidas** | ✅ 45 features | Cobertura amplia: forma, fuerza, árbitro, odds, xG rolling |
| **Clasificación ftr** | ✅ Funcional | Accuracy CV 49.58% vs Bet365 50.83% (solo 1.25 pp de diferencia) |

---

### Infraestructura y Documentación
| Aspecto | Estado |
|---|---|
| `pagina_web/data/` — CSVs de métricas y predicciones | ✅ Listos |
| `pagina_web/graficas/` — PNGs de ambos modelos | ✅ Listos |
| `pagina_web/informes/` — Markdown completos | ✅ Listos |
| Artefactos `.joblib` de ambos modelos | ✅ Guardados |
| EDA de las 4 fuentes de datos | ✅ Completo |
| Diccionario de datos | ✅ Documentado |

---

## 3. Lo que debe cambiar — Prioridades de mejora

### Modelo 1 — Variables faltantes (todas existen en `features_modelo1_a_j.csv`)

| Variable | Impacto esperado | Evidencia |
|---|---|---|
| **`is_penalty`** | 🔴 CRÍTICO | Tasa de gol: **82.9%** vs 10.4% resto — es la mayor brecha del dataset |
| **`shot_quality_index`** | 🔴 Alto | Correlación con `is_goal` = **0.336** (la más alta de todas las features disponibles) |
| **`is_in_area`** | 🟠 Medio-Alto | Dentro del área: **13.8%** vs fuera: **5.9%** de conversión |
| **`is_central`** | 🟠 Medio-Alto | Central: **12.6%** vs no central: **4.1%** |
| **`dist_angle`** | 🟡 Medio | Interacción distancia×ángulo: corr = -0.154 (captura no-linealidad) |
| **`is_volley`** | 🟡 Medio | Voleas: 9.3% vs normal: 11.5% — diferencia que ayuda a discriminar |
| **`is_set_piece`** | 🟡 Medio | Set pieces: 7.3% vs dinámico: 11.5% |
| **`is_counter`** | 🟡 Leve | Contraataque: 13.3% vs 11.1% — señal pequeña pero real |

> **Nota sobre decisión previa:** El reporte actual justifica excluir `is_penalty`, `is_in_area`, `is_central` y `dist_angle` por VIF y redundancia con geometría. Esa justificación es parcialmente válida para las variables geométricas (`dist_angle`), pero **no aplica a `is_penalty`** (que es un caso cualitativamente distinto) ni a `shot_quality_index` (que es un índice compuesto, no redundante). Revisar esa decisión.

---

### Modelo 2A — Regresión `total_goals` (R² = -0.034)

**Problema raíz:** Las 3 features de árbitro tienen correlaciones ≤ 0.06 con `total_goals`. El modelo no supera predecir la media.

**Variables que mejorarían (ya existen en `features_modelo_2.csv`):**

| Variable | Correlación con `total_goals` | Acción |
|---|---|---|
| `home_xg_for_avg5` + `away_xg_for_avg5` | ~0.04 c/u (suma: ~0.10) | Sumar como `expected_total_xg = home_xg + away_xg` |
| `home_sot_for_avg5` + `away_sot_for_avg5` | 0.055 c/u | Incluir como features directas |
| `bookmaker_spread_draw` | 0.100 | Ya está en el CSV — no se está usando para regresión |
| `implied_prob_d` | -0.087 | Menor prob. de empate → más goles |
| `away_strength_rating` | 0.076 | Incluir |

**Variables que NO existen pero serían las más poderosas:**
- Cuotas Over/Under 2.5 goles (`b365_over25`, `bwover25`) — disponibles en football-data.co.uk pero no descargadas. Estas serían la mejor feature por mucho para regresión de goles.

**Techo realista con datos actuales:** R² ≈ 0.05–0.10.  
**Techo con cuotas Over/Under:** R² ≈ 0.25–0.35.

---

### Modelo 2B — Clasificación `ftr` (Accuracy 49.58%)

**Problema:** La búsqueda de features probó bloques independientemente, nunca combinados.

**Combinación recomendada:** `odds (7 features)` + estas variables adicionales del CSV:

| Variable a añadir | Justificación |
|---|---|
| `xg_form_diff` | xG diferencial rolling — complementa cuotas con ejecución reciente |
| `points_form_diff` | Forma reciente explícita en puntos |
| `big_chances_diff` | Diferencial de ocasiones claras (las más ligadas a goles) |
| `home_strength_rating` | Rating absoluto del local (las cuotas ya lo capturan parcialmente, pero el rating es explícito) |

**Ganancia estimada:** 51–52% accuracy (superaría Bet365).

---

### Página Web — Pendiente de desarrollo

| Componente | Estado |
|---|---|
| Contenido (datos, gráficas, informes) | ✅ Listo en `pagina_web/` |
| HTML/CSS/JS o Streamlit | ❌ No existe |
| Deploy (Vercel/Netlify/Streamlit Cloud) | ❌ No existe |

La carpeta `pagina_web/` es un repositorio de contenido estático. La interfaz visual está pendiente.

---

## 4. Guía de Rúbricas del Taller 2

### Rúbrica 1 — Modelo de Regresión Lineal

**Objetivo del taller:** Predecir goles (ya sea `fthg` o `total_goals`).

| Criterio | Estado actual | Acción necesaria |
|---|---|---|
| Modelo implementado | ✅ Regresión lineal para `total_goals` | — |
| Features usadas | ⚠️ Solo 3 features de árbitro | Cambiar a features de rendimiento (xG, SOT rolling) |
| Métricas reportadas (R², RMSE, MAE) | ✅ RMSE=1.60, MAE=1.27, R²=-0.034 | — |
| Análisis de residuos | ✅ `regression_residuals.png` | — |
| **R² positivo** | ❌ R²=-0.034 | Cambiar features → objetivo R²>0.10 |
| Interpretación de coeficientes | ⚠️ Hecha para árbitro | Re-hacer con nuevas features |

**Pasos concretos:**
1. En `build_features_modelo_2.py` — añadir `expected_total_xg = home_xg_for_avg5 + away_xg_for_avg5`
2. En `train_modelo_2.py` — cambiar `feature_blocks["regression"]` por: `home_xg_for_avg5`, `away_xg_for_avg5`, `home_sot_for_avg5`, `away_sot_for_avg5`, `bookmaker_spread_draw`, `implied_prob_d`
3. Re-correr `train_modelo_2.py`

---

### Rúbrica 2 — Modelo de Regresión Logística Multiclase

**Objetivo del taller:** Predecir resultado `ftr` (H/D/A) y comparar con Bet365.

| Criterio | Estado actual | Acción necesaria |
|---|---|---|
| Modelo multiclase implementado | ✅ LogisticRegression multiclase | — |
| Probabilidades implícitas de odds | ✅ `implied_prob_h/d/a` | — |
| Matriz de confusión | ✅ `confusion_matrix_multiclass.png` | — |
| Accuracy reportada | ✅ 49.58% CV | — |
| Benchmarking vs Bet365 | ✅ `accuracy_vs_bet365.png` | — |
| **Superar a Bet365** | ❌ 49.58% < 50.83% | Añadir `xg_form_diff`, `points_form_diff`, `big_chances_diff` |
| Odds Ratios / Coeficientes | ✅ `multiclass_coefficients.csv` | — |
| F1-macro por clase | ✅ 0.377 promedio | Mejoraría con nuevas features |

**Pasos concretos:**
1. En `train_modelo_2.py` — añadir al bloque `odds`: `xg_form_diff`, `points_form_diff`, `big_chances_diff`
2. Re-correr búsqueda de features (`feature_search`) con bloque combinado `odds_plus_form`
3. Reportar si el bloque combinado supera el bloque puro de odds

---

### Rúbrica 3 — Modelo xG (Modelo 1)

**Objetivo del taller:** xG logístico con features geométricas + originales, AUC > 0.78.

| Criterio | Estado actual | Acción necesaria |
|---|---|---|
| AUC-ROC > 0.78 | ✅ **0.7813** | — |
| Features geométricas obligatorias | ✅ `distance_to_goal`, `angle_to_goal` | — |
| Features originales (≥3) | ✅ 6 originales | — |
| VIF < 5 | ✅ Max 4.15 | — |
| Calibración xG | ✅ 1.05x (casi perfecta) | — |
| **`is_penalty` incluido** | ❌ Falta (82.9% conversión) | Añadir al modelo |
| **AUC > 0.83** | ⚠️ Potencial si se añaden features clave | Añadir `is_penalty`, `shot_quality_index`, `is_in_area` |
| Brier Score reportado | ✅ 0.0733 | — |
| Log Loss reportado | ✅ 0.2599 | — |

**Pasos concretos:**
1. En `train_modelo_1.py` — añadir al feature list: `is_penalty`, `shot_quality_index`, `is_in_area`, `is_central`
2. Re-correr con VIF check (estos no deberían elevar VIF significativamente)
3. Re-correr comparación de variantes

---

### Rúbrica 4 — Feature Engineering Original

| Criterio | Estado actual |
|---|---|
| Features geométricas estándar | ✅ `distance_to_goal`, `angle_to_goal`, `dist_squared`, `dist_angle`, `is_in_area`, `is_central` |
| Features de qualifiers | ✅ `is_big_chance`, `is_header`, `is_penalty`, `is_volley`, `first_touch`, `is_set_piece`, `from_corner`, `is_counter`, `is_right_foot`, `is_left_foot` |
| Feature original A — Defensive Pressure | ✅ `defensive_pressure` — proxy de freeze_frame sin StatsBomb |
| Feature original B — Buildup Quality | ✅ `buildup_passes`, `buildup_unique_players`, `buildup_decentralized` |
| Feature original C — Portería Zone | ✅ `porteria_zone` + 9 dummies (3×3 grid) |
| Feature original D — xG Debt | ✅ `home_xg_debt_5` |
| Feature original E — PPDA Proxy | ✅ `ppda` |
| Feature original F — Pass Decentralization | ✅ `pass_decentralization` |
| Shot Quality Index compuesto | ✅ `shot_quality_index` |

Esta rúbrica está bien cubierta. No requiere cambios.

---

### Rúbrica 5 — Validación y Metodología

| Criterio | Estado actual |
|---|---|
| Sin leakage | ✅ Solo features pre-partido en M2, sin stats post-tiro en M1 |
| Split temporal M1 | ✅ `train_test_split` por `match_date` (80/20) |
| TimeSeriesSplit M2 | ✅ 5 folds, orden temporal preservado |
| Comparación de subsets de features | ✅ `feature_search_summary.md` documenta todos los bloques |
| Análisis VIF | ✅ Reportado en ambos modelos |
| Interpretación futbolística | ✅ Coeficientes interpretados en contexto táctico |

Esta rúbrica está bien cubierta. No requiere cambios.

---

### Rúbrica 6 — Dashboard / Página Web

| Criterio | Estado actual | Acción necesaria |
|---|---|---|
| Contenido organizado | ✅ `pagina_web/` con datos, gráficas e informes | — |
| Interfaz visual (HTML/Streamlit) | ❌ No existe | **Desarrollar la UI** |
| Deploy público (URL accesible) | ❌ No existe | Deploy en Vercel, Netlify o Streamlit Cloud |
| Visualización de predicciones | ❌ No existe | Mostrar predicciones M1 y M2 en pantalla |
| Comparación vs Bet365 visual | ❌ No existe | Incluir gráfico interactivo |

**Esta rúbrica es la más incompleta. Es la que más trabajo requiere.**

---

## 5. Checklist de inicio para la próxima sesión

### Cambios de alta prioridad (impacto en rúbricas)

- [ ] **M1:** Añadir `is_penalty` al feature set de `train_modelo_1.py`
- [ ] **M1:** Añadir `shot_quality_index`, `is_in_area`, `is_central` y evaluar AUC
- [ ] **M2A:** Cambiar features de regresión: reemplazar bloque `referee` por `xG+SOT rolling`
- [ ] **M2B:** Probar bloque combinado `odds + xg_form_diff + points_form_diff + big_chances_diff`
- [ ] **Web:** Crear `pagina_web/index.html` o `app.py` (Streamlit) con visualización básica

### Cambios de media prioridad (mejoras)

- [ ] **M2A:** Descargar cuotas Over/Under 2.5 de football-data.co.uk y añadir al dataset
- [ ] **M1:** Probar `is_volley`, `is_set_piece`, `is_counter` como features adicionales
- [ ] **Web:** Deploy en Streamlit Cloud (gratuito, no requiere dominio)

### No cambiar (está funcionando bien)

- Pipeline de feature engineering completo en `data/processed/`
- Validación temporal (`TimeSeriesSplit`) de M2
- Estructura de `pagina_web/` (contenido listo)
- Artefactos `.joblib` y reportes generados
- Features originales del taller (A–F) — todas documentadas y cumplidas

---

## 6. Métricas actuales vs objetivos

| Modelo | Métrica | Valor actual | Objetivo taller | Estado |
|---|---|---|---|---|
| M1 xG | AUC-ROC | 0.7813 | > 0.78 | ✅ Cumple |
| M1 xG | AUC-ROC con mejoras | — | > 0.83 | ⬜ Potencial |
| M2A Regresión | R² CV | -0.034 | > 0 | ❌ Falla |
| M2A Regresión | RMSE CV | 1.608 | Minimizar | ⚠️ Alto |
| M2B Clasificación | Accuracy CV | 49.58% | > Bet365 (50.83%) | ❌ Por debajo |
| M2B Clasificación | Accuracy con mejoras | — | > 51% | ⬜ Potencial |
| Web | Deploy público | No existe | URL accesible | ❌ Pendiente |
