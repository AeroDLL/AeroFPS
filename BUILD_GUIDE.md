# 🔨 AeroFPS PRO - Build Rehberi

Bu rehber AeroFPS PRO'yu kaynak koddan EXE'ye dönüştürme sürecini açıklar.

---

## 📋 Gereksinimler

### 1. Python Kurulumu

```bash
# Python 3.8 veya üzeri
python --version
```

Python yoksa: https://www.python.org/downloads/

### 2. Bağımlılıkları Yükle

```bash
# Proje klasörüne git
cd AeroFPS

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. PyInstaller Kontrolü

```bash
# PyInstaller versiyonunu kontrol et
pyinstaller --version

# Yoksa yükle
pip install pyinstaller
```

---

## 🚀 Hızlı Build (Otomatik)

En kolay yöntem build scriptini kullanmaktır:

```bash
# Build scriptini çalıştır
python build.py
```

Script size seçenekler sunacak:
1. **Tek dosya/Klasörlü** EXE
2. **Konsol göster/gizle**

Seçiminizi yapın ve bekleyin. EXE `dist/` klasöründe oluşacak.

---

## 🔧 Manuel Build

Build scriptini kullanmak istemiyorsanız:

### Tek Dosya EXE (Önerilen)

```bash
pyinstaller --name=AeroFPS_PRO ^
    --onefile ^
    --clean ^
    --icon=assets/aerofps.ico ^
    --add-data="features;features" ^
    --hidden-import=features.logger ^
    --hidden-import=features.process_manager ^
    --hidden-import=features.temp_monitor ^
    --hidden-import=features.auto_optimizer ^
    --hidden-import=features.updater ^
    --hidden-import=protection ^
    AeroFPS.py
```

### Klasörlü EXE (Daha Hızlı Başlar)

```bash
pyinstaller --name=AeroFPS_PRO ^
    --clean ^
    --icon=assets/aerofps.ico ^
    --add-data="features;features" ^
    --hidden-import=features.logger ^
    --hidden-import=features.process_manager ^
    --hidden-import=features.temp_monitor ^
    --hidden-import=features.auto_optimizer ^
    --hidden-import=features.updater ^
    --hidden-import=protection ^
    AeroFPS.py
```

### Konsol Gizli (Release)

```bash
pyinstaller --name=AeroFPS_PRO ^
    --onefile ^
    --noconsole ^
    --clean ^
    --icon=assets/aerofps.ico ^
    --add-data="features;features" ^
    --hidden-import=features.logger ^
    --hidden-import=features.process_manager ^
    --hidden-import=features.temp_monitor ^
    --hidden-import=features.auto_optimizer ^
    --hidden-import=features.updater ^
    --hidden-import=protection ^
    AeroFPS.py
```

**Not:** `--noconsole` kullanılırsa hatalar görünmez, sadece final release için kullanın!

---

## 📁 Dosya Yapısı

Build öncesi klasör yapısı:

```
AeroFPS/
├── AeroFPS.py              # Ana program
├── protection.py           # Koruma modülü
├── build.py               # Build scripti
├── requirements.txt       # Bağımlılıklar
├── features/              # Özellik modülleri
│   ├── __init__.py
│   ├── logger.py
│   ├── process_manager.py
│   ├── temp_monitor.py
│   ├── auto_optimizer.py
│   └── updater.py
└── assets/               # Icon vb.
    └── aerofps.ico
```

Build sonrası:

```
AeroFPS/
├── ... (önceki dosyalar)
├── build/                # Geçici build dosyaları
├── dist/                 # ÇIKTI KLASÖRÜ
│   └── AeroFPS_PRO.exe   # TEK DOSYALI
│   # VEYA
│   └── AeroFPS_PRO/      # KLASÖRLÜ
│       ├── AeroFPS_PRO.exe
│       ├── features/
│       └── ... (DLL dosyaları)
└── AeroFPS_PRO.spec      # PyInstaller spec dosyası
```

---

## 🎨 Icon Ekleme

### Icon Hazırlama

1. **PNG/JPG'yi ICO'ya çevir:**
   - Online: https://convertio.co/png-ico/
   - Boyut: 256x256 piksel önerilir

2. **Icon dosyasını assets/ klasörüne koy:**
   ```
   assets/aerofps.ico
   ```

3. **Build komutuna ekle:**
   ```bash
   --icon=assets/aerofps.ico
   ```

### Icon Olmadan Build

Icon yoksa `--icon` parametresini kaldırın:

```bash
pyinstaller --name=AeroFPS_PRO ^
    --onefile ^
    --clean ^
    --add-data="features;features" ^
    ...
