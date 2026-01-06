# 🚀 AeroFPS PRO - GitHub'a Yükleme Rehberi

## 📋 Hazırlık

### 1. Gereksiz Dosyaları Sil

Repo'ya **yüklenmemesi** gereken dosyalar (`.gitignore` bunları otomatik atlar):

```bash
# Bu dosyaları manuel olarak silmeyi düşünün (eski web sürümünden):
- api.py
- index.html
- script.js  
- style.css
- .aerofps_installed
```

**Kontrol:**
```bash
cd C:\Users\Emirhan\Desktop\AeroFPS
dir
```

---

## 🔧 Git Kurulumu

### Git Var mı Kontrol

```bash
git --version
```

**Yoksa İndir:** https://git-scm.com/download/win

---

## 📦 GitHub Repo Oluşturma

### Adım 1: GitHub'da Repo Oluştur

1. **GitHub.com'a git** → Giriş yap
2. **New Repository** tıkla
3. **Bilgileri doldur:**
   - Repository name: `AeroFPS`
   - Description: `🎮 Ultimate Windows Gaming Optimization Suite - FPS Boost, Process Manager, System Cleaner & More | PRO Edition`
   - Public ✅
   - **Don't initialize** (README.md zaten var)
4. **Create Repository**

---

### Adım 2: Yerel Repo Başlat

```bash
# AeroFPS klasörüne git
cd C:\Users\Emirhan\Desktop\AeroFPS

# Git başlat
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "🎉 Initial commit - AeroFPS PRO v1.0"
```

---

### Adım 3: GitHub'a Bağla ve Push

**GitHub'dan aldığınız URL'yi kullanın:**

```bash
# Remote ekle (URL'yi kendi repo'nuzla değiştirin)
git remote add origin https://github.com/AeroDLL/AeroFPS.git

# Branch adını main yap
git branch -M main

# Push
git push -u origin main
```

**İlk push'ta GitHub kullanıcı adı ve token isteyecek:**
- Username: GitHub kullanıcı adınız
- Password: **Personal Access Token** (klasik şifre artık çalışmaz)

---

### Adım 4: Personal Access Token Oluştur

**Şifre yerine token gerekli!**

1. GitHub → **Settings** (sağ üst profil)
2. **Developer settings** (en altta)
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token** → **Generate new token (classic)**
5. **Note:** `AeroFPS Upload`
6. **Scopes:** ✅ `repo` (tüm repo yetkisi)
7. **Generate token**
8. **Kopyala** (tekrar gösterilmeyecek!)

**Push komutunda şifre yerine bu token'ı kullan!**

---

## 🏷️ Release Oluşturma

### GitHub'da Release

1. Repo sayfasında **Releases** → **Create a new release**
2. **Tag:** `v1.0` veya `PRO-v1.0`
3. **Title:** `AeroFPS PRO v1.0 - Initial Release`
4. **Description:** CHANGELOG.md'den kopyala
5. **Assets:** EXE dosyasını ekle (opsiyonel):
   ```bash
   python build.py
   # dist/AeroFPS_PRO.exe → GitHub Release'e yükle
   ```
6. **Publish release**

---

## 📝 README Badge Ekle

GitHub'da güzel gözüksün diye README'ye badge ekle:

```markdown
![GitHub Release](https://img.shields.io/github/v/release/AeroDLL/AeroFPS)
![GitHub Stars](https://img.shields.io/github/stars/AeroDLL/AeroFPS)
![GitHub Issues](https://img.shields.io/github/issues/AeroDLL/AeroFPS)
```

---

## 🎯 Repo Ayarları

### Settings → General

- **Features:**
  - ✅ Issues
  - ✅ Discussions (opsiyonel)
  - ❌ Projects
  - ❌ Wiki

### Settings → Pages (GitHub Pages - Opsiyonel)

- Eğer web sitesi yapmak istersen:
  - Source: `main` branch → `/docs` or `/`
  - Ama şu an gerekli değil

---

## 📂 Klasör Yapısı (GitHub'da Görünecek)

```
AeroFPS/
├── .gitignore
├── LICENSE
├── README.md
├── CHANGELOG.md
├── BUILD_GUIDE.md
├── TROUBLESHOOTING.md
├── AeroFPS.py
├── protection.py
├── build.py
├── requirements.txt
├── version.json
├── features/
│   ├── __init__.py
│   ├── logger.py
│   ├── process_manager.py
│   ├── temp_monitor.py
│   ├── auto_optimizer.py
│   └── updater.py
└── assets/
    └── (icon dosyaları)
```

---

## 🔄 Güncelleme Gönderme

**Değişiklik yaptıktan sonra:**

```bash
# Değişiklikleri ekle
git add .

# Commit
git commit -m "✨ Yeni özellik eklendi"

# Push
git push
```

**Commit mesaj örnekleri:**
- `✨ Add new feature`
- `🐛 Fix bug`
- `📝 Update documentation`
- `🔧 Improve performance`
- `♻️ Refactor code`

---

## 🎨 GitHub Profile README

**Bonus:** Projeyi profile ekle

```markdown
## 🎮 AeroFPS PRO

[![GitHub](https://img.shields.io/badge/AeroFPS-PRO-blue)](https://github.com/AeroDLL/AeroFPS)

Ultimate Windows Gaming Optimization Suite
```

---

## ✅ Checklist

**Yüklemeden önce kontrol et:**

- [ ] Git kurulu
- [ ] GitHub hesabı aktif
- [ ] Repo oluşturuldu
- [ ] Gereksiz dosyalar silindi/ignore edildi
- [ ] `.gitignore` dosyası var
- [ ] `LICENSE` dosyası var
- [ ] `README.md` güncel
- [ ] Personal Access Token oluşturuldu

**Push sonrası kontrol:**

- [ ] Tüm dosyalar yüklendi mi?
- [ ] README düzgün görünüyor mu?
- [ ] License seçildi mi?
- [ ] About bölümü dolu mu? (Description, Website, Topics)

---

## 🏷️ Topics Ekle

**Repo → Settings → Topics:**

```
windows, optimization, fps-boost, gaming, performance, 
system-cleaner, python, process-manager, gaming-tools, 
windows-10, windows-11, fps-optimizer, game-optimizer
```

---

## 🚀 Başarılar!

Artık projen GitHub'da! 

**Link:** `https://github.com/AeroDLL/AeroFPS`

**Paylaş:**
- Twitter
- Reddit (r/pcgaming, r/pcmasterrace)
- Discord sunucuları

---

## 💡 İpuçları

1. **README görünümü:** GitHub'da README önizlemesi için `Preview` kullan
2. **Issues:** Kullanıcılar bug rapor edebilir
3. **Pull Requests:** Başkaları katkıda bulunabilir
4. **Star:** İnsanlar projeyi beğenirse star atar
5. **Watch:** İnsanlar güncellemeleri takip edebilir

**Good luck!** 🎉
