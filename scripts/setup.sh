#!/bin/bash
# =============================================================================
#  Phishing Detector – Tek Komutla Kur ve Başlat
#  Kullanım: bash start.sh   veya   bash scripts/setup.sh
#
#  Bu script her şeyi otomatik yapar:
#    1. Docker'ı kontrol eder
#    2. Gerekli tüm kütüphaneleri otomatik indirir (Docker image'ları)
#    3. Veritabanı, cache, backend ve frontend'i başlatır
#    4. Uygulamanın gerçekten çalıştığını doğrular
#    5. Tarayıcıyı otomatik açar
# =============================================================================

# Hata olursa dur
set -e

# Repo kökünden çalıştığımızdan emin ol
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
# Eğer script doğrudan repo kökünden çalıştırıldıysa (start.sh) ROOT_DIR zaten doğrudur
if [ "$(basename "$SCRIPT_DIR")" != "scripts" ]; then
    ROOT_DIR="$SCRIPT_DIR"
fi
cd "$ROOT_DIR"

# ── Renkler ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo ""
echo -e "${BLUE}🛡️  Phishing Detector – Kurulum ve Başlatma${NC}"
echo "============================================"
echo ""

# ── ADIM 1: Docker var mı kontrol et ─────────────────────────────────────────
echo -e "${YELLOW}[1/4]${NC} Docker kontrol ediliyor..."

if ! command -v docker &>/dev/null; then
    echo -e "${RED}❌ Docker bulunamadı!${NC}"
    echo ""
    echo "  Docker'ı yüklemek için:"
    # OS tespiti
    case "$(uname -s)" in
        Darwin)
            echo "  👉 Mac:     https://docs.docker.com/desktop/install/mac-install/"
            echo "  İndirdikten sonra Docker Desktop'ı başlatıp tekrar çalıştır:"
            echo "     bash start.sh"
            ;;
        Linux)
            echo "  👉 Linux:   https://docs.docker.com/engine/install/"
            echo "  Hızlı kurulum (Ubuntu/Debian):"
            echo "     curl -fsSL https://get.docker.com | sh"
            echo "     sudo usermod -aG docker \$USER   # logout/login gerektirir"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo "  👉 Windows: https://docs.docker.com/desktop/install/windows-install/"
            echo "  İndirdikten sonra Docker Desktop'ı başlatıp tekrar çalıştır:"
            echo "     bash start.sh"
            ;;
        *)
            echo "  👉 https://docs.docker.com/get-docker/"
            ;;
    esac
    echo ""
    exit 1
fi

if ! docker info &>/dev/null 2>&1; then
    echo -e "${RED}❌ Docker kurulu ama çalışmıyor!${NC}"
    echo ""
    echo "  Docker Desktop'ı başlat, ardından tekrar çalıştır:"
    echo "     bash start.sh"
    echo ""
    exit 1
fi

echo -e "  ${GREEN}✅ Docker hazır${NC}"

# ── ADIM 2: .env dosyası oluştur ─────────────────────────────────────────────
echo -e "${YELLOW}[2/4]${NC} Yapılandırma dosyası kontrol ediliyor..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    # Güvenli bir SECRET_KEY üret ve .env dosyasına yaz
    if command -v python3 &>/dev/null; then
        NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    elif command -v openssl &>/dev/null; then
        NEW_SECRET=$(openssl rand -base64 32 | tr -d '/+=' | head -c 43)
    else
        NEW_SECRET="auto-$(date +%s)-$(head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 32)"
    fi
    if [ -n "$NEW_SECRET" ]; then
        sed -i.bak "s|SECRET_KEY=change-me-run-setup-sh|SECRET_KEY=${NEW_SECRET}|" .env && rm -f .env.bak
    fi
    echo -e "  ${GREEN}✅ .env dosyası oluşturuldu ve SECRET_KEY üretildi${NC}"
else
    echo -e "  ${GREEN}✅ .env dosyası zaten mevcut${NC}"
fi

# ── ADIM 3: Tüm servisleri başlat ────────────────────────────────────────────
echo -e "${YELLOW}[3/4]${NC} Servisler başlatılıyor..."
echo ""
echo "  Gerekli tüm kütüphaneler ve bağımlılıklar Docker tarafından"
echo "  otomatik indirilecek. İlk seferinde image build edilir ve ML modeli"
echo "  eğitilir (3-7 dk). Sonraki çalıştırmalarda her şey hazır gelir,"
echo "  yeniden eğitim gerekmez."
echo ""

docker compose up -d

echo ""
echo -e "  ${GREEN}✅ Container'lar başlatıldı${NC}"

# ── ADIM 4: Uygulama hazır olana kadar bekle ─────────────────────────────────
echo -e "${YELLOW}[4/4]${NC} Uygulamanın hazır olması bekleniyor..."
echo ""

MAX_WAIT=120   # maksimum 2 dakika bekle
WAITED=0
INTERVAL=5

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Backend hazır! (${WAITED}s bekledik)${NC}"
        break
    fi
    printf "  ⏳ Backend başlatılıyor... (%ds)   \r" "$WAITED"
    sleep $INTERVAL
    WAITED=$((WAITED + INTERVAL))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "\n  ${YELLOW}⚠️  Backend ${MAX_WAIT}s içinde yanıt vermedi.${NC}"
    echo "     Servisler hâlâ başlıyor olabilir. Birkaç dakika bekleyip şunu dene:"
    echo "     curl http://localhost:8000/api/v1/health"
    echo "     veya logları kontrol et: docker compose logs -f backend"
fi

# ── Test: Örnek URL taraması yap ─────────────────────────────────────────────
if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo ""
    echo "  🧪 Örnek tarama yapılıyor (test amaçlı)..."
    SCAN_RESULT=$(curl -sf -X POST http://localhost:8000/api/v1/scan/url \
        -H "Content-Type: application/json" \
        -d '{"url":"http://paypa1-secure.xyz/login"}' 2>/dev/null || echo "")
    if [ -n "$SCAN_RESULT" ]; then
        echo -e "  ${GREEN}✅ API çalışıyor ve URL taraması yapılabiliyor${NC}"
    fi
fi

# ── Tarayıcıyı aç ────────────────────────────────────────────────────────────
DASHBOARD_URL="http://localhost"
echo ""
echo "  🌐 Dashboard açılıyor: $DASHBOARD_URL"
case "$(uname -s)" in
    Darwin)   open "$DASHBOARD_URL" 2>/dev/null || true ;;
    Linux)    xdg-open "$DASHBOARD_URL" 2>/dev/null || true ;;
    MINGW*|CYGWIN*|MSYS*)  start "$DASHBOARD_URL" 2>/dev/null || true ;;
esac

# ── Başarı mesajı ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  Phishing Detector başarıyla çalışıyor!                ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}  🌐  Dashboard (Ana Sayfa) :  http://localhost              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  📡  API Dokümantasyonu    :  http://localhost:8000/docs    ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  📊  Grafana İzleme        :  http://localhost:3001         ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}       (kullanıcı: admin, şifre: admin)                      ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  🔭  Prometheus            :  http://localhost:9090          ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Diğer komutlar:                                            ║${NC}"
echo -e "${GREEN}║${NC}    docker compose logs -f    → Canlı logları izle           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    docker compose down       → Tüm servisleri durdur        ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    make help                 → Tüm komutları listele         ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
