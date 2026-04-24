# Informe Actualizado — Modelo 2A: Regresión `total_goals`

**Fecha:** 23 de abril de 2026  
**Taller:** ML1-2026I — Universidad Externado de Colombia  
**Modelo:** Regresión lineal — target: `total_goals`

---

## Estado real del modelo

El diagnóstico general se mantiene: el Modelo 2A era uno de los puntos débiles del proyecto. Pero el informe anterior quedó viejo porque describía como pendiente una mejora que **ya fue incorporada al script**.

En [scripts/04_train_modelo2.py](/home/camilo/proyectos/Ml_Futbol_Final/scripts/04_train_modelo2.py:44) el bloque de regresión ya usa:

- `home_xg_for_avg5`
- `away_xg_for_avg5`
- `home_sot_avg5`
- `away_sot_avg5`
- `expected_total_xg`
- `bookmaker_spread_draw`
- `implied_prob_d`
- `away_strength_rating`

Eso corrige el problema central del diseño anterior: ya no se entrena con un bloque débil o irrelevante, sino con variables de rendimiento y mercado mucho más razonables.

---

## Métricas confirmadas vs. métricas pendientes

### Último diagnóstico confirmado

El informe histórico describe un modelo previo con:

| Métrica | Valor histórico |
|---------|----------------:|
| R² | -0.034 |
| RMSE | 1.60 |
| MAE | 1.27 |

Ese resultado correspondía a una versión anterior del modelo.

### Estado de la versión actual

La versión nueva del script **aún no tiene métricas regeneradas en este workspace** porque no existe:

- `data/processed/features_modelo2.csv`

Sin ese archivo, no puede producirse el nuevo `metrics_modelo2.json` ni validarse si el R² ya pasó a positivo.

---

## Lo que sí mejoró

### El feature set ahora sí está alineado con la tarea

La regresión de goles necesita señales de producción ofensiva esperada y contexto de mercado. El script actual ya refleja esa lógica.

### `expected_total_xg` ya está contemplada

Antes se criticaba que esta variable obvia no existía. En el código de entrenamiento actual ya se espera explícitamente como parte del bloque de regresión.

### La metodología sigue siendo correcta

`TimeSeriesSplit`, separación temporal y métricas CV siguen siendo decisiones adecuadas para este problema.

---

## Lo que sigue pendiente

### Confirmar si la mejora fue suficiente

El cambio más importante ya se hizo en código, pero aún falta responder con datos:

- si `R²` ya es positivo,
- cuánto bajó el `RMSE`,
- y si el modelo por fin supera la línea base trivial.

### Verificar consistencia de nombres de columnas

El script actual espera `home_sot_avg5` y `away_sot_avg5`. Cuando reaparezcan los datos, conviene confirmar que esos nombres coinciden exactamente con el CSV procesado.

### Seguir considerando cuotas Over/Under como mejora opcional

Si más adelante se incorporan cuotas de Over/Under 2.5, el techo del modelo puede subir bastante. Pero eso ya sería una mejora adicional, no el arreglo principal.

---

## Veredicto actualizado

El Modelo 2A **ya fue corregido a nivel de diseño**: el script actual usa un bloque de features mucho mejor que el descrito en el informe viejo. Lo que falta ahora no es redefinir el enfoque, sino volver a correrlo con `features_modelo2.csv` y reemplazar las métricas históricas negativas por resultados reales de la versión nueva.
