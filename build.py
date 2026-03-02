"""
AeroFPS PRO - EXE Build Script
PyInstaller kullanarak EXE oluşturur
"""

import os
import subprocess
import sys
from datetime import datetime

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                  AeroFPS PRO - BUILD SCRIPT                            ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

# Gerekli dosyaların kontrolü
required_files = [
    "AeroFPS.py",
    "protection.py",
    "features/__init__.py",
    "features/logger.py",
    "features/process_manager.py",
    "features/temp_monitor.py",
    "features/auto_optimizer.py",
    "features/updater.py"
]

print("📋 Dosya kontrolü yapılıyor...")
missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)
        print(f"   ❌ Eksik: {file}")
    else:
        print(f"   ✅ Bulundu: {file}")

if missing_files:
    print(f"\n❌ Eksik dosyalar bulundu! Lütfen tüm dosyaların yerinde olduğundan emin olun.")
    sys.exit(1)

print("\n✅ Tüm dosyalar mevcut!\n")

# PyInstaller kontrolü
print("🔧 PyInstaller kontrolü...")
try:
    import PyInstaller
    print("   ✅ PyInstaller kurulu\n")
except ImportError:
    print("   ❌ PyInstaller bulunamadı!")
    print("\n🔧 PyInstaller kuruluyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("   ✅ PyInstaller kuruldu!\n")

# Build seçenekleri
print("╔═══════════════════════════════════════════════════════════════════════╗")
print("║                        BUILD SEÇENEKLERİ                               ║")
print("╚═══════════════════════════════════════════════════════════════════════╝\n")

print("  [1] Tek dosya EXE (Önerilen - Daha yavaş başlar)")
print("  [2] Klasörlü EXE (Daha hızlı başlar)")
print("  [3] Konsol gizli (Release için)")
print("  [4] Konsol görünür (Debug için)")

build_type = input("\n  Build tipi (1-4) [Varsayılan: 1]: ").strip() or "1"
console_mode = input("  Konsol modu (3-4) [Varsayılan: 4]: ").strip() or "4"

# Build komutu oluştur
cmd = [
    "pyinstaller",
    "--name=AeroFPS_PRO",
    "--clean",
]

# Icon ekle (varsa)
if os.path.exists("assets/aerofps.ico"):
    cmd.append("--icon=assets/aerofps.ico")
    print("\n  ✅ Icon eklendi")

# Tek dosya/klasörlü
if build_type == "1":
    cmd.append("--onefile")
    print("  📦 Tek dosya EXE oluşturulacak")
else:
    print("  📦 Klasörlü EXE oluşturulacak")

# Konsol modu
if console_mode == "3":
    cmd.append("--noconsole")
    print("  🖥️  Konsol gizli")
else:
    print("  🖥️  Konsol görünür")

# Data files ekle
cmd.extend([
    "--add-data=features;features",
    "--hidden-import=features.logger",
    "--hidden-import=features.process_manager",
    "--hidden-import=features.temp_monitor",
    "--hidden-import=features.auto_optimizer",
    "--hidden-import=features.updater",
    "--hidden-import=protection",
])

# Ana dosya
cmd.append("AeroFPS.py")

print("\n" + "="*70)
print(f"🚀 BUILD BAŞLIYOR...")
print("="*70 + "\n")

print("⏳ Bu işlem birkaç dakika sürebilir...\n")

# Build başlat
build_start = datetime.now()
result = subprocess.run(cmd)

if result.returncode == 0:
    build_end = datetime.now()
    build_time = (build_end - build_start).total_seconds()
    
    print("\n" + "="*70)
    print("✅ BUILD BAŞARILI!")
    print("="*70)
    print(f"\n⏱️  Süre: {build_time:.1f} saniye")
    
    # EXE konumu
    if build_type == "1":
        exe_path = "dist\\AeroFPS_PRO.exe"
    else:
        exe_path = "dist\\AeroFPS_PRO\\AeroFPS_PRO.exe"
    
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"📦 EXE: {exe_path}")
        print(f"💾 Boyut: {exe_size:.1f} MB")
        
        print("\n" + "="*70)
        print("📋 DAĞITIM BİLGİLERİ:")
        print("="*70)
        print("\n1. Python kullanıcıları için:")
        print("   • AeroFPS.py + features/ + protection.py gönder")
        print("   • requirements.txt ile bağımlılıkları yükletsin")
        print(f"\n2. Normal kullanıcılar için:")
        print(f"   • {exe_path} dosyasını gönder")
        print("   • Yönetici olarak çalıştırmaları gerektiğini belirt")
        
        print("\n💡 İpuçları:")
        print("   • README.md dosyasını eklemeyi unutma")
        print("   • VirusTotal gibi sitelerde tara")
        print("   • Dijital imza ekleyebilirsin (opsiyonel)")
        
        print("\n" + "="*70)
    else:
        print(f"\n⚠️  Uyarı: EXE dosyası beklenen yerde bulunamadı.")
        print(f"   Beklenen: {exe_path}")
        print("   dist/ klasörünü kontrol edin.")
else:
    print("\n" + "="*70)
    print("❌ BUILD BAŞARISIZ!")
    print("="*70)
    print("\nHata detayları için yukarıdaki çıktıyı kontrol edin.")
    print("\nSık karşılaşılan sorunlar:")
    print("  • Eksik modüller: pip install -r requirements.txt")
    print("  • Yol sorunları: Dosya yollarını kontrol et")
    print("  • Antivirus: Geçici olarak kapat")

print("\n" + "="*70)
print("Build scripti tamamlandı!")
print("="*70 + "\n")

input("Çıkmak için ENTER'a basın...")
