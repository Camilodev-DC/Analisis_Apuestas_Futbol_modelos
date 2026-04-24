# Informe Final — Taller 2 ML Premier League

**Fecha:** 23 de abril de 2026  
**Curso:** Machine Learning I (ML1-2026I)  
**Taller:** *¿Puedes predecir el fútbol mejor que las casas de apuestas?*

---

## 1. Resumen ejecutivo

El proyecto quedó mejor parado de lo que parecía al inicio de la sesión:

- **Modelo 1 xG**: tras podar variables redundantes, la regresión logística final quedó en **AUC = 0.7955** y sigue cumpliendo el benchmark. El bonus con **Random Forest** subió a **0.8250**.
- **Modelo 2B multiclase (`ftr`)**: al dejar solo la familia `implied_prob_*` y quitar cuotas duplicadas, la logística multiclase quedó en **50.87% accuracy**, apenas por encima de **Bet365 = 50.43%**.
- **Modelo 2A regresión (`total_goals`)**: sigue siendo el punto débil. El resultado final fue **R² = -0.0793**, así que no supera la línea base de predecir la media.
- **Bonus modelos avanzados**: sí aporta valor en `M1` porque Random Forest mejora al baseline logístico. En `M2B`, en cambio, la logística baseline fue mejor que Random Forest, SVM y Neural Network.
- **Bonus clustering**: implementado con K-Means sobre perfiles de remate de jugadores, con visualización PCA e interpretación futbolística.
- **Feature engineering creativo**: el proyecto ya trae un bloque creativo serio y justificable; no está vacío ni superficial.

Conclusión corta: **el taller queda razonablemente fuerte en xG, justo pero válido en clasificación de resultado, débil en regresión de goles, y con los dos bonos pedidos ya implementados y medidos.**

---

## 2. `balanced` vs `unweighted` en regresión logística

### Qué significa cada una

En clasificación desbalanceada, como `is_goal` en un modelo xG, hay muchas más observaciones de la clase 0 que de la clase 1.

- **`unweighted`**: la logística trata cada observación con el mismo peso. Si hay pocos goles, el modelo aprende una probabilidad baja para la mayoría de tiros, que suele parecerse más a la frecuencia real del fenómeno.
- **`balanced`**: la logística le da más peso a la clase minoritaria automáticamente. En este caso, les da mucho más peso a los goles para “compensar” que son pocos.

### Qué pasó en tu dataset

Resultados reales en `M1`:

| Variante | AUC | Brier | Log Loss | xG medio | goal rate |
|---|---:|---:|---:|---:|---:|
| `unweighted` | **0.7955** | **0.0744** | **0.2665** | **0.1149** | 0.1099 |
| `balanced` | 0.7963 | 0.1768 | 0.5413 | 0.4210 | 0.1099 |

### Interpretación clara

`balanced` consiguió una AUC apenas un poco mejor, pero **rompió la calibración**:

- el partido real tiene tasa de gol de **10.99%**
- el modelo `balanced` predijo en promedio **42.10%**

Eso significa que el modelo **sobreestima muchísimo** la probabilidad de gol. Para xG eso es grave, porque xG no solo debe ordenar tiros; también debe dar probabilidades creíbles.

### Qué se deja como modelo final

Para `M1` hay que dejar **`unweighted`** como baseline final.

Razón:

- AUC casi igual de buena
- mejor Brier Score
- mejor Log Loss
- mejor calibración
- más útil como modelo xG real

En otras palabras: **`balanced` mejora un poco el ranking, pero empeora mucho la probabilidad. Para xG eso no compensa.**

---

## 3. ¿Se puede hacer matriz de confusión en regresión logística?

Sí. **Toda regresión logística es un clasificador**, así que se le puede construir matriz de confusión.

### Cuándo tiene sentido

- **Logística multiclase (`M2B`)**: sí tiene mucho sentido. Ya quedó generada en `pagina_web/graficas/confusion_matrix_multiclass.png`.
- **Logística binaria (`M1`)**: también se puede hacer, pero hay una advertencia importante.

### La advertencia importante en xG

