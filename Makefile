# =============================================================================
#  Phishing Detector – Makefile
#  Tüm komutlar için: make help
# =============================================================================

.DEFAULT_GOAL := help
.PHONY: help start stop restart logs status dev dev-stop test train clean build open

# ── Renkler / Colors ──────────────────────────────────────────────────────────
BLUE  := \033[34m
GREEN := \033[32m
RESET := \033[0m

## ─────────────────────────────────────────────────────────────────────────────
## HIZLI BAŞLANGIÇ / QUICK START
## ─────────────────────────────────────────────────────────────────────────────

help: ## Bu yardım mesajını göster / Show this help
	@echo ""
	@echo "  $(BLUE)🛡️  Phishing Detector$(RESET)"
	@echo ""
	@echo "  $(GREEN)Docker ile çalıştır (önerilen):$(RESET)"
	@echo "    make start       → Kütüphaneleri indir, başlat, tarayıcı aç (tek tuş)"
	@echo "    make open        → Tarayıcıda dashboard'u aç"
	@echo "    make stop        → Tüm servisleri durdur"
	@echo "    make restart     → Servisleri yeniden başlat"
	@echo "    make logs        → Canlı logları izle"
	@echo "    make status      → Servis durumlarını göster"
	@echo "    make clean       → Volume'ları ve container'ları sil"
	@echo ""
	@echo "  $(GREEN)Yerel geliştirme (hot-reload):$(RESET)"
	@echo "    make dev         → Backend + DB/Redis'i başlat (hot-reload)"
	@echo "    make dev-stop    → Yerel geliştirme servislerini durdur"
	@echo ""
	@echo "  $(GREEN)Diğer:$(RESET)"
	@echo "    make test        → Backend testlerini çalıştır"
	@echo "    make train       → ML modelini yeniden eğit"
	@echo "    make build       → Docker image'larını yeniden build et"
	@echo ""
	@echo "  📖 Detaylı döküman: README.md"
	@echo ""

## ─────────────────────────────────────────────────────────────────────────────
## DOCKER (ÜRETİM BENZERİ) / DOCKER (PRODUCTION-LIKE)
## ─────────────────────────────────────────────────────────────────────────────

start: ## Tüm servisleri başlat – kütüphaneleri indirir, hazır olunca tarayıcı açar
	@bash scripts/setup.sh

open: ## Tarayıcıda dashboard'u aç
	@case "$$(uname -s)" in \
		Darwin)  open http://localhost ;; \
		Linux)   xdg-open http://localhost 2>/dev/null || sensible-browser http://localhost 2>/dev/null || echo "http://localhost adresini tarayıcında aç" ;; \
		*)       echo "http://localhost adresini tarayıcında aç" ;; \
	esac

stop: ## Tüm Docker servislerini durdur
	docker compose down
	@echo "$(GREEN)✅ Tüm servisler durduruldu.$(RESET)"

restart: stop start ## Servisleri yeniden başlat

logs: ## Canlı Docker loglarını izle (Ctrl+C ile çık)
	docker compose logs -f

status: ## Servis durumlarını göster
	docker compose ps

build: _ensure_env ## Docker image'larını yeniden build et
	docker compose build --no-cache
	@echo "$(GREEN)✅ Build tamamlandı.$(RESET)"

clean: ## Container'ları, volume'ları ve image'ları sil (veri silinir!)
	@echo "⚠️  Tüm veriler silinecek. Devam etmek için Enter'a bas, iptal için Ctrl+C"
	@read _confirm
	docker compose down -v --rmi local
	@echo "$(GREEN)✅ Temizlendi.$(RESET)"

## ─────────────────────────────────────────────────────────────────────────────
## YEREL GELİŞTİRME / LOCAL DEVELOPMENT  (hot-reload)
## ─────────────────────────────────────────────────────────────────────────────

dev: _ensure_env ## Veritabanı/Redis Docker'da, backend+frontend hot-reload ile
	@echo "$(GREEN)▶  Geliştirme ortamı başlatılıyor...$(RESET)"
	@echo "   PostgreSQL ve Redis Docker ile başlatılıyor..."
	docker compose -f docker-compose.dev.yml up -d postgres redis
	@echo ""
	@echo "   Backend sanal ortam hazırlanıyor..."
	@cd backend && \
		([ -d .venv ] || python3 -m venv .venv) && \
		.venv/bin/pip install -q --upgrade pip && \
		.venv/bin/pip install -q -r requirements.txt
	@echo ""
	@echo "$(GREEN)✅ Geliştirme ortamı hazır!$(RESET)"
	@echo ""
	@echo "  Şimdi ayrı terminallerde şunları çalıştır:"
	@echo ""
	@echo "  $(BLUE)Terminal 1 – Backend:$(RESET)"
	@echo "    cd backend"
	@echo "    source .venv/bin/activate"
	@echo "    uvicorn app.main:app --reload --port 8000"
	@echo ""
	@echo "  $(BLUE)Terminal 2 – Frontend:$(RESET)"
	@echo "    cd frontend"
	@echo "    npm install && npm run dev"
	@echo ""
	@echo "  📡 Backend : http://localhost:8000/docs"
	@echo "  🌐 Frontend: http://localhost:3000"

dev-stop: ## Yerel geliştirme Docker servislerini durdur
	docker compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✅ Geliştirme servisleri durduruldu.$(RESET)"

## ─────────────────────────────────────────────────────────────────────────────
## TEST VE MODEL
## ─────────────────────────────────────────────────────────────────────────────

test: ## Backend birim testlerini çalıştır
	@echo "$(GREEN)▶  Testler çalıştırılıyor...$(RESET)"
	@cd backend && \
		([ -d .venv ] && .venv/bin/pip show pytest > /dev/null 2>&1 || pip install -q -r requirements.txt) && \
		([ -d .venv ] && .venv/bin/pytest tests/ -v || pytest tests/ -v)

train: ## ML modelini yeniden eğit (Docker içinde)
	@echo "$(GREEN)▶  ML modeli eğitiliyor...$(RESET)"
	docker compose exec backend python ml/train.py
	@echo "$(GREEN)✅ Model eğitimi tamamlandı.$(RESET)"

## ─────────────────────────────────────────────────────────────────────────────
## İÇ HEDEFLER / INTERNAL
## ─────────────────────────────────────────────────────────────────────────────

_ensure_env:
	@if [ ! -f .env ]; then \
		echo "$(BLUE)ℹ️  .env dosyası bulunamadı, .env.example'dan oluşturuluyor...$(RESET)"; \
		cp .env.example .env; \
		NEW_SECRET=$$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32 | tr -d '/+=' | head -c 43); \
		if [ -n "$$NEW_SECRET" ]; then \
			sed -i.bak "s|SECRET_KEY=change-me-run-setup-sh|SECRET_KEY=$$NEW_SECRET|" .env && rm -f .env.bak; \
		fi; \
		echo "$(GREEN)✅ .env dosyası oluşturuldu ve SECRET_KEY üretildi.$(RESET)"; \
	fi
