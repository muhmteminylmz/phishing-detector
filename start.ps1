# =============================================================================
#  Phishing Detector – Windows PowerShell ile Tek Tuşla Başlat
#  Kullanım:  powershell -ExecutionPolicy Bypass -File start.ps1
#
#  WSL/bash olmadan doğrudan Windows'ta çalışır.
#  Bu script:
#    ✅ Docker'ı kontrol eder (yoksa nasıl kuracağını gösterir)
#    ✅ Gerekli tüm kütüphaneleri otomatik indirir
#    ✅ Veritabanını, backend'i ve frontend'i başlatır
#    ✅ Uygulama hazır olana kadar bekler
#    ✅ Tarayıcıyı otomatik açar
# =============================================================================

$ErrorActionPreference = "Stop"

# Repo kökünden çalıştığımızdan emin ol
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  🛡️  Phishing Detector – Kurulum ve Başlatma (PowerShell)" -ForegroundColor Cyan
Write-Host "  ========================================================="
Write-Host ""

# ── ADIM 1: Docker var mı kontrol et ─────────────────────────────────────────
Write-Host "[1/4] Docker kontrol ediliyor..." -ForegroundColor Yellow

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "  ❌ Docker bulunamadı!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Docker Desktop'ı yüklemek için:"
    Write-Host "  👉 https://docs.docker.com/desktop/install/windows-install/"
    Write-Host ""
    Write-Host "  İndirdikten sonra Docker Desktop'ı başlatıp tekrar çalıştır:"
    Write-Host "     powershell -ExecutionPolicy Bypass -File start.ps1"
    Write-Host ""
    exit 1
}

$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Docker kurulu ama çalışmıyor!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Docker Desktop uygulamasını başlat (görev çubuğunda Docker simgesi yeşil olmalı)."
    Write-Host "  Sonra tekrar çalıştır:"
    Write-Host "     powershell -ExecutionPolicy Bypass -File start.ps1"
    Write-Host ""
    exit 1
}

Write-Host "  ✅ Docker hazır" -ForegroundColor Green

# ── ADIM 2: .env dosyası oluştur ─────────────────────────────────────────────
Write-Host "[2/4] Yapılandırma dosyası kontrol ediliyor..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✅ .env dosyası otomatik oluşturuldu" -ForegroundColor Green
} else {
    Write-Host "  ✅ .env dosyası zaten mevcut" -ForegroundColor Green
}

# ── ADIM 3: Tüm servisleri başlat ────────────────────────────────────────────
Write-Host "[3/4] Servisler başlatılıyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Gerekli tüm kütüphaneler ve bağımlılıklar Docker tarafından"
Write-Host "  otomatik indirilecek. İlk seferinde image build edilir ve ML modeli"
Write-Host "  eğitilir (3-7 dk). Sonraki çalıştırmalarda her şey hazır gelir,"
Write-Host "  yeniden eğitim gerekmez."
Write-Host ""

docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Docker Compose başlatılamadı!" -ForegroundColor Red
    Write-Host "  Docker Desktop'ın çalıştığından emin ol ve tekrar dene."
    exit 1
}

Write-Host ""
Write-Host "  ✅ Container'lar başlatıldı" -ForegroundColor Green

# ── ADIM 4: Uygulama hazır olana kadar bekle ─────────────────────────────────
Write-Host "[4/4] Uygulamanın hazır olması bekleniyor..." -ForegroundColor Yellow
Write-Host ""

$maxWait = 120
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Backend hazır! (${waited}s bekledik)" -ForegroundColor Green
            break
        }
    } catch {
        # Henüz hazır değil
    }
    Write-Host "  ⏳ Backend başlatılıyor... (${waited}s)" -NoNewline
    Write-Host "`r" -NoNewline
    Start-Sleep -Seconds $interval
    $waited += $interval
}

if ($waited -ge $maxWait) {
    Write-Host ""
    Write-Host "  ⚠️  Backend ${maxWait}s içinde yanıt vermedi." -ForegroundColor Yellow
    Write-Host "     Servisler hâlâ başlıyor olabilir. Birkaç dakika bekleyip kontrol et:"
    Write-Host "     curl http://localhost:8000/api/v1/health"
    Write-Host "     veya logları kontrol et: docker compose logs -f backend"
}

# ── Test: Örnek URL taraması yap ─────────────────────────────────────────────
try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host ""
        Write-Host "  🧪 Örnek tarama yapılıyor (test amaçlı)..."
        try {
            $body = '{"url":"http://paypa1-secure.xyz/login"}'
            $scanResult = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/scan/url" `
                -Method POST -Body $body -ContentType "application/json" `
                -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
            if ($scanResult.StatusCode -eq 200) {
                Write-Host "  ✅ API çalışıyor ve URL taraması yapılabiliyor" -ForegroundColor Green
            }
        } catch {
            # Tarama testi opsiyonel
        }
    }
} catch {
    # Health check opsiyonel
}

# ── Tarayıcıyı aç ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  🌐 Dashboard açılıyor: http://localhost"
Start-Process "http://localhost"

# ── Başarı mesajı ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║  ✅  Phishing Detector başarıyla çalışıyor!                ║" -ForegroundColor Green
Write-Host "  ╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "  ║                                                              ║" -ForegroundColor Green
Write-Host "  ║  🌐  Dashboard (Ana Sayfa) :  http://localhost              ║"
Write-Host "  ║  📡  API Dokümantasyonu    :  http://localhost:8000/docs    ║"
Write-Host "  ║  📊  Grafana İzleme        :  http://localhost:3001         ║"
Write-Host "  ║       (kullanıcı: admin, şifre: admin)                      ║"
Write-Host "  ║  🔭  Prometheus            :  http://localhost:9090          ║"
Write-Host "  ║                                                              ║" -ForegroundColor Green
Write-Host "  ╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "  ║  Diğer komutlar:                                            ║" -ForegroundColor Green
Write-Host "  ║    docker compose logs -f    → Canlı logları izle           ║"
Write-Host "  ║    docker compose down       → Tüm servisleri durdur        ║"
Write-Host "  ║    make help                 → Tüm komutları listele        ║"
Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
