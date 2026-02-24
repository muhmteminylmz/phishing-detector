#!/bin/bash
set -e

echo "🛡️  Setting up Phishing Detector..."

# Create virtual environment
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate and install
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Create .env if not exists
if [ ! -f "../.env" ]; then
    cp ../.env.example ../.env
    echo "✅ .env file created from .env.example"
fi

# Train ML model
echo "🧠 Training ML model..."
python ml/train.py
echo "✅ ML model trained"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Start with:  docker compose up -d"
echo "Backend dev: uvicorn app.main:app --reload"
