# 🛡️ Phishing Detector

Production-ready, ML-based phishing site detection system with real-time URL analysis, ensemble machine learning models, and a modern React dashboard.

## ✨ Features

- **Ensemble ML Model** — XGBoost + LightGBM + Random Forest with soft voting
- **40+ URL Features** — URL structure, SSL, WHOIS, HTML analysis, blacklist
- **Real-time API** — FastAPI with async I/O, Redis caching, rate limiting
- **Modern Dashboard** — React + TypeScript + TailwindCSS
- **Bulk Scanning** — Upload CSV or paste URLs, export results
- **Monitoring** — Prometheus metrics + Grafana dashboards
- **Docker** — One-command deployment

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────────────────────────────────┐
│   Browser   │───▶│              Nginx (port 80)              │
└─────────────┘    └──────┬───────────────────┬───────────────┘
                          │                   │
                   ┌──────▼──────┐    ┌───────▼──────┐
                   │  Frontend   │    │   Backend     │
                   │ React/Vite  │    │  FastAPI      │
                   │ (port 3000) │    │  (port 8000)  │
                   └─────────────┘    └──────┬────────┘
                                             │
                          ┌──────────────────┼──────────────┐
                          │                  │              │
                   ┌──────▼──────┐  ┌────────▼────┐  ┌─────▼──────┐
                   │ PostgreSQL  │  │    Redis     │  │ ML Models  │
                   │ (port 5432) │  │ (port 6379)  │  │  (joblib)  │
                   └─────────────┘  └─────────────┘  └────────────┘
```

## 🚀 Quick Start (Docker)

```bash
# Clone
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector

# Copy env and start
cp .env.example .env
docker compose up -d

# Train ML model (first time)
docker compose exec backend python ml/train.py
```

Open http://localhost for the dashboard, http://localhost:8000/docs for API.

## 🔧 Manual Setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python ml/train.py            # Train the model
uvicorn app.main:app --reload  # Start backend

# In another terminal
cd frontend
npm install
npm run dev                    # Start frontend (port 3000)
```

Or use the setup script:
```bash
bash scripts/setup.sh
```

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/scan/url` | Scan a single URL |
| `POST` | `/api/v1/scan/bulk` | Start bulk scan (up to 100 URLs) |
| `GET` | `/api/v1/scan/bulk/{task_id}` | Get bulk scan status |
| `GET` | `/api/v1/scan/history` | Paginated scan history |
| `GET` | `/api/v1/scan/{scan_id}` | Get scan by ID |
| `GET` | `/api/v1/reports/stats` | Aggregate statistics |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypa1-secure.xyz/login"}'
```

### Example Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "http://paypa1-secure.xyz/login",
  "is_phishing": true,
  "confidence": 0.94,
  "risk_score": 94,
  "risk_level": "CRITICAL",
  "features": { "url_length": 32, "suspicious_words": 1, ... },
  "feature_importance": { "suspicious_words": 0.21, ... },
  "model_version": "1.0.0",
  "scan_time_ms": 234
}
```

## 🧠 ML Model

**Algorithm:** Ensemble (XGBoost + LightGBM + Random Forest, soft voting)

**Features (47 total):**
- URL structure: length, dots, hyphens, depth, entropy, character ratios
- Domain: age, registration length, subdomain count, IP detection
- SSL: validity, issuer trust, days remaining
- HTML: form count, iframe count, external links, obfuscation
- Blacklist membership

**Training:**
```bash
cd backend
python ml/train.py     # Trains and saves to ml/models/ensemble_model.joblib
python ml/evaluate.py  # Evaluate on held-out test set
```

## 🧪 Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## 📊 Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest tests/ -v`
4. Submit a pull request

## 📄 License

MIT License — see [LICENSE](LICENSE)
