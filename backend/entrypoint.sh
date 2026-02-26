#!/bin/bash
# =============================================================================
#  Entrypoint: Ensure the pre-trained model is available in the volume,
#  then start the application.
# =============================================================================
set -e

MODEL_DIR="/app/ml/models"
PRETRAINED_DIR="/app/ml/pretrained"
MODEL_FILE="ensemble_model.joblib"

# If the volume-mounted models directory is empty (first run or after prune),
# copy the model that was pre-trained during Docker build.
if [ ! -f "$MODEL_DIR/$MODEL_FILE" ] && [ -f "$PRETRAINED_DIR/$MODEL_FILE" ]; then
    echo "📦 Pre-trained model not found in volume – copying from image..."
    cp "$PRETRAINED_DIR/$MODEL_FILE" "$MODEL_DIR/$MODEL_FILE"
    echo "✅ Model ready."
fi

# Copy pre-trained metrics if missing
if [ ! -f "$MODEL_DIR/../results/metrics.json" ] && [ -f "$PRETRAINED_DIR/metrics.json" ]; then
    mkdir -p /app/ml/results
    cp "$PRETRAINED_DIR/metrics.json" /app/ml/results/metrics.json
fi

exec "$@"
