# 🔧 AeroFPS PRO - Bilinen Sorunlar ve Çözümler

## ✅ Düzeltilen Sorunlar

### 1. ❌ → ✅ Güncelleme Kontrolü Hatası

**Sorun:** "İnternet bağlantısı yok veya GitHub'a erişilemiyor"

**Sebep:**
- GitHub API erişim kısıtlamaları
- Firewall/Proxy engeli
- SSL sertifika sorunları
- Türkiye'de bazen GitHub erişimi sorunlu olabiliyor

**Çözüm:** ✅ Düzeltildi
- Çoklu kaynak desteği eklendi (GitHub API + Raw JSON)
- SSL doğrulama bypass
- Timeout süresi artırıldı (5s → 10s)
- User-Agent değiştirildi
- Manuel kontrol seçeneği
- Detaylı hata mesajları

**Şimdi:** Programı internet olmadan da kullanabilirsiniz, güncelleme kontrolü opsiyoneldir.

---

## ⚠️ Kullanıcı Dikkat Etmesi Gerekenler

### 1. Windows Defender Kontrolü

**Bazı durumlarda çalışmayabilir:**
- Windows 11 Home Edition
- Windows Enterprise (Yönetici politikası)
- Antivirüs yazılımı yüklüyse

**Önerimiz:** 
- Defender'ı kapatmak yerine "Dışlama" ekleyin
- Oyun klasörünü Defender dışlamalarına ekleyin
- Oyun bitince mutlaka tekrar açın

---

### 2. BCD Tweaks

**Restart gerektirir!**
- BCD değişiklikleri yeniden başlatma olmadan aktif olmaz
- Eğer Windows boot etmezse, `bcdedit /deletevalue` ile geri alabilirsiniz

**Güvenli kullanım:**
- Önce sistem geri yükleme noktası oluşturun
- Sadece deneyimliyseniz kullanın

---

### 3. Servis Kapatma

**Bazı servisler tekrar açılabilir:**
- Windows Update servisleri otomatik başlar
- Belirli uygulamalar servis açabilir

**Normal:** Bu beklenen bir davranıştır.

---

### 4. CPU Sıcaklığı

**Bazı sistemlerde okunamaz:**
- Laptop'larda genelde çalışır
- Desktop'larda BIOS bağımlı
- WMI desteği gerekir

**Alternatif:** 
- HWMonitor
- MSI Afterburner
- BIOS/UEFI ekranı

---

### 5. Network Adaptör Tespiti

**Özel/Sanal adaptörler tespit edilmeyebilir:**
- VPN adaptörleri
- Sanal makine adaptörleri
- Bluetooth adaptörleri

**Çözüm:** Manuel olarak adaptör adını kontrol edip DNS ayarlarını yapın.

---

## 🐛 Küçük Hatalar (Kritik Değil)

### 1. Syntax Warnings

**Ne:** Python bazı string'lerde escape sequence uyarısı verir
```
SyntaxWarning: invalid escape sequence '\S'
```

**Etki:** Yok, program düzgün çalışır

**Sebep:** Registry path'lerinde `\` kullanımı

**Düzeltmek için:** Raw string kullan (`r"..."`) ama gerek yok.

---

### 2. Admin Hakları Tekrar İsteğ i

**Ne:** Bazen program kapanıp tekrar açılabilir

**Sebep:** Windows UAC davranışı

**Çözüm:** Programı ilk baştan "Yönetici olarak çalıştır" ile açın

---

## 💡 Performans İpuçları

### En İyi Sonuç İçin

1. **İlk Kullanım:**
   ```
   [5] Güvenlik Yedeği → [0] One-Click Optimize → Restart
   ```

2. **Oyun Öncesi:**
   ```
   [3] Process Manager → Arka plan temizle
   [4] Sıcaklık İzle → Kontrol et
   ```

3. **Sorun Varsa:**
   ```
   [23] Logları görüntüle → Detayları kontrol et
   [25] Sıfırla → Tüm ayarları geri al
   ```

---

## 🔄 EXE Build Sorunları

### 1. "Modül bulunamadı" hatası

**Çözüm:**
```bash
pip install -r requirements.txt
python build.py
```

### 2. Antivirüs EXE'yi siliyor

**Çözüm:**
- False positive (normal)
- VirusTotal'da tarat
- Windows Defender'a dışlama ekle:
  - Ayarlar → Güvenlik → Virüs koruması → Dışlamalar
  - `C:\Users\[Kullanıcı]\Desktop\AeroFPS` klasörünü ekle

### 3. EXE çok büyük

**Normal Boyut:** 15-25 MB (PyInstaller tüm Python runtime'ı içerir)

**Küçültmek için:** UPX kullanabilirsiniz ama antivirüsler daha çok tepki verir.

---

## 📞 Destek

### Sorun Bildirme

1. **Loglara bakın:** `[23] Log Görüntüle`
2. **GitHub Issues:** https://github.com/AeroDLL/AeroFPS/issues
3. **Log dosyasını paylaşın:** `logs/aerofps.log`

### Sık Sorulan Sorular

**S: Program başlamıyor?**
A: Yönetici olarak çalıştırıyor musunuz?

**S: Bir özellik çalışmadı?**
A: Normal, bazı özellikler sistem bağımlıdır. Loglara bakın.

**S: FPS artışı göremedim?**
A: 
- Restart yaptınız mı?
- Oyununuz CPU/GPU bottleneck'te mi?
- Driver'larınız güncel mi?

**S: Ayarları geri almak istiyorum?**
A: `[25] Sıfırla` seçeneğini kullanın veya sistem geri yükleme noktasından dönün.

---

## ✅ Test Edildi ve Çalışıyor

- ✅ Windows 10 (20H2+)
- ✅ Windows 11
- ✅ Python 3.8 - 3.12
- ✅ Admin haklarıyla
- ✅ Offline mod (güncelleme hariç)
- ✅ EXE build
- ✅ Tüm temel özellikler

---

**Son Güncelleme:** 06.01.2026  
**Versiyon:** PRO v1.1  
**Durum:** Stabil ✅