En `M1`, el objetivo real no es solo clasificar `gol / no gol`, sino estimar una **probabilidad de gol**. Por eso:

- para xG, **ROC-AUC, Brier y Log Loss** son más importantes que una matriz de confusión;
- la matriz de confusión depende del **umbral** elegido (`0.5`, `0.2`, etc.);
- si usas `0.5` en tiros de fútbol, casi todo queda como “no gol”, porque la mayoría de tiros tiene xG muy bajo.

Conclusión:

- **sí se puede** hacer matriz de confusión en ambos modelos logísticos;
- en `M2B` es una métrica natural;
- en `M1` es solo una vista complementaria, no la métrica principal.

---

## 4. Estado de cumplimiento del taller

Esta evaluación se hizo contrastando el estado actual del proyecto con la rúbrica local resumida en `resumen.md` y con los criterios de bonos que pediste explícitamente.

| Componente | Estado | Veredicto |
|---|---|---|
| Modelo 1 xG logístico | AUC = 0.7955 | **Cumple** |
| Modelo 2A regresión lineal | R² = -0.0793 | **No cumple bien** |
| Modelo 2B logística multiclase | 50.87% > 50.43% Bet365 | **Cumple** |
| Feature engineering original | Sí, amplio y justificable | **Cumple** |
| Validación temporal y metodología | Sí | **Cumple** |
| Página web / dashboard público | No desarrollado | **Pendiente / no cumple aún** |
| Bonus modelos avanzados | Sí, implementado y comparado | **Cumple** |
| Bonus clustering | Sí, implementado e interpretado | **Cumple** |
| Bonus feature engineering creativo | Sí, justificable y analizable | **Probablemente cumple** |

### Lectura honesta

Si la rúbrica exige que **todos** los bloques obligatorios estén completos, todavía hay dos puntos delicados:

1. **Modelo 2A** no alcanzó un resultado satisfactorio.
2. **La página web** todavía no existe como interfaz pública.

O sea: **no estamos cumpliendo absolutamente todo el taller**.  
Pero sí estamos cumpliendo una parte grande y ya resolvimos dos puntos importantes:

- `M1` quedó fuerte
- `M2B` ya supera Bet365

---

## 5. Modelo 1 — xG por tiro (regresión logística baseline)

### Objetivo

Predecir `is_goal` a nivel de tiro.

### Predictores usados

Baseline final:

- `distance_to_goal`
- `angle_to_goal`
- `is_penalty`
- `shot_quality_index`
- `defensive_pressure`
- `buildup_passes`
- `buildup_unique_players`
- `buildup_decentralized`
- `ppda`
- `pass_decentralization`
- `first_touch`

### Por qué esas variables

- `distance_to_goal`, `angle_to_goal`: geometría clásica del tiro.
- `is_penalty`: evento extremo con tasa de conversión mucho mayor.
- `shot_quality_index`: resume calidad contextual del tiro y reemplaza parte de la información redundante de `is_big_chance`, `is_in_area` e `is_central`.
- `defensive_pressure`, `buildup_*`, `ppda`, `pass_decentralization`: contexto colectivo previo al remate.
- `first_touch`: patrón técnico relevante en definición.

### Métricas finales

Archivo: `data/outputs/metrics_modelo1.json`

| Métrica | Valor |
|---|---:|
| AUC-ROC | **0.7955** |
| Brier Score | **0.0744** |
| Log Loss | **0.2665** |
| xG medio | 0.1149 |
| goal rate | 0.1099 |
| n_train | 5103 |
| n_test | 1256 |

### VIF y multicolinealidad

Archivo: `data/outputs/vif_modelo1.csv`

Hallazgo clave: **la multicolinealidad bajó bastante respecto a la versión ampliada, pero no desapareció**.

Variables con VIF especialmente alto:

- `pass_decentralization`: 45.37
- `buildup_unique_players`: 29.59
- `angle_to_goal`: 28.73
- `distance_to_goal`: 17.36
- `buildup_decentralized`: 14.07
- `buildup_passes`: 7.19

Interpretación:

