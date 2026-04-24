#!/usr/bin/env bash
# Ejecuta el pipeline completo. Activar venv antes: source venv/bin/activate
set -e

PYTHON=../venv/bin/python
if [ ! -f "$PYTHON" ]; then
    PYTHON=python3
fi

cd "$(dirname "$0")/.."

echo "=== [1/4] Feature engineering Modelo 1 ==="
$PYTHON scripts/01_build_features_modelo1.py

echo "=== [2/4] Entrenamiento Modelo 1 (xG) ==="
$PYTHON scripts/02_train_modelo1.py

echo "=== [3/4] Feature engineering Modelo 2 ==="
$PYTHON scripts/03_build_features_modelo2.py

echo "=== [4/4] Entrenamiento Modelo 2 (regresión + clasificación) ==="
$PYTHON scripts/04_train_modelo2.py

echo ""
echo "Pipeline completo. Resultados en data/outputs/ y models/"
