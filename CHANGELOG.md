# 📋 AeroFPS PRO - Changelog

Tüm önemli değişiklikler bu dosyada belgelenir.

---

## [PRO v1.1] - 2026-03-01

### 🎉 Büyük Güncelleme - 4 Yeni Özellik!

### ✨ Yeni Özellikler

#### 🌐 Network Ping Optimizer
- **Gerçek Zamanlı Ping Monitör**
  - Popüler oyun sunucularına ping testi (Valorant, CS2, Fortnite, League)
  - Cloudflare ve Google DNS ping kontrolü
  - Packet loss tespiti
  - Jitter (ping dalgalanması) gösterimi
  - Renkli ping gösterimi (yeşil/sarı/kırmızı)

- **Gelişmiş Network Tweaks**
  - TCP Window Auto-Tuning
  - Network Throttling Index optimizasyonu
  - TCP Chimney Offload
  - RSS (Receive Side Scaling)
  - Direct Cache Access
  - ECN Capability
  - TCP Timestamps
  - QoS Packet Scheduler optimizasyonu

- **Otomatik DNS Optimizer**
  - En hızlı DNS'i otomatik bulma
  - Cloudflare, Google, Quad9, OpenDNS karşılaştırması
  - Tek tıkla en iyi DNS'i uygulama
  - Tüm aktif adaptörlere otomatik uygulama

- **Network Reset**
  - Winsock reset
  - TCP/IP stack reset
  - DNS cache temizleme

#### 🤖 Akıllı Öneri Sistemi
- **Sistem Analizi**
  - CPU çekirdek ve thread sayısı
  - CPU frekans bilgisi
  - RAM kapasitesi ve kullanım yüzdesi
  - Disk tipi tespiti (SSD/HDD)
  - Windows versiyonu
  - Başlangıç programları sayısı
  - Arka plan process sayısı

- **Kişiselleştirilmiş Öneriler**
  - Yüksek öncelikli öneriler (kırmızı)
  - Orta öncelikli öneriler (sarı)
  - Düşük öncelikli öneriler (mavi)
  - Her öneri için beklenen FPS kazancı
  - Hangi menüden uygulanacağı bilgisi

- **Hızlı Aksiyon**
  - Tüm önerileri otomatik uygulama
  - Sadece yüksek öncelikli önerileri uygulama
  - Manuel uygulama seçeneği

- **Akıllı Tespit**
  - Düşük RAM uyarısı (<8GB)
  - Yüksek RAM kullanımı uyarısı (>80%)
  - HDD kullanımı uyarısı (SSD önerisi)
  - Fazla başlangıç programı uyarısı (>10)
  - Fazla arka plan process uyarısı (>150)
  - Windows 11 VBS optimizasyonu önerisi

#### 🎨 Oyun İçi Ayar Önerileri
- **Desteklenen Oyunlar**
  - Counter-Strike 2 (CS2)
  - Valorant
  - Fortnite
  - Apex Legends

- **Config Profilleri**
  - Competitive (Max FPS) profili
  - Balanced (Quality + FPS) profili
  - Her oyun için özel ayarlar

- **Otomatik Tespit**
  - Yüklü oyunları otomatik bulma
  - Config dosyası varlık kontrolü
  - Config klasörü otomatik oluşturma

- **Config Yönetimi**
  - Otomatik yedekleme (.backup)
  - Config dosyası oluşturma
  - Ayarları önizleme
  - Tek tıkla uygulama

- **Genel Öneriler**
  - Low-End PC için ayarlar
  - Mid-Range PC için ayarlar
  - High-End PC için ayarlar
  - Beklenen FPS aralıkları
  - Grafik ayarları ipuçları

#### ⏰ Zamanlanmış Optimizasyon
- **Otomatik Görevler**
  - Günlük Temizlik (temp dosyalar, DNS cache)
  - Haftalık Optimizasyon (tam sistem optimizasyonu)
  - Oyun Öncesi Hazırlık (RAM temizliği, process optimizasyonu)
  - Başlangıç Optimizasyonu (Windows başlangıcında)

- **Windows Task Scheduler Entegrasyonu**
  - Otomatik görev oluşturma
  - Görev silme
  - Görev durumu kontrolü
  - SYSTEM yetkisiyle çalışma

- **Esnek Zamanlama**
  - Saat bazlı zamanlama
  - Gün bazlı zamanlama (Pazartesi-Pazar)
  - Startup trigger
  - Özelleştirilebilir zamanlar

- **Görev Yönetimi**
  - Görevleri aktif/pasif yapma
  - Görevleri test etme (şimdi çalıştır)
  - Tüm görevleri temizleme
  - Görev durumunu görüntüleme

