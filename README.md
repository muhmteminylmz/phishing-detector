# 🛡️ Phishing Detector

> **🇹🇷 Adım adım detaylı Türkçe rehber → [KURULUM.md](KURULUM.md)**  
> **Türkçe → [hemen aşağıda](#-türkçe--tek-tuşla-çalıştır)**  
> **English → [scroll down](#-english--one-command-start)**

---

## 🇹🇷 Türkçe — Tek Tuşla Çalıştır

### Tek Gereksinim: Docker

Docker'ı kur, başlat, işte bu kadar. Başka hiçbir şeye gerek yok.
Python da, Node.js da, veritabanı da — hepsi Docker tarafından **otomatik** indirilir.

| İşletim Sistemi | Docker İndirme Linki |
|---|---|
| Windows | https://docs.docker.com/desktop/install/windows-install/ |
| Mac | https://docs.docker.com/desktop/install/mac-install/ |
| Linux | `curl -fsSL https://get.docker.com \| sh` |

> Docker Desktop'ı kurduktan sonra uygulamayı başlat (sağ alttaki Docker simgesi yeşil olmalı).

---

### Çalıştırma Adımları

**Adım 1 — Projeyi indir:**
```bash
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
```

**Adım 2 — Tek komutla başlat:**

Windows (CMD — en kolay yol, çift tıkla veya CMD'ye yaz):
```
start.bat
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

Mac / Linux:
```bash
bash start.sh
```

> **💡 Detaylı adım adım rehber için:** [KURULUM.md](KURULUM.md)

Bu kadar. Script her şeyi kendi kendine yapar:
- Gerekli tüm kütüphaneleri indirir (ilk seferinde ~2-5 dakika, sonraki çalıştırmalarda çok hızlı)
- Veritabanını ve cache'i başlatır
- ML modelini eğitir
- Backend ve frontend'i başlatır
- Uygulama hazır olana kadar bekler
- **Tarayıcıyı otomatik açar**

---

### Ne Göreceksin?

Script başarıyla tamamlandığında terminalde şunu göreceksin:

```
✅  Phishing Detector başarıyla çalışıyor!
══════════════════════════════════════════
🌐  Dashboard (Ana Sayfa) :  http://localhost
📡  API Dokümantasyonu    :  http://localhost:8000/docs
📊  Grafana İzleme        :  http://localhost:3001
🔭  Prometheus            :  http://localhost:9090
```

Ve tarayıcın **http://localhost** adresinde otomatik açılacak:

- URL kutusuna bir adres yaz (örn. `http://paypal-secure-login.xyz`) ve **"Tara"** butonuna bas
- Sonuç: Phishing mi? Güvenli mi? Risk skoru nedir?

---

### Model Eğitimi (Training) – İlerleme Takibi

Model eğitimi sırasında terminalde her adımın ilerlemesini, tamamlanma yüzdesini ve geçen süreyi göreceksin:

```
============================================================
  🛡️  Phishing Detector — Model Training
============================================================
  Steps: 6
    1. Dataset generation
    2. Build ensemble model
    3. Cross-validation (5-fold)
    4. Train final model
    5. Evaluation
    6. Save model & metrics
============================================================

[Step 1/6] Generating dataset...
  Phishing samples: 100%|████████████| 1000/1000
  Legit samples   : 100%|████████████| 1000/1000
  ✅ Dataset ready — 2000 samples (0.3s)

[Step 3/6] Cross-validating (5-fold)...
  CV folds: 100%|████████████| 5/5
  ✅ CV AUC: 0.9998 ± 0.0002 (12.4s)

...

============================================================
  🎉 Training complete!  Total time: 0m 18s
============================================================
```

Her adımdan sonra tahmini kalan süre (`⏱️ Estimated remaining: ~12s`) gösterilir, böylece eğitimin ne zaman biteceğini takip edebilirsin.

**Arka planda çalışan Vmmem nedir?**
Windows'ta Docker çalışırken `Vmmem` adlı bir süreç görürsün. Bu, Docker Desktop'ın kullandığı WSL2 sanal makinesidir ve yalnızca Windows'a özgüdür (Mac/Linux'ta görünmez). Eğitim tamamlandığında kaynak kullanımı düşer. Yukarıdaki ilerleme çubuklarıyla eğitimin ne zaman biteceğini takip edebilirsin.

> **💡 Vmmem bellek kullanımını sınırlamak için:** `%USERPROFILE%\.wslconfig` dosyası oluşturup şunu ekle:
> ```ini
> [wsl2]
> memory=4GB
> processors=2
> ```
> Sonra PowerShell'de `wsl --shutdown` çalıştır ve Docker Desktop'ı yeniden başlat.

---

### PC Kapanırsa Ne Olur? (Checkpoint / Resume)

Eğitim sırasında PC kapanırsa veya Docker durdurulursa **sorun yok** — eğitim kaldığı yerden devam eder:

```bash
# PC yeniden açıldıktan sonra sadece tekrar çalıştır:
bash start.sh
```

Script otomatik olarak:
- ✅ Tamamlanan adımları atlar (dataset, cross-validation vb.)
- ✅ Kalan adımlardan devam eder
- ✅ Tamamlandığında checkpoint dosyalarını temizler

Terminalde şöyle bir çıktı göreceksin:

```
============================================================
  🛡️  Phishing Detector — Model Training
============================================================
  Steps: 6
    ✅ Dataset generation
    ✅ Build ensemble model
    ✅ Cross-validation (5-fold)
     4. Train final model
     5. Evaluation
     6. Save model & metrics

  ▶ Resuming from step 4 (steps 1-3 already done)
============================================================
```

> **Not:** Eğitimi sıfırdan başlatmak istersen checkpoint klasörünü sil:
> ```bash
> rm -rf backend/ml/checkpoints/
> ```

---

### Uzak Bilgisayarda (Remote) Eğitim

Projeyi uzak bir sunucuda (VPS, bulut VM, üniversite sunucusu vb.) eğitmek için:

```bash
# 1. Uzak sunucuya bağlan
ssh kullanici@sunucu-adresi

# 2. Projeyi indir
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector

# 3. Docker kur (Linux sunucularda)
curl -fsSL https://get.docker.com | sh

# 4. Başlat
bash start.sh
```

> **İpucu:** SSH bağlantısı kesilse bile eğitimin devam etmesi için `screen` veya `tmux` kullan:
> ```bash
> tmux new -s training
> bash start.sh
> # Ctrl+B, D ile çık — eğitim arka planda devam eder
> # Tekrar bağlanmak için: tmux attach -t training
> ```

---

### Sık Kullanılan Komutlar

```bash
# Servisleri durdur
docker compose down

# Logları izle (Ctrl+C ile çık)
docker compose logs -f

# Tekrar başlat
bash start.sh

# Yardım
make help
```

---

### Sorun Giderme

**WSL hatası: `execvpe(/bin/bash) failed: No such file or directory`:**
→ Bu hata Windows'ta WSL (Linux Alt Sistemi) kurulu olmadığında oluşur.
**Çözüm:** PowerShell ile başlat (WSL gerektirmez):
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```
Veya WSL'i kurmak istersen PowerShell'i **yönetici olarak** açıp şunu çalıştır:
```powershell
wsl --install
```
Sonra bilgisayarı yeniden başlat ve `bash start.sh` komutunu tekrar dene.

**"Docker bulunamadı" hatası:**
→ Docker Desktop'ı yükle ve başlat, sonra tekrar başlat.

**"Docker çalışmıyor" hatası:**
→ Docker Desktop uygulamasını aç (sağ alttaki sistem saatinde Docker simgesi görünmeli).

**Port zaten kullanımda (port already in use):**
```bash
docker compose down
bash start.sh
```

**Servisler yavaş başlıyor:**
→ İlk çalıştırmada Docker image'ları indirildiği için 5-10 dakika sürebilir. Bir sonraki seferinde çok daha hızlı olacak.

**Logları görmek istiyorum:**
```bash
docker compose logs -f          # tüm servisler
docker compose logs -f backend  # sadece backend
```

---

## 🇬🇧 English — One-Command Start

### Only requirement: Docker

[Get Docker Desktop](https://docs.docker.com/get-docker/) — no Python, Node.js, or database setup needed. Everything is downloaded automatically.

### Run

Windows (CMD — easiest, double-click or type in CMD):
```
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
start.bat
```

Windows (PowerShell — no WSL required):
```powershell
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
powershell -ExecutionPolicy Bypass -File start.ps1
```

Mac / Linux:
```bash
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
bash start.sh
```

That's it. The script:
- Downloads all dependencies automatically (Docker images, ~2-5 min first time)
- Starts the database, cache, backend, and frontend
- Waits until the app is actually ready
- Opens the browser automatically at **http://localhost**

### What you'll see

The dashboard at `http://localhost` lets you type any URL and scan it for phishing. The API docs at `http://localhost:8000/docs` let you test the API interactively.

### Commands

```bash
docker compose down          # stop all services
docker compose logs -f       # watch live logs
bash start.sh                # start / restart everything
make help                    # list all make targets
```

---

## ✨ Features

- **Ensemble ML Model** — XGBoost + LightGBM + Random Forest with soft voting
- **47 URL Features** — URL structure, SSL, WHOIS, HTML analysis, blacklist
- **Real-time API** — FastAPI with async I/O, Redis caching, rate limiting
- **Modern Dashboard** — React + TypeScript + TailwindCSS
- **Bulk Scanning** — Upload CSV or paste URLs, export results
- **Monitoring** — Prometheus metrics + Grafana dashboards

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
| `POST` | `/api/v1/scan/bulk` | Bulk scan (up to 100 URLs) |
| `GET` | `/api/v1/scan/history` | Paginated scan history |
| `GET` | `/api/v1/reports/stats` | Aggregate statistics |
| `GET` | `/api/v1/health` | Health check |

```bash
curl -X POST http://localhost:8000/api/v1/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypa1-secure.xyz/login"}'
```

```json
{
  "is_phishing": true,
  "confidence": 0.94,
  "risk_score": 94,
  "risk_level": "CRITICAL"
}
```

## 🧪 Tests

```bash
make test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run `make test`
4. Submit a pull request

## 📄 License

MIT License