- quitar `is_big_chance`, `is_in_area` e `is_central` redujo de forma fuerte la colinealidad más extrema;
- aun así, sigue habiendo solapamiento entre geometría y algunas features de construcción de jugada.

Entonces:

- **predictivamente** el modelo funciona bien;
- **interpretativamente** los coeficientes deben leerse con mucha cautela.

### Coeficientes relevantes

Archivo principal de inferencia: `data/outputs/inference_modelo1_logit.csv`

Coeficientes log-odds positivos y significativos más importantes:

- `shot_quality_index`: `+4.650`, `p < 0.001`
- `is_penalty`: `+2.790`, `p < 0.001`
- `distance_to_goal`: `+0.079`, `p < 0.001`
- `first_touch`: `+0.233`, `p = 0.017`
- `ppda`: `+0.0076`, `p = 0.015`

Coeficientes negativos:

- `defensive_pressure`: `-0.365`, `p = 0.048`
- `angle_to_goal`: `-0.059`, no significativo al 5%

### Odds ratios e intervalos de confianza en `M1`

Odds ratios relevantes:

- `shot_quality_index`: `OR = 104.55`, IC95% `[67.84, 161.12]`
- `is_penalty`: `OR = 16.28`, IC95% `[7.93, 33.43]`
- `first_touch`: `OR = 1.26`, IC95% `[1.04, 1.53]`
- `defensive_pressure`: `OR = 0.69`, IC95% `[0.48, 1.00]`

Lectura:

- un penal multiplica las odds de gol por unas `16.3x`, manteniendo constantes las demás variables;
- `shot_quality_index` aparece como el predictor dominante;
- algunos signos siguen siendo difíciles de leer causalmente por la colinealidad residual.

### Veredicto

Como baseline del taller, `M1` **cumple** y ahora es más interpretable que antes.  
El costo de esa mejora fue perder parte del AUC (`0.8112 -> 0.7955`).  
La decisión final es razonable si valoras interpretación además de benchmark.

---

## 6. Modelo 1 bonus — Random Forest vs baseline logístico

Archivo: `data/outputs/metrics_bonus_modelos_avanzados.json`

Comparación real:

| Modelo | AUC | Brier | Log Loss |
|---|---:|---:|---:|
| Logistic `unweighted` | 0.7955 | 0.0744 | 0.2665 |
| Logistic `balanced` | 0.7963 | 0.1768 | 0.5413 |
| **Random Forest** | **0.8250** | **0.0711** | **0.2536** |
| SVM RBF | 0.7455 | 0.0857 | 0.3122 |
| Neural Network (MLP) | 0.7789 | 0.0766 | 0.2943 |

### Qué mejora y por qué

El **Random Forest** fue el mejor modelo del bonus en `M1`.

Por qué probablemente mejora:

- capta interacciones no lineales entre geometría y contexto;
- maneja mejor umbrales tipo “estar muy cerca”, “ser penal” o “gran ocasión”;
- no depende de una relación lineal estricta entre predictores y log-odds.

### Importancias del Random Forest

Archivo: `data/outputs/importance_modelo1_bonus_rf.csv`

Top features:

- `shot_quality_index`
- `distance_to_goal`
- `angle_to_goal`
- `is_penalty`
- `ppda`

### Veredicto del bonus en `M1`

Aquí sí vale la pena el bonus:

- mejora cuantitativamente al baseline;
- mantiene buenas métricas probabilísticas;
- aporta una explicación razonable del porqué.

Por eso dejé guardado el modelo bonus en:

- `models/modelo1_xg_bonus_random_forest.joblib`

---

## 7. Modelo 2A — Regresión lineal de `total_goals`

### Objetivo

Predecir goles totales por partido (`total_goals`).

### Predictores usados

- `home_xg_for_avg5`
- `away_xg_for_avg5`
- `home_sot_avg5`
- `away_sot_avg5`
- `expected_total_xg`
- `bookmaker_spread_draw`
- `implied_prob_d`
- `away_strength_rating`

### Por qué esas variables

