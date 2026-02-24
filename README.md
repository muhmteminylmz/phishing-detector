# 🛡️ Phishing Detector

> **Türkçe talimatlar için → [aşağıya kaydır](#-türkçe--nasıl-çalıştırılır)**
> **English instructions → [scroll down](#-english--how-to-run)**

---

## 🇹🇷 Türkçe — Nasıl Çalıştırılır?

### Ön Gereksinim

Sadece **Docker** gereklidir.
[Docker Desktop'ı buradan indir](https://docs.docker.com/get-docker/)

> Windows kullanıcısıysan Docker Desktop'ı indirip kurduktan sonra başlatman yeterli.

---

### Adım 1 — Projeyi indir

```bash
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
```

---

### Adım 2 — Başlat

```bash
bash scripts/setup.sh
```

**Hepsi bu kadar.** Script gerekli tüm servisleri (veritabanı, cache, backend, frontend) otomatik olarak başlatır.
ML modeli de ilk açılışta **otomatik eğitilir** — ayrıca bir şey yapmana gerek yok.

`make` komutu varsa alternatif olarak:

```bash
make start
```

---

### Adım 3 — Tarayıcıda aç

Servisler başladıktan sonra şu adreslere gidebilirsin:

| Adres | Ne işe yarar |
|---|---|
| **http://localhost** | 🌐 Ana dashboard (URL tara, sonuçları gör) |
| http://localhost:8000/docs | 📡 API dökümantasyonu (Swagger UI) |
| http://localhost:3001 | 📊 Grafana izleme (kullanıcı: `admin`, şifre: `admin`) |
| http://localhost:9090 | 🔭 Prometheus metrikleri |

---

### Sık Kullanılan Komutlar

```bash
make help      # Tüm komutları listele
make start     # Servisleri başlat
make stop      # Servisleri durdur
make restart   # Yeniden başlat
make logs      # Canlı logları izle (Ctrl+C ile çık)
make status    # Hangi servisler çalışıyor?
make test      # Backend testlerini çalıştır
make train     # ML modelini yeniden eğit
make clean     # Tüm verileri sil (dikkat!)
```

`make` komutu yoksa Docker Compose komutlarını doğrudan kullanabilirsin:

```bash
docker compose up -d      # başlat
docker compose down       # durdur
docker compose logs -f    # logları izle
```

---

### Sorun Giderme

**"Docker bulunamadı" hatası alıyorum:**
Docker Desktop'ın yüklü ve çalışır durumda olduğundan emin ol.

**Servisler başlamadı / hata var:**
```bash
make logs     # hata mesajlarına bak
make stop
make start    # yeniden dene
```

**Port zaten kullanımda hatası (port already in use):**
80, 8000, 5432 veya 6379 portlarını kullanan başka bir uygulama olabilir.
`docker compose down` ile önce durdur, sonra tekrar başlat.

---

### Yerel Geliştirme (hot-reload ile)

Kodu düzenleyip anlık değişiklik görmek istiyorsan:

```bash
make dev
```

Bu komut PostgreSQL ve Redis'i Docker'da başlatır. Ardından **iki ayrı terminal** aç:

```bash
# Terminal 1 — Backend (http://localhost:8000)
cd backend
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend (http://localhost:3000)
cd frontend
npm install
npm run dev
```

---

## 🇬🇧 English — How to Run

### Prerequisites

Only **Docker** is required. [Get Docker Desktop](https://docs.docker.com/get-docker/).

### Quick Start

```bash
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
bash scripts/setup.sh   # or: make start
```

Open **http://localhost** for the dashboard.
The ML model is **trained automatically on first startup** — no manual step needed.

### All Make Commands

```bash
make help      # List all commands
make start     # Start all services (Docker)
make stop      # Stop all services
make restart   # Restart services
make logs      # Follow live logs
make status    # Show service status
make dev       # Local dev with hot-reload (DB+Redis in Docker)
make dev-stop  # Stop local dev services
make test      # Run backend tests
make train     # Re-train ML model inside Docker
make clean     # Delete all volumes/data (destructive!)
```

### Service URLs

| URL | Description |
|---|---|
| http://localhost | Dashboard |
| http://localhost:8000/docs | API documentation (Swagger) |
| http://localhost:3001 | Grafana (admin / admin) |
| http://localhost:9090 | Prometheus |

---

## ✨ Features

- **Ensemble ML Model** — XGBoost + LightGBM + Random Forest with soft voting
- **47 URL Features** — URL structure, SSL, WHOIS, HTML analysis, blacklist
- **Real-time API** — FastAPI with async I/O, Redis caching, rate limiting
- **Modern Dashboard** — React + TypeScript + TailwindCSS
- **Bulk Scanning** — Upload CSV or paste URLs, export results
- **Monitoring** — Prometheus metrics + Grafana dashboards
- **One-command startup** — `bash scripts/setup.sh`

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

## 📡 API Reference

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

### Example

```bash
curl -X POST http://localhost:8000/api/v1/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypa1-secure.xyz/login"}'
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "http://paypa1-secure.xyz/login",
  "is_phishing": true,
  "confidence": 0.94,
  "risk_score": 94,
  "risk_level": "CRITICAL",
  "features": { "url_length": 32, "suspicious_words": 1 },
  "feature_importance": { "suspicious_words": 0.21 },
  "model_version": "1.0.0",
  "scan_time_ms": 234
}
```

## 🧠 ML Model

**Algorithm:** Ensemble (XGBoost + LightGBM + Random Forest, soft voting)

The model is **automatically trained on first startup** if no saved model file exists.
To force a re-train: `make train`

**Features (47 total):** URL structure, entropy, character ratios, subdomain count,
IP detection, SSL validity/issuer/expiry, WHOIS domain age, HTML forms/iframes/obfuscation,
blacklist membership.

## 🧪 Tests

```bash
make test
# or manually:
cd backend && pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `make test`
4. Submit a pull request

## 📄 License

MIT License
