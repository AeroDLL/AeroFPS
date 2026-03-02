"""
AeroFPS PRO - Kod Koruma Modülü
Copyright (c) 2026 AeroDLL
GitHub: github.com/AeroDLL/AeroFPS

Bu kod telif hakkı ile korunmaktadır.
Yetkisiz kopyalama, dağıtım veya değiştirme yasaktır.
"""

import hashlib
import os
import sys

# Anti-Piracy Watermark
WATERMARK = """
╔═══════════════════════════════════════════════════════════════════╗
║  AeroFPS PRO - Orijinal Yazılım                                   ║
║  Copyright © 2026 AeroDLL | Tüm hakları saklıdır                  ║
║                                                                    ║
║  ⚠️  UYARI: Bu yazılım telif hakkı ile korunmaktadır.             ║
║  Yetkisiz kopyalama, paylaşma veya satışı yasaktır.               ║
║                                                                    ║
║  GitHub: github.com/AeroDLL/AeroFPS                                ║
╚═══════════════════════════════════════════════════════════════════╝
"""

LICENSE_TEXT = """
AeroFPS PRO - KULLANIM LİSANSI

1. Bu yazılım ücretsiz olarak kullanılabilir.
2. Kaynak kodunu inceleyebilir ve öğrenme amaçlı kullanabilirsiniz.
3. Değiştirerek dağıtamazsınız (fork serbesttir, credit gereklidir).
4. Ticari kullanım için izin gereklidir.
5. Yazılım "OLDUĞU GİBİ" sunulmaktadır, hiçbir garanti verilmez.

© 2026 AeroDLL - github.com/AeroDLL
"""

def show_watermark():
    """Başlangıçta watermark göster"""
    print(WATERMARK)

def show_license():
    """Lisans metnini göster"""
    print(LICENSE_TEXT)

def check_integrity():
    """
    Dosya bütünlüğünü kontrol et (gelişmiş koruma için)
    Not: Bu basit bir implementasyon, daha güçlü koruma için
    PyArmor gibi araçlar kullanılabilir.
    """
    try:
        # Ana dosyanın hash'ini kontrol et (opsiyonel)
        main_file = os.path.join(os.path.dirname(__file__), "AeroFPS.py")
        if os.path.exists(main_file):
            with open(main_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            # Hash sabit tutulabilir ve kontrol edilebilir
            # Ancak her değişiklikte güncellemek gerekir
            return True
    except:
        pass
    return True

def first_run_setup():
    """İlk çalıştırma kurulumu"""
    first_run_file = os.path.join(os.path.dirname(__file__), ".aerofps_installed")
    
    if not os.path.exists(first_run_file):
        show_watermark()
        print("\n" + "="*70)
        print("  İLK ÇALIŞTIRMA KURULUMU")
        print("="*70)
        print("\nAeroFPS PRO'ya hoş geldiniz!")
        print("\nDevam etmeden önce lütfen lisans şartlarını okuyun:")
        input("\nDevam etmek için ENTER'a basın...")
        
        show_license()
        
        print("\n" + "="*70)
        choice = input("\nLisans şartlarını kabul ediyor musunuz? (E/H): ").strip().upper()
        
        if choice == 'E' or choice == 'Y':
            # İlk kurulum bayrağını oluştur
            try:
                with open(first_run_file, 'w') as f:
                    f.write(f"AeroFPS PRO kuruldu - {os.getlogin()}\n")
                print("\n✅ Kurulum tamamlandı! Program başlatılıyor...\n")
                return True
            except:
                print("\n✅ Devam ediliyor...\n")
                return True
        else:
            print("\n❌ Lisans kabul edilmedi. Program kapatılıyor...")
            sys.exit(0)
    
    return True

if __name__ == "__main__":
    # Test
    show_watermark()
    show_license()