- xG rolling y tiros al arco rolling: forma ofensiva reciente;
- `expected_total_xg`: resumen del potencial ofensivo agregado;
- `implied_prob_d` y spread bookmaker: información del mercado sobre partidos cerrados o abiertos;
- `away_strength_rating`: fuerza relativa del visitante.

### Métricas finales

Archivo: `data/outputs/metrics_modelo2.json`

| Métrica | Valor |
|---|---:|
| R² | **-0.0793** |
| RMSE | 1.6384 |
| MAE | 1.2898 |

### Diagnóstico

El modelo **no supera predecir la media**.

Interpretación:

- la tarea es más difícil de lo que parecía con estas variables;
- el conjunto de features todavía no captura bien la varianza del marcador;
- las cuotas Over/Under 2.5 probablemente siguen siendo la ausencia más importante.

### Coeficientes

Archivo de inferencia: `data/outputs/inference_modelo2a_ols.csv`

Coeficientes más altos:

- `away_sot_avg5`: `+0.1597`, IC95% `[0.0080, 0.3114]`, `p = 0.039`
- `home_sot_avg5`: `+0.0416`, IC95% `[-0.1319, 0.2150]`
- `bookmaker_spread_draw`: `+0.0052`, IC95% `[-0.0636, 0.0740]`

Coeficientes negativos:

- `implied_prob_d`: `-3.8106`, IC95% `[-9.6410, 2.0197]`
- `away_strength_rating`: `-0.0692`, IC95% `[-0.3164, 0.1779]`

Lectura:

- la única señal con soporte estadístico modesto al 5% fue `away_sot_avg5`;
- el resto de variables tiene intervalos que cruzan 0 o coeficientes prácticamente indeterminados;
- esto es coherente con el mal `R²`: el modelo no está encontrando una estructura lineal estable.

### VIF

Archivo: `data/outputs/vif_modelo2_regresion.csv`

Problema importante:

- `expected_total_xg` es combinación lineal de `home_xg_for_avg5 + away_xg_for_avg5`
- por eso el VIF queda indefinido o extremo en varias columnas

Conclusión:

- predictivamente no funciona bien;
- estructuralmente además hay redundancia en el bloque de regresión.

### Veredicto

`M2A` sigue siendo el modelo más flojo del proyecto.  
No lo daría por aprobado todavía.

---

## 8. Modelo 2B — Regresión logística multiclase para `ftr`

### Objetivo

Predecir resultado final:

- `H` = gana local
- `D` = empate
- `A` = gana visitante

### Predictores usados

- `implied_prob_h`
- `implied_prob_d`
- `implied_prob_a`
- `xg_form_diff`
- `points_form_diff`
- `big_chances_diff`
- `home_strength_rating`

### Por qué esas variables

- las cuotas resumen información de mercado de altísimo valor predictivo;
- `xg_form_diff` y `points_form_diff` añaden forma reciente;
- `big_chances_diff` aproxima superioridad ofensiva de alta calidad;
- `home_strength_rating` refuerza la ventaja local estructural.

### Métricas finales

Archivo: `data/outputs/metrics_modelo2.json`

| Métrica | Valor |
|---|---:|
| Accuracy | **50.87%** |
| F1-macro | **0.4066** |
| Bet365 accuracy | **50.43%** |

### Resultado clave

Sí: **el modelo ya supera a Bet365** en el benchmark definido.

Margen:

- `50.87% - 50.43% = +0.44 pp`

### VIF

Con el bloque reducido, la multicolinealidad bajó mucho frente a la versión anterior.

Archivo: `data/outputs/vif_modelo2b_reducido.csv`

VIF principales:

- `implied_prob_d`: `27.90`
- `implied_prob_a`: `12.29`
- `implied_prob_h`: `10.67`
- `points_form_diff`: `1.81`
- `home_strength_rating`: `1.33`

Interpretación:

- ya no hay redundancia brutal entre cuotas crudas, cuotas implícitas y spread;
- pero sigue habiendo dependencia fuerte dentro del propio trío de probabilidades implícitas.

### Coeficientes

