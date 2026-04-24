# Panorama General Actualizado — ML Premier League 25/26

**Fecha:** 23 de abril de 2026  
**Taller:** ML1-2026I — Universidad Externado de Colombia  
**Docente:** Julián Zuluaga

---

## Lectura consolidada del estado actual

El proyecto sigue teniendo una base metodológica fuerte: validación temporal, ausencia de leakage y comparación seria contra Bet365. La diferencia frente a la versión anterior de los informes es que varias mejoras que antes aparecían como "pendientes" ya fueron implementadas en los scripts de entrenamiento.

En este momento, el principal cuello de botella ya no es de diseño sino de ejecución: faltan los archivos procesados en `data/` para regenerar métricas y artefactos.

---

## Estado por componente

| Componente | Estado actual | Comentario |
|-----------|---------------|------------|
| Modelo 1 xG | Código mejorado implementado | Falta rerun con `features_modelo1.csv` |
| Modelo 2A regresión | Bloque de features corregido | Falta rerun con `features_modelo2.csv` |
| Modelo 2B clasificación | Bloque `odds + form` implementado | Falta rerun con `features_modelo2.csv` |
| Metodología | Fuerte | Split temporal y benchmarking bien planteados |
| Reportería | Actualizada | Ahora alineada con el código real |
| Página web | Pendiente | No existe interfaz visible todavía |

---

## Qué resultados siguen siendo los últimos confirmados

Mientras no se vuelva a ejecutar el pipeline con los datos, estos siguen siendo los valores históricos confirmados en la documentación:

| Modelo | Métrica principal | Valor confirmado |
|-------|-------------------|-----------------:|
| Modelo 1 xG | AUC-ROC | 0.7813 |
| Modelo 2A regresión | R² | -0.034 |
| Modelo 2B clasificación | Accuracy | 49.58% |
| Benchmark Bet365 | Accuracy | 50.83% |

Estos valores sirven como línea base documental, pero ya no describen necesariamente el comportamiento del código actual.

---

## Qué mejoras ya están implementadas

### Modelo 1

El script actual ya incorpora:

- `is_penalty`
- `shot_quality_index`
- `is_in_area`
- `is_central`

La mejora dejó de ser teórica y pasó a estar codificada.

### Modelo 2A

El script actual ya usa un bloque de regresión orientado a rendimiento y mercado:

- xG rolling
- tiros al arco rolling
- `expected_total_xg`
- spread de cuotas y probabilidad implícita de empate
- `away_strength_rating`

### Modelo 2B

El script actual ya usa la combinación que antes se recomendaba probar:

- cuotas implícitas
- cuotas crudas Bet365
- `bookmaker_spread_draw`
- `xg_form_diff`
- `points_form_diff`
- `big_chances_diff`
- `home_strength_rating`

---

## Qué sigue pendiente de forma real

### 1. Regenerar datos y métricas

Hoy faltan en el workspace:

- `data/raw/events.csv`
- `data/processed/features_modelo1.csv`
- `data/processed/features_modelo2.csv`

Sin esos archivos no se pueden recrear:

- `metrics_modelo1.json`
- `metrics_modelo2.json`
- modelos `.joblib`
- gráficas actualizadas

### 2. Confirmar impacto real de los cambios

La expectativa razonable es que:

- M1 mejore o al menos mantenga el benchmark con más colchón,
- M2A suba respecto al R² negativo histórico,
- M2B quede más cerca o por encima de Bet365.

Pero eso todavía debe demostrarse con una nueva corrida.

### 3. Construir la página web

La parte visual sigue pendiente. El proyecto tiene contenido, pero no interfaz final ni despliegue público.

---

## Veredicto actualizado

El proyecto está en una posición mejor que la que reflejaban los informes viejos. El código ya incorporó varias de las mejoras más importantes, especialmente en selección de features. Aun así, no conviene declarar victoria todavía: faltan los datos para rerun, faltan métricas nuevas y falta la capa final de presentación web.