- **JSON Tabanlı Yapılandırma**
  - schedule.json dosyası
  - Kolay düzenleme
  - Yedekleme ve geri yükleme

### 🔧 İyileştirmeler

- **Kod Kalitesi**
  - 4 yeni modül eklendi (network_optimizer, smart_advisor, game_config_optimizer, scheduler)
  - Modüler yapı genişletildi
  - Hata yönetimi iyileştirildi
  - Log entegrasyonu tüm yeni özelliklerde

- **Kullanıcı Deneyimi**
  - 4 yeni menü öğesi (27-30)
  - Daha detaylı bilgilendirme mesajları
  - Renkli ve görsel feedback
  - Progress göstergeleri

- **Performans**
  - Network testleri optimize edildi
  - Sistem analizi hızlandırıldı
  - Config dosyası işlemleri optimize edildi

### 🔄 Değiştirilen

- **Versiyon**: PRO v1.0 → PRO v1.1
- **Menü Sayısı**: 26 → 30 seçenek
- **Modül Sayısı**: 6 → 10 modül
- **README.md**: Yeni özellikler eklendi
- **requirements.txt**: requests kütüphanesi eklendi

### 🐛 Düzeltilen

- Network adaptör tespiti iyileştirildi
- DNS uygulama hatası düzeltildi
- Config dosyası encoding sorunları çözüldü
- Windows Task Scheduler uyumluluk sorunları giderildi

### 📦 Yeni Dosyalar

- `features/network_optimizer.py` - Network ping optimizer modülü
- `features/smart_advisor.py` - Akıllı öneri sistemi modülü
- `features/game_config_optimizer.py` - Oyun config optimizer modülü
- `features/scheduler.py` - Zamanlanmış optimizasyon modülü
- `schedule.json` - Zamanlama yapılandırma dosyası (otomatik oluşur)

### 🎯 Toplam İstatistikler

- **Toplam Özellik**: 30+ özellik
- **Kod Satırı**: ~3500+ satır
- **Modül Sayısı**: 10 modül
- **Desteklenen Oyun**: 20+ oyun (process manager) + 4 oyun (config optimizer)
- **Network Tweaks**: 8 farklı optimizasyon
- **Zamanlanmış Görev**: 4 hazır görev

### ⚠️ Bilinen Sorunlar

- Bazı antivirüs programları network tweaks'i engelleyebilir
- Windows 11'de bazı WMI komutları çalışmayabilir (normal)
- Config dosyaları oyun güncellemelerinde sıfırlanabilir
- Task Scheduler bazı Windows Home sürümlerinde kısıtlı olabilir

### 🔮 Gelecek Sürümler İçin Planlar

- [ ] Daha fazla oyun config desteği (Overwatch, R6S, PUBG)
- [ ] VPN ping testi
- [ ] Benchmark karşılaştırma sistemi
- [ ] Cloud sync (ayarları buluta kaydetme)
- [ ] Discord Rich Presence entegrasyonu
- [ ] Oyun FPS overlay (gerçek zamanlı)

---

## [PRO v1.0] - 2026-01-06

### 🎉 İlk PRO Sürümü

v8.0'dan PRO versiyonuna geçiş. Kapsamlı kod yeniden yazımı ve yeni özellikler.

### ✨ Yeni Özellikler

#### 🚀 Ana Özellikler
- **One-Click Optimize** - Tüm optimizasyonları tek tuşla uygulama
  - Progress bar ile görsel geri bildirim
  - 12 farklı optimizasyon adımı
  - İşlem sonrası detaylı rapor
  
- **Process Manager** - Gelişmiş process yönetimi
  - Popüler oyunları otomatik tespit
  - Oyun önceliğini "High Priority" yapma
  - Gereksiz arka plan uygulamalarını kapatma
  - Manuel process ekleme desteği

- **Sıcaklık & Kaynak İzleme**
  - CPU kullanımı gösterimi
  - RAM kullanımı gösterimi
  - CPU sıcaklığı izleme (destekleyen sistemlerde)
  - Renkli progress bar'lar
  - Sıcaklık uyarı sistemi

- **Log Sistemi**
  - Tüm işlemlerin otomatik kaydı
  - Tarih/saat damgalı loglar
  - Log görüntüleme arayüzü
  - Log temizleme özelliği

- **Otomatik Güncelleme Kontrolü**
  - GitHub API entegrasyonu
  - Versiyon karşılaştırması
  - Yayın notlarını gösterme
  - Direkt indirme linki

#### 🔧 İyileştirmeler

- **Kod Kalitesi**
  - Tüm fonksiyonlara hata yönetimi (try-catch)
  - Timeout kontrolü ekle lendi
  - Return code kontrolü
  - Detaylı hata mesajları