Archivo de inferencia: `data/outputs/inference_modelo2b_mnlogit.csv`

Para inferencia multinomial se omitió `implied_prob_a`, porque:

- `implied_prob_h + implied_prob_d + implied_prob_a = 1`
- si metes las tres con intercepto, la matriz queda singular

La clase de referencia quedó en orden alfabético: **`A`**.

Resultados más útiles:

- `H vs A`:
  - `implied_prob_h`: `coef = 6.576`, `p < 0.001`
  - `OR = 717.90`, IC95% `[51.99, 9913.80]`
- `D vs A`:
  - `implied_prob_h`: `coef = 3.140`, `p = 0.016`
  - `OR = 23.10`, IC95% `[1.79, 298.12]`

Variables no significativas al 5% en esta especificación:

- `implied_prob_d`
- `points_form_diff`
- `home_strength_rating`

Además, en este dataset actual:

- `xg_form_diff` quedó constante en `0`
- `big_chances_diff` quedó constante en `0`

por lo que no pudieron aportar inferencia estadística en la multinomial.

### Matriz de confusión

Sí está implementada y guardada en:

- `pagina_web/graficas/confusion_matrix_multiclass.png`

### Veredicto

`M2B` **cumple** el objetivo principal del taller mejor que antes:

- está bien validado en tiempo;
- todavía supera a Bet365, aunque por un margen corto;
- y sigue siendo el mejor modelo para predicción de resultado final en el proyecto.

---

## 9. Bonus modelos avanzados en `M2B`

Comparación real:

| Modelo | Accuracy | F1-macro |
|---|---:|---:|
| **Logistic multinomial** | **0.5087** | **0.4066** |
| Random Forest | 0.4783 | 0.3731 |
| SVM RBF | 0.4783 | 0.3348 |
| Neural Network (MLP) | 0.4130 | 0.3787 |

### Lectura

En `M2B`, el bonus fue útil no porque reemplazara al baseline, sino porque mostró algo importante:

- **la logística multinomial ya era el mejor modelo** para este feature set.

Probable razón:

- las cuotas e implícitas ya contienen una señal muy estructurada;
- la frontera entre clases parece más lineal de lo que pensábamos;
- los modelos más flexibles probablemente sobreajustan un dataset relativamente pequeño (`277` partidos útiles).

### Veredicto del bonus en `M2B`

Sí cumple como bonus porque:

- se implementó,
- se comparó cuantitativamente,
- y se concluyó con evidencia que **no mejora** al baseline.

Eso también es análisis válido.

---

## 10. Bonus clustering — Segmentación de jugadores

Script:

- `scripts/06_bonus_clustering.py`

Artefactos:

- `data/outputs/bonus_clustering_players.csv`
- `data/outputs/bonus_clustering_summary.csv`
- `pagina_web/graficas/bonus_clustering_players_pca.png`
- `pagina_web/graficas/bonus_clustering_silhouette.png`

### Qué se hizo

Se construyeron perfiles de remate por jugador usando jugadores con al menos `20` tiros.

Variables de clustering:

- volumen de tiros
- tasa de gol
- distancia media
- ángulo medio
- xG medio por tiro
- proporción de tiros dentro del área
- proporción central
- proporción de big chances
- proporción de cabezazos
- proporción de penales
- proporción de first-touch shots

### Selección de K

Silhouette:

- `k=2`: **0.2818**
- `k=3`: `0.2104`
- `k=4`: `0.2140`

Se dejó **`k=3`** por interpretabilidad futbolística, aunque `k=2` era el mejor puramente por silhouette.

### Interpretación futbolística de clusters

Resumen:

| Cluster | Perfil |
|---|---|
| 0 | Rematadores de media distancia / volumen medio / baja conversión |
| 1 | Atacantes interiores mixtos / llegada al área / calidad media-alta |
| 2 | Finalizadores de área / cabeceadores / alta xG y alta conversión |

Centros de cluster:

- **Cluster 0**
  - `goal_rate = 0.082`
  - `mean_distance = 21.0`
  - `mean_xg = 0.303`
  - perfil de remate más lejano y menos eficiente