```

---

## ⚙️ Build Seçenekleri

| Parametre | Açıklama |
|-----------|----------|
| `--onefile` | Tek EXE dosyası (yavaş başlar) |
| `--onedir` | Klasör içinde EXE (hızlı başlar) |
| `--noconsole` | Konsol penc eresini gizle |
| `--console` | Konsol penceresini göster (varsayılan) |
| `--icon=FILE` | Icon dosyası |
| `--name=NAME` | Çıktı dosya adı |
| `--clean` | Önceki build dosyalarını temizle |
| `--add-data=SRC;DEST` | Ek dosyalar ekle |
| `--hidden-import=MODULE` | Gizli modül ekle |

### Önerilen Kombinasyonlar

**Debug/Test:**
```bash
--onefile --console --clean
```

**Release:**
```bash
--onefile --noconsole --clean --icon=assets/aerofps.ico
```

**Hızlı Başlatma:**
```bash
--onedir --console --clean --icon=assets/aerofps.ico
```

---

## 🐛 Sorun Giderme

### ModuleNotFoundError

**Hata:**
```
ModuleNotFoundError: No module named 'features'
```

**Çözüm:**
```bash
--add-data="features;features"
--hidden-import=features.logger
```

### Icon bulunamadı

**Hata:**
```
Unable to find icon file
```

**Çözüm:**
- Icon dosyasının `assets/aerofps.ico` konumunda olduğundan emin olun
- Veya `--icon` parametresini kaldırın

### EXE çok büyük

**Normal Boyutlar:**
- Tek dosya: ~15-25 MB
- Klasörlü: ~10-15 MB (toplam klasör boyutu)

**Küçültme:**
- UPX kullanın (çok önerilmez, antivirüsler flag'ler):
  ```bash
  --upx-dir=C:\upx
  ```

### EXE çalışmıyor

**Kontroller:**
1. **Yönetici haklarıyla çalıştırın** (sağ tıkla → Yönetici olarak çalıştır)
2. **Antivirüs kapalı mı?** (Geçici olarak)
3. **Konsol gösterin** (debug için):
   ```bash
   # --noconsole kaldır
   ```
4. **Loglara bakın:**
   - EXE'yi konsoldan çalıştırın:
     ```bash
     dist\AeroFPS_PRO.exe
     ```

### Antivirüs Uyarısı

**Neden?**
- PyInstaller ile paketlenmiş EXE'ler bazen false positive tetikler
- Normal bir durumdur

**Çözüm:**
1. **VirusTotal'da tarat:**
   - https://www.virustotal.com
   - EXE'yi yükle ve tarama sonuçlarını kontrol et
   - 1-2 antivirüs uyarısı normal (false positive)

2. **Dijital imza ekle** (gelişmiş):
   - Windows Code Signing sertifikası gerekir
   - `signtool` kullan

3. **Kaynak kodu paylaş:**
   - Kullanıcılar kendileri build edebilir

---

## 📦 Dağıtım

### EXE Dağıtımı

1. **`dist/AeroFPS_PRO.exe`** dosyasını alın
2. **ZIP'le** (opsiyonel):
   ```bash
   # PowerShell
   Compress-Archive -Path dist\AeroFPS_PRO.exe -DestinationPath AeroFPS_PRO_v1.0.zip
   ```
3. **README ekle:**
   - Kullanım talimatları
   - Yönetici haklarıyla çalıştırma uyarısı
   - Lisans bilgisi

### Kaynak Kod Dağıtımı

1. **Tüm dosyaları paketleyin:**
   ```
   AeroFPS/
   ├── AeroFPS.py
   ├── protection.py
   ├── requirements.txt
   ├── features/
   └── README.md
   ```

2. **ZIP oluştur:**
   ```bash
   Compress-Archive -Path AeroFPS -DestinationPath AeroFPS_PRO_Source_v1.0.zip
   ```

### Her İkisi de

```
📦 AeroFPS_PRO_v1.0_FULL.zip
├── AeroFPS_PRO.exe              # EXE
├── Source/                      # Kaynak kod
│   ├── AeroFPS.py
│   ├── features/
│   └── ...
├── README.md
├── CHANGELOG.md
└── BUILD_GUIDE.md
```

---

## 🔐 Gelişmiş: Kod Obfuscation

**Not:** PyArmor lisans gerektirir, basit koruma için manuel obfuscation kullanıldı.

### Manuel Obfuscation (Mevcut)

Kodda zaten var:
- Copyright header'ları
- License metinleri
- Watermark sistemi
- First-run setup

### PyArmor (Opsiyonel)

```bash
# PyArmor kurulumu (Ücretli lisans gerektirir)
pip install pyarmor

# Obfuscate
pyarmor obfuscate AeroFPS.py

# Obfuscated dosyayı build et
pyinstaller ... dist/AeroFPS.py
```

---

## 📊 Build Süresi ve Boyut

### Test Sistemi
- CPU: Intel i5-10400
- RAM: 16GB
- SSD: 500GB NVMe

### Sonuçlar

| Build Tipi | Süre | Boyut |
|-----------|------|-------|
| Tek dosya | ~2-4 dk | ~18 MB |
| Klasörlü | ~2-3 dk | ~12 MB (toplam ~25 MB) |
| Konsol gizli | ~2-4 dk | +0 MB |

---

## ✅ Build Checklist

Kontrol listesi:

- [ ] Python 3.8+ kurulu
- [ ] Bağımlılıklar yüklü (`pip install -r requirements.txt`)
- [ ] Tüm modül dosyaları mevcut
- [ ] Icon hazır (opsiyonel)
- [ ] Build scripti çalıştırıldı VEYA manuel komut
- [ ] EXE `dist/` klasöründe oluştu
- [ ] EXE test edildi (çalışıyor)
- [ ] README ve dokümantasyon hazır
- [ ] VirusTotal taraması yapıldı (opsiyonel)
- [ ] Dağıtım paketi oluşturuldu

---

## 🆘 Yardım

Sorun yaşıyorsanız:

1. **Loglara bakın:**
   ```bash
   logs/aerofps.log
   ```

2. **Verbose mode:**
   ```bash
   pyinstaller --log-level=DEBUG ...
   ```

3. **GitHub Issues:**
   - https://github.com/AeroDLL/AeroFPS/issues

4. **Dokümantasyon:**
   - PyInstaller: https://pyinstaller.org/

---

<div align="center">

**AeroFPS PRO Build Guide**

*İyi build'ler! 🚀*

[⬆️ README'ye Dön](README.md) | [📝 Changelog](CHANGELOG.md)

</div>
