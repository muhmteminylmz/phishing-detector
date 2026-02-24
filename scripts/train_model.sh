#!/bin/bash
set -e
cd "$(dirname "$0")/../backend"
[ -f ".venv/bin/activate" ] && source .venv/bin/activate
echo "Training ML model..."
python ml/train.py
echo "Done."
