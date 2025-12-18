# 🚀 AeroFPS v7.0 | Ultimate Windows Gaming Suite

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**AeroFPS**, Windows işletim sistemini oyunlar için optimize eden, gereksiz servisleri kapatan, RAM'i temizleyen ve giriş gecikmesini (Input Lag) düşüren gelişmiş bir açık kaynaklı sistem aracıdır.

> ⚠️ **UYARI:** Bu araç sistem kayıt defterinde (Registry) köklü değişiklikler yapar. Kullanmadan önce menüdeki **[3]** numaralı seçenek ile yedek almanız önerilir.

---

## 🔥 Özellikler (20+ Araç)

### 🚀 Performans
- **Ultimate FPS Boost:** Güç planını nihai performansa çeker.
- **CPU Optimizasyonu:** İşlemciyi oyunlara öncelik verecek şekilde ayarlar.
- **GPU Turbo Mode:** NVIDIA/AMD kartlar için donanım hızlandırmayı açar.
- **RAM Cleaner:** Şişen belleği (Working Set) temizler.

### 🌐 Ağ & İnternet
- **DNS Optimizer:** Cloudflare (1.1.1.1) veya Google DNS ile pingi düşürür.
- **Network Repair:** Lag ve paket kaybı için TCP/IP yığınını sıfırlar.
- **Wi-Fi Boost:** Ağ darbolazını (Throttling) kapatır.

### 🛠️ Sistem Araçları
- **Repair Station:** `SFC` ve `DISM` ile bozuk Windows dosyalarını onarır.
- **Software Updater:** Bilgisayardaki tüm programları tek tıkla günceller (`winget`).
- **Startup Manager:** Başlangıçta açılan gereksiz programları listeler.
- **Deep Clean:** Temp, Prefetch, DNS Cache ve Log dosyalarını siler.

### 🛡️ Gizlilik & Güvenlik
- **Privacy Shield:** Windows telemetri ve takip servislerini engeller.
- **Defender Control:** Oyun sırasında antivirüs taramasını durdurur.

---

## 📦 Kurulum & Kullanım

### Yöntem 1: Hazır EXE (Önerilen)
Python kurmakla uğraşmak istemiyorsanız:
1. Sağ taraftaki **[Releases]** kısmından son sürümü (`AeroFPS.exe`) indirin.
2. Sağ tıklayıp **"Yönetici Olarak Çalıştır"** deyin.
3. Menüden istediğiniz işlemi seçin.

### Yöntem 2: Kaynak Koddan Çalıştırma
Geliştirici iseniz:
```bash
# Repoyu klonlayın
git clone [https://github.com/AeroDLL/FPS-BOOSTER-.git](https://github.com/AeroDLL/FPS-BOOSTER-.git)

# Gerekli kütüphaneleri kurun
pip install colorama

# Başlatın
python AeroFPS.py