- **Admin Kontrolü**
  - Sonsuz döngü düzeltildi
  - Argüman kontrolü ile tekrar başlatmayı önleme
  - Hata durumunda kullanıcıya açıklayıcı mesaj

- **Network Adaptör Tespiti**
  - Dinamik adaptör listesi
  - Sabit "Ethernet"/"Wi-Fi" yerine otomatik tespit
  - Aktif adaptörleri bulma

- **Kullanıcı Deneyimi**
  - Modern, renkli banner
  - Emoji'li menü öğeleri
  - Daha iyi mesaj formatlaması
  - Progress indicator'lar
  - Başarı/hata durumlarında görsel feedback

#### 🛡️ Güvenlik & Koruma

- **İlk Çalıştırma Kurulumu**
  - Lisans onay ekranı
  - Watermark gösterimi
  - First-run flag dosyası

- **Kod Koruma**
  - Copyright header'ları
  - Anti-piracy uyarıları
  - License metni koruması
  - File integrity check (opsiyonel)

#### 📦 Build & Dağıtım

- **Build Script**
  - Otomatik PyInstaller build
  - Icon desteği
  - Tek dosya/klasörlü seçenekler
  - Konsol göster/gizle seçenekleri
  - Build süresi ve boyut raporu

- **Dokümantasyon**
  - Detaylı README.md (TR/EN)
  - BUILD_GUIDE.md
  - CHANGELOG.md
  - requirements.txt

### 🔄 Değiştirilen

- **Versiyon İsimleri**: v8.0 → PRO v1.0
- **Banner Tasarımı**: Daha modern ve gösterişli
- **Menü Düzeni**: Daha organize ve kategorize
- **Dil Sistemi**: Geliştirilmiş T() fonksiyonu
- **Title Yönetimi**: Her ekran için özel başlık

### 🐛 Düzeltilen

- ❌ Admin rechte sonsuz döngü
- ❌ Sabit ağ adaptör adları sorunu
- ❌ Hata durumlarında program crash'i
- ❌ Sessiz hata lar (kullanıcı bilgilendirilmiyordu)
- ❌ Log kaydı olmayan işlemler
- ❌ Tehlikeli işlemler için onay eksikliği

### 🗑️ Kaldırılan

- Flask/Flask-CORS bağımlılıkları (gerekli değildi)
- pywin32 bağımlılığı (native ctypes kullanıldı)
- Web server özellikleri (PRO terminal-based)
- Overclock özellikleri (kullanıcı isteği)

### ⚠️ Bilinen Sorunlar

- Bazı sistemlerde CPU sıcaklığı okunamayabilir (WMIC kısıtlaması)
- Defender kapatma işlemi bazı Windows sürümlerinde çalışmayabilir
- Network adaptör tespiti bazı özel adaptörlerde başarısız olabilir

### 🔮 Gelecek Sürümler İçin Planlar

- [ ] GUI versiyonu (Tkinter/PyQt5)
- [ ] Oyun profilleri kaydetme/yükleme
- [ ] Otomatik güncelleme indirme ve kurma
- [ ] Daha fazla dil desteği (Rusça, İspanyolca, vb.)
- [ ] Portable versiyon (Registry değişikliği yok)
- [ ] Konfigürasyon export/import
- [ ] Gelişmiş benchmark araçları

---

## [v8.0] - Önceki Versiyon

### Özellikler (Eski)
- Temel FPS boost optimizasyonları
- Sistem temizliği
- DNS optimizer
- GPU ayarları
- BCD tweaks
- Gaming runtimes installer

### Sorunlar
- Hata yönetimi eksik
- Log sistemi yok
- Admin kontrolü sorunlu
- Sabit network adaptörleri
- Modüler yapı yok

---

## Versiyon Notasyonu

Format: `[TİP] [vX.Y.Z] - YYYY-MM-DD`

- **TİP**: PRO, BETA, RC, vb.
- **X**: Major versiyon (büyük değişiklikler)
- **Y**: Minor versiyon (yeni özellikler)
- **Z**: Patch versiyon (hata düzeltmeleri)

### Değişiklik Kategorileri

- ✨ **Yeni Özellikler** - Added
- 🔄 **Değiştirilen** - Changed
- 🐛 **Düzeltilen** - Fixed
- 🗑️ **Kaldırılan** - Removed
- ⚠️ **Kullanımdan Kaldırılacak** - Deprecated
- 🛡️ **Güvenlik** - Security

---

<div align="center">

**AeroFPS PRO Changelog**

*Son Güncellenme: 2026-01-06*

[⬆️ README'ye Dön](README.md)

</div>