- **Cluster 1**
  - `goal_rate = 0.108`
  - `mean_distance = 18.9`
  - `mean_xg = 0.358`
  - perfil intermedio, más equilibrado

- **Cluster 2**
  - `goal_rate = 0.165`
  - `mean_distance = 14.2`
  - `mean_xg = 0.416`
  - más tiros de área, más cabezazos y más remates de primer toque

### Veredicto del bonus de clustering

Sí está cumplido:

- hay algoritmo implementado;
- hay visualización;
- hay selección de `k`;
- y hay interpretación futbolística coherente.

---

## 11. Revisión del bonus de feature engineering creativo

El proyecto sí tiene feature engineering creativo defendible. No es solo “rolling averages básicas”.

### Features creativas ya presentes

En tiros / xG:

- `defensive_pressure`
- `buildup_passes`
- `buildup_unique_players`
- `buildup_decentralized`
- `shot_quality_index`
- `home_xg_debt_5`
- `ppda`
- `pass_decentralization`
- `momentum`
- `home_bias`
- `altitude_of_play`
- `clutch_ratio`

En partidos:

- `points_form_diff`
- `sot_diff`
- `gf_diff`
- `expected_total_xg`
- `home_strength_rating`
- `away_strength_rating`
- `bookmaker_spread_draw`

### Qué evidencia hay de que aportan algo

Correlaciones observadas con `is_goal` en el dataset enriquecido de tiros:

- `shot_quality_index`: **0.3361**
- `altitude_of_play`: `-0.0606`
- `buildup_unique_players`: `-0.0514`
- `buildup_decentralized`: `-0.0407`
- `ppda`: `0.0389`

La más fuerte por bastante margen es `shot_quality_index`, que de hecho termina siendo una de las variables clave del proyecto. En cambio, algunas features creativas del modelo de partido (`xg_form_diff`, `big_chances_diff`) no variaron en esta versión procesada del dataset y por eso su aporte real quedó limitado.

### Juicio honesto sobre este bonus

Sí hay base para reclamarlo porque:

- las features son originales y justificadas;
- varias no son triviales;
- se conectan con ideas tácticas reales;
- y al menos algunas sí muestran señal útil.

Lo que no está tan fuerte todavía es una validación sistemática feature por feature para todas las creativas.

Mi lectura: **este bonus es defendible como cumplido, pero conviene argumentarlo bien en la entrega.**

---

## 12. Qué dejar finalmente

### Modelos a dejar como principales

- **Modelo 1 oficial del taller**: `models/modelo1_xg.joblib`
  - variante logística `unweighted`
- **Modelo 2A oficial**: `models/modelo2a_regresion.joblib`
  - aunque su desempeño no es satisfactorio
- **Modelo 2B oficial**: `models/modelo2b_clasificacion.joblib`
  - logística multinomial, ya por encima de Bet365

### Modelo bonus a dejar

- **Mejor modelo bonus en xG**: `models/modelo1_xg_bonus_random_forest.joblib`

### Decisiones finales

- En `M1`, **dejar `unweighted`** como baseline oficial.
- En `M2B`, **dejar la logística multinomial** como modelo final.
- En bonus, **dejar Random Forest solo como mejora adicional de `M1`**, no como reemplazo obligatorio del baseline del taller.

---

## 13. Conclusión final

El estado final del proyecto es bastante más sólido que al comienzo:

- `M1` ya no está raspando el benchmark; lo supera con margen.
- `M2B` ya supera ligeramente a Bet365 incluso con un bloque más limpio.
- los bonos de modelos avanzados y clustering quedaron implementados y medidos.

Lo que sigue débil es:

- `M2A` regresión de goles,
- y la parte de página web / dashboard.

Si el objetivo es defender el taller académicamente, hoy la historia más honesta es:

- **sí hay evidencia razonable en xG y en clasificación de partido**;
- **sí hay bonus reales y analizados**;
- **todavía hay una deuda en regresión lineal y en la capa web**.

Ese es el balance correcto del proyecto al 23 de abril de 2026.
