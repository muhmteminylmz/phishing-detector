#!/bin/bash
# =============================================================================
#  Phishing Detector – Kurulum ve Başlatma Scripti
#  Kullanım: bash scripts/setup.sh
# =============================================================================
set -e

# Repo kökünden çalıştığımızdan emin ol
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo ""
echo "🛡️  Phishing Detector – Kurulum Başlıyor"
echo "==========================================="
echo ""

# ── Docker var mı kontrol et ──────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    echo "❌ Docker bulunamadı."
    echo "   Lütfen Docker Desktop'ı yükleyin: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "❌ Docker çalışmıyor. Lütfen Docker Desktop'ı başlatın."
    exit 1
fi

echo "✅ Docker hazır"

# ── .env dosyası oluştur ──────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env dosyası .env.example'dan oluşturuldu"
else
    echo "ℹ️  .env dosyası zaten mevcut, atlanıyor"
fi

# ── Servisleri başlat ─────────────────────────────────────────────────────────
echo ""
echo "▶  Tüm servisler başlatılıyor (bu ilk seferde birkaç dakika sürebilir)..."
echo ""

docker compose up -d

echo ""
echo "⏳ Servislerin hazır olması bekleniyor..."
sleep 5

# ── Durum özeti ───────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅  Phishing Detector başarıyla başlatıldı!               ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  🌐  Dashboard  :  http://localhost                         ║"
echo "║  📡  API Docs   :  http://localhost:8000/docs               ║"
echo "║  📊  Grafana    :  http://localhost:3001  (admin / admin)   ║"
echo "║  🔭  Prometheus :  http://localhost:9090                    ║"
echo "║                                                              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Diğer komutlar:                                            ║"
echo "║    make logs    → Canlı logları izle                       ║"
echo "║    make stop    → Tüm servisleri durdur                    ║"
echo "║    make help    → Tüm komutları listele                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
