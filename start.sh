#!/bin/bash
# =============================================================================
#  Phishing Detector – Tek Tuşla Başlat
#  Kullanım: bash start.sh
#
#  Bu script:
#    ✅ Docker'ı kontrol eder (yoksa nasıl kuracağını gösterir)
#    ✅ Gerekli tüm kütüphaneleri otomatik indirir
#    ✅ Veritabanını, backend'i ve frontend'i başlatır
#    ✅ Uygulama hazır olana kadar bekler
#    ✅ Tarayıcıyı otomatik açar
# =============================================================================
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/setup.sh" "$@"
