# 📋 AeroFPS PRO - Changelog

Tüm önemli değişiklikler bu dosyada belgelenir.

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
