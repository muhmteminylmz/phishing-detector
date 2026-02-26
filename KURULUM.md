# 🛡️ Phishing Detector — Adım Adım Kurulum ve Çalıştırma Rehberi

> Bu rehber, projeyi Windows'ta **sıfırdan** kurup çalıştırman için her adımı somut olarak gösterir.
> Mac/Linux kullanıyorsan doğrudan [Adım 2](#adım-2--projeyi-indir)'ye geçebilirsin.

---

## Adım 1 — Docker Desktop Kur

Docker, uygulamayı tek komutla çalıştırmamızı sağlayan araçtır. Python, veritabanı, Node.js gibi hiçbir şeyi ayrıca kurmana gerek yok — hepsini Docker halleder.

1. **Şu linke git:** https://docs.docker.com/desktop/install/windows-install/
2. **"Download Docker Desktop for Windows"** butonuna tıkla
3. İndirilen `.exe` dosyasını çalıştır ve kurulumu tamamla
4. Bilgisayarı **yeniden başlat** (kurulum bunu isteyecektir)
5. Yeniden başladıktan sonra **Docker Desktop** uygulamasını aç
6. Görev çubuğunda (sağ alt) Docker simgesinin **yeşil** olduğunu doğrula

> **⏳ İlk açılışta** Docker Desktop birkaç dakika hazırlanabilir. "Docker Desktop is running" mesajını bekle.

> **💡 WSL uyarısı çıkarsa:** Docker kurulumu sırasında WSL 2 kurulmasını isteyebilir — "Yes" de ve devam et.

---

## Adım 2 — Projeyi İndir

### Yöntem A: Git ile (önerilen)

Git kuruluysa CMD veya PowerShell aç ve şu komutları gir:

```
git clone https://github.com/muhmteminylmz/phishing-detector
cd phishing-detector
```

### Yöntem B: ZIP olarak (Git yoksa)

1. https://github.com/muhmteminylmz/phishing-detector adresine git
2. Yeşil **"Code"** butonuna tıkla → **"Download ZIP"** seç
3. ZIP dosyasını bir klasöre çıkar (örn. `C:\Users\senin-adi\Desktop\phishing-detector`)
4. CMD veya PowerShell aç ve o klasöre git:
   ```
   cd C:\Users\senin-adi\Desktop\phishing-detector
   ```

---

## Adım 3 — Uygulamayı Başlat

Docker Desktop'ın çalıştığından emin ol (görev çubuğunda yeşil simge), sonra:

### Windows CMD kullanıyorsan:
```
start.bat
```

### Windows PowerShell kullanıyorsan:
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

### Mac veya Linux kullanıyorsan:
```bash
bash start.sh
```

> **⚠️ `bash start.sh` yazınca hata alıyorsan:**
> ```
> WSL ERROR: execvpe(/bin/bash) failed: No such file or directory
> ```
> Bu, WSL kurulu olmadığı anlamına gelir. Sorun değil — yukarıdaki `start.bat` veya PowerShell komutunu kullan.

---

## Adım 4 — Ne Olacak? (Beklenen Çıktılar)

Script çalıştıktan sonra terminalde şu adımları göreceksin:

### 4.1 — Docker Kontrolü
```
[1/4] Docker kontrol ediliyor...
  ✅ Docker hazır
```
→ Docker çalışıyorsa yeşil tik görürsün.

### 4.2 — Yapılandırma Dosyası
```
[2/4] Yapılandırma dosyası kontrol ediliyor...
  ✅ .env dosyası otomatik oluşturuldu
```
→ Ayar dosyası otomatik oluşturulur.

### 4.3 — Servislerin Başlatılması
```
[3/4] Servisler başlatılıyor...

  Gerekli tüm kütüphaneler ve bağımlılıklar Docker tarafından
  otomatik indirilecek. Bu işlem ilk seferinde 2-5 dakika sürebilir.

  ✅ Container'lar başlatıldı
```
→ **İlk seferinde 2-5 dakika sürer** (Docker image'ları indirilir). Sonraki çalıştırmalarda saniyeler sürer.

### 4.4 — Backend Hazırlık Kontrolü
```
[4/4] Uygulamanın hazır olması bekleniyor...
  ⏳ Backend başlatılıyor... (15s)
  ✅ Backend hazır! (20s bekledik)
```
→ Backend'in tamamen başlaması beklenir.

### 4.5 — Başarı Mesajı
```
╔══════════════════════════════════════════════════════════════╗
║  ✅  Phishing Detector başarıyla çalışıyor!                ║
╠══════════════════════════════════════════════════════════════╣
║  🌐  Dashboard (Ana Sayfa) :  http://localhost              ║
║  📡  API Dokümantasyonu    :  http://localhost:8000/docs    ║
║  📊  Grafana İzleme        :  http://localhost:3001         ║
║  🔭  Prometheus            :  http://localhost:9090          ║
╚══════════════════════════════════════════════════════════════╝
```
→ Bu mesajı gördüysen **her şey çalışıyor**! Tarayıcın otomatik açılacak.

---

## Adım 5 — Uygulamayı Kullan

Tarayıcında **http://localhost** adresi otomatik açılacak.

1. URL kutusuna şüpheli bir adres yaz, örneğin: `http://paypa1-secure.xyz/login`
2. **"Tara"** butonuna bas
3. Sonucu gör:
   - **Phishing mi?** → Evet/Hayır
   - **Risk skoru** → 0-100 arası
   - **Risk seviyesi** → LOW / MEDIUM / HIGH / CRITICAL

### API'yi test etmek istersen:

Tarayıcında **http://localhost:8000/docs** adresine git — interaktif API dokümantasyonu açılır. Buradan doğrudan URL taraması yapabilirsin.

---

## Adım 6 — Durdurma ve Tekrar Başlatma

### Uygulamayı durdurmak için:
```
docker compose down
```

### Tekrar başlatmak için:
```
start.bat
```

### Logları canlı izlemek için:
```
docker compose logs -f
```
> `Ctrl+C` ile log izlemeyi durdurabilirsin.

### Sadece backend loglarını görmek:
```
docker compose logs -f backend
```

### Servislerin durumunu kontrol et:
```
docker compose ps
```

---

## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| `bash start.sh` → WSL hatası | `start.bat` veya PowerShell komutu kullan (Adım 3'e bak) |
| "Docker bulunamadı" | Docker Desktop'ı kur ve başlat (Adım 1'e bak) |
| "Docker çalışmıyor" | Docker Desktop uygulamasını aç, yeşil simgeyi bekle |
| Port zaten kullanımda | `docker compose down` yap, sonra tekrar başlat |
| İlk çalıştırma çok yavaş | Normal — Docker image'ları ilk seferinde indirilir (2-5 dk) |
| Backend yanıt vermiyor | `docker compose logs -f backend` ile logları kontrol et |
| Sayfada "502 Bad Gateway" | Backend henüz hazır değil, 1-2 dakika bekle ve sayfayı yenile |

### Vmmem Yüksek Bellek Kullanımı (Windows)

Docker çalışırken görev yöneticisinde `Vmmem` sürecini görebilirsin. Bu normaldir — Docker'ın sanal makinesidir.

Bellek kullanımını sınırlamak için `%USERPROFILE%\.wslconfig` dosyası oluştur:
```ini
[wsl2]
memory=4GB
processors=2
```
Sonra PowerShell'de `wsl --shutdown` çalıştır ve Docker Desktop'ı yeniden başlat.

---

## Dosya Yapısı (Neyin Ne Olduğu)

```
phishing-detector/
├── start.bat              ← Windows CMD için başlatma (çift tıkla)
├── start.ps1              ← Windows PowerShell için başlatma
├── start.sh               ← Mac/Linux için başlatma
├── docker-compose.yml     ← Tüm servislerin tanımı
├── .env.example           ← Örnek ayar dosyası
├── backend/               ← Python FastAPI backend
│   ├── app/               ← API kodları
│   ├── ml/                ← Makine öğrenmesi modeli
│   └── tests/             ← Testler
├── frontend/              ← React dashboard
├── nginx/                 ← Web sunucu ayarları
└── monitoring/            ← Grafana + Prometheus
```
