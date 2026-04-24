# Informe Actualizado — Modelo 2B: Clasificación `ftr` (H/D/A)

**Fecha:** 23 de abril de 2026  
**Taller:** ML1-2026I — Universidad Externado de Colombia  
**Modelo:** Regresión logística multiclase — target: `ftr`

---

## Estado real del modelo

El informe anterior acertaba en el diagnóstico: el modelo estaba muy cerca de Bet365 pero no lo superaba. Lo que cambió es que la combinación de features recomendada ya fue llevada al código.

En [scripts/04_train_modelo2.py](/home/camilo/proyectos/Ml_Futbol_Final/scripts/04_train_modelo2.py:52) el bloque de clasificación actual ya incluye:

- `implied_prob_h`, `implied_prob_d`, `implied_prob_a`
- `b365h`, `b365d`, `b365a`
- `bookmaker_spread_draw`
- `xg_form_diff`
- `points_form_diff`
- `big_chances_diff`
- `home_strength_rating`

Eso significa que la mejora `odds + form`, antes presentada como experimento pendiente, ya está implementada.

---

## Métricas confirmadas vs. métricas pendientes

### Último resultado confirmado

La documentación previa reporta para la versión histórica:

| Métrica | Valor histórico |
|---------|----------------:|
| Accuracy | 49.58% |
| F1-macro | 0.377 |
| Accuracy Bet365 | 50.83% |
| Brecha vs Bet365 | -1.25 pp |

### Estado de la versión actual

La versión nueva del script todavía **no ha sido rerun en este workspace** porque falta:

- `data/processed/features_modelo2.csv`

Por lo tanto, todavía no existe una métrica actualizada que confirme si el modelo ya supera a Bet365.

---

## Lo que sí mejoró

### La mejora principal ya no está pendiente

Antes el punto crítico era que nunca se había probado la combinación `odds + form`. Esa objeción ya no aplica al código actual: la combinación ya está definida como feature set base.

### El modelo mantiene una evaluación sensata

La comparación directa contra Bet365 sigue siendo el benchmark correcto, y el uso de validación temporal conserva credibilidad metodológica.

### El caso sigue siendo recuperable

Como la brecha histórica era solo de 1.25 puntos porcentuales, este es un modelo donde una mejora de features sí puede mover la aguja de forma realista.

---

## Lo que sigue pendiente

### Falta validar si el nuevo bloque sí supera a Bet365

La hipótesis ya está implementada, pero falta confirmarla con datos. Sin `metrics_modelo2.json` regenerado, cualquier afirmación sobre una nueva accuracy sería especulativa.

### Falta explorar una variante para empates

El script actual no incorpora todavía una versión con `class_weight="balanced"`. Eso sigue siendo una línea útil para intentar subir el desempeño en draws y mejorar F1-macro.

### Faltan métricas de probabilidad

Sigue siendo recomendable añadir:

- calibración multiclase,
- Brier score multiclase,
- y F1 por clase.

Eso fortalecería la lectura técnica del modelo aunque la accuracy siga siendo la métrica principal frente al benchmark.

---

## Veredicto actualizado

El Modelo 2B ya no está en fase de diagnóstico sino en fase de validación final. La mejora más importante del feature set ya quedó incorporada al código, pero el proyecto todavía necesita volver a correr el pipeline con `features_modelo2.csv` para saber si la nueva versión realmente supera a Bet365 o si aún falta un ajuste adicional.
