# Informe Actualizado — Modelo 1: Expected Goals (xG)

**Fecha:** 23 de abril de 2026  
**Taller:** ML1-2026I — Universidad Externado de Colombia  
**Modelo:** Regresión logística binaria — target: `is_goal`

---

## Estado real del modelo

El Modelo 1 sigue siendo el más sólido del proyecto. El último resultado confirmado en la documentación es **AUC-ROC = 0.7813**, suficiente para cumplir el benchmark del taller. Sin embargo, el estado del código ya cambió: la versión actual de entrenamiento incorpora un set de features más fuerte que el reportado originalmente.

En [scripts/02_train_modelo1.py](/home/camilo/proyectos/Ml_Futbol_Final/scripts/02_train_modelo1.py:37) ya están incluidas estas mejoras:

- `is_penalty`
- `shot_quality_index`
- `is_in_area`
- `is_central`
- `ppda`
- `pass_decentralization`

Eso significa que el informe anterior quedó desactualizado: las mejoras ya no son solo una propuesta, sino parte del pipeline actual.

---

## Métricas confirmadas vs. métricas pendientes

### Último resultado confirmado

| Métrica | Valor |
|---------|------:|
| AUC-ROC | 0.7813 |
| Brier Score | 0.0733 |
| Log Loss | 0.2599 |
| xG medio | 0.1118 |
| Tasa real de gol | 0.1062 |
| Ratio calibración | 1.05x |

### Estado de la versión mejorada

La versión mejorada **todavía no tiene métricas regeneradas en este workspace** porque faltan los archivos de entrada:

- `data/raw/events.csv`
- `data/processed/features_modelo1.csv`

Por eso, hoy no existe todavía un `metrics_modelo1.json` nuevo que confirme el rendimiento del feature set ampliado.

---

## Lo que sí está bien

### El benchmark del taller ya se cumplió

Con AUC = 0.7813, el modelo supera el umbral de 0.78. El margen es corto, pero válido.

### La validación temporal está bien planteada

El split por `match_date` sigue siendo una decisión metodológica correcta. Evita leakage y hace que la métrica sea creíble.

### La calibración documentada es muy buena

El modelo histórico quedó bien calibrado: el xG medio predicho estuvo muy cerca de la tasa real de gol.

### El código actual ya corrigió la mayor debilidad del informe viejo

Antes se criticaba que variables muy potentes como `is_penalty` y `shot_quality_index` no se usaban. Esa crítica ya no aplica al código actual: ahora sí están dentro del modelo.

---

## Lo que sigue pendiente

### Falta correr de nuevo el modelo mejorado

La principal deuda ya no es de diseño sino de ejecución. El feature set mejorado existe, pero no se ha podido reentrenar en esta copia del proyecto porque no están los CSV necesarios.

### Falta confirmar el impacto real de las nuevas features

Es razonable esperar una mejora sobre 0.7813, pero todavía no debe afirmarse una AUC nueva sin regenerar:

- ROC
- calibración
- VIF
- `metrics_modelo1.json`

### Falta enriquecer la interpretación final

Sería útil añadir una tabla breve de coeficientes u odds ratios con lectura táctica para dejar el informe más fuerte frente a la rúbrica.

---

## Veredicto actualizado

El Modelo 1 **cumple** su rúbrica con las métricas históricas confirmadas y además **ya tiene implementada** una versión mejorada en el código. En este momento, el cuello de botella no es conceptual sino operativo: faltan los datos de entrada para regenerar las métricas y reemplazar el valor histórico de AUC = 0.7813 por el resultado real de la versión ampliada.
