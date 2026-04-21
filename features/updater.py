"""
AeroFPS PRO - Otomatik Güncelleme Kontrolü
Çoklu kaynak desteği ile versiyon kontrolü
"""

import urllib.request
import json
import ssl
import webbrowser
from colorama import Fore, Style

# Import constants
try:
    from .constants import TIMEOUT_MEDIUM, CURRENT_VERSION, UPDATE_SOURCES, MANUAL_CHECK_URL
except ImportError:
    TIMEOUT_MEDIUM = 10
    CURRENT_VERSION = "PRO v1.1"
    UPDATE_SOURCES = [
        {
            'name': 'GitHub API',
            'url': 'https://api.github.com/repos/AeroDLL/AeroFPS/releases/latest',
            'type': 'api'
        },
        {
            'name': 'GitHub Raw',
            'url': 'https://raw.githubusercontent.com/AeroDLL/AeroFPS/main/version.json',
            'type': 'raw'
        }
    ]
    MANUAL_CHECK_URL = "https://github.com/AeroDLL/AeroFPS/releases"

def try_github_api(url):
    """GitHub API'den veri al (güvenli SSL ile)"""
    try:
        # Önce normal SSL doğrulama ile dene
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_MEDIUM) as response:
                data = json.loads(response.read().decode())
        except ssl.SSLError as ssl_error:
            # SSL hatası durumunda sadece fallback kullan
            log_warning(f"SSL doğrulama hatası, güvenli mod kullanılıyor: {ssl_error}")
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=TIMEOUT_MEDIUM, context=context) as response:
                data = json.loads(response.read().decode())

        return {
            'version': data.get('tag_name', 'Unknown'),
            'url': data.get('html_url', MANUAL_CHECK_URL),
            'notes': data.get('body', 'Yayın notları yok.')
        }
    except urllib.error.URLError as url_error:
        log_error(f"URL erişim hatası: {url_error}")
        return None
    except json.JSONDecodeError as json_error:
        log_error(f"JSON parse hatası: {json_error}")
        return None
    except Exception as e:
        log_error(f"GitHub API hatası: {e}")
        return None

def try_raw_json(url):
    """Raw JSON dosyasından veri al (güvenli SSL ile)"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')

        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_MEDIUM) as response:
                data = json.loads(response.read().decode())
        except ssl.SSLError as ssl_error:
            # SSL hatası durumunda sadece fallback kullan
            log_warning(f"SSL doğrulama hatası, güvenli mod kullanılıyor: {ssl_error}")
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=TIMEOUT_MEDIUM, context=context) as response:
                data = json.loads(response.read().decode())

        return {
            'version': data.get('version', 'Unknown'),
            'url': data.get('download_url', MANUAL_CHECK_URL),
            'notes': data.get('release_notes', 'Yayın notları yok.')
        }
    except urllib.error.URLError as url_error:
        log_error(f"URL erişim hatası: {url_error}")
        return None
    except json.JSONDecodeError as json_error:
        log_error(f"JSON parse hatası: {json_error}")
        return None
    except Exception as e:
        log_error(f"Raw JSON hatası: {e}")
        return None

def check_for_updates():
    """Güncellemeleri kontrol et - çoklu kaynak desteği"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       GÜNCELLEME KONTROLÜ                      ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    print(Fore.YELLOW + f"  📦 Mevcut Versiyon: {CURRENT_VERSION}\n")
    print(Fore.WHITE + "  🔍 Güncelleme kontrol ediliyor...\n")
    
    update_info = None
    successful_source = None
    
    # Tüm kaynakları dene
    for source in UPDATE_SOURCES:
        print(Fore.CYAN + f"  ⏳ {source['name']} deneniyor...")
        
        if source['type'] == 'api':
            update_info = try_github_api(source['url'])
        elif source['type'] == 'raw':
            update_info = try_raw_json(source['url'])
        
        if update_info:
            successful_source = source['name']
            print(Fore.GREEN + f"  ✅ {source['name']} bağlantı başarılı!\n")
            break
        else:
            print(Fore.RED + f"  ✗ {source['name']} erişilemedi")
    
    if update_info:
        latest_version = update_info['version']
        release_url = update_info['url']
        release_notes = update_info['notes']
        
        print(Fore.GREEN + f"\n  ✅ Son Versiyon: {latest_version}")
        print(Fore.CYAN + f"  📡 Kaynak: {successful_source}\n")
        
        # Versiyon karşılaştırması
        if latest_version != CURRENT_VERSION:
            print(Fore.YELLOW + Style.BRIGHT + "  🎉 YENİ GÜNCELLEME MEVCUT!\n")
            print(Fore.WHITE + "  " + "─" * 46)
            print(Fore.CYAN + "  📝 Yayın Notları:")
            
            # Release notes'u düzgün formatla
            notes_lines = release_notes.split('\n')[:5]  # İlk 5 satır
            for line in notes_lines:
                if line.strip():
                    print(Fore.WHITE + f"  {line[:60]}")
            if len(release_notes) > 300:
                print(Fore.WHITE + "  ...")
            
            print(Fore.WHITE + "\n  " + "─" * 46)
            print(Fore.GREEN + f"\n  🔗 İndirme Linki:")
            print(Fore.WHITE + f"     {release_url}\n")
            
            choice = input(Fore.YELLOW + "  Tarayıcıda açmak ister misiniz? (E/H): ").strip().upper()
            if choice == 'E':
                webbrowser.open(release_url)
                print(Fore.GREEN + "\n  ✅ Tarayıcı açıldı!")
        else:
            print(Fore.GREEN + "  ✅ En son sürümü kullanıyorsunuz!\n")
    
    else:
        # Tüm kaynaklar başarısız
        print(Fore.RED + "\n  ❌ Güncelleme kontrolü yapılamadı.")
        print(Fore.YELLOW + "\n  💡 Olası Sebepler:")
        print(Fore.WHITE + "     • İnternet bağlantınız yok")
        print(Fore.WHITE + "     • GitHub erişimi engellenmiş (firewall/proxy)")
        print(Fore.WHITE + "     • Geçici bir sunucu sorunu")
        
        print(Fore.CYAN + "\n  📋 Manuel Kontrol:")
        print(Fore.WHITE + f"     {MANUAL_CHECK_URL}")
        
        choice = input(Fore.YELLOW + "\n  Manuel kontrol sayfasını açmak ister misiniz? (E/H): ").strip().upper()
        if choice == 'E':
            webbrowser.open(MANUAL_CHECK_URL)
            print(Fore.GREEN + "  ✅ Tarayıcı açıldı!")

if __name__ == "__main__":
    # Test
    from colorama import init
    init(autoreset=True)
    check_for_updates()
    input("\n\nDevam etmek için ENTER'a basın...")

if __name__ == "__main__":
    # Test
    from colorama import init
    init(autoreset=True)
    check_for_updates()
    input("\nDevam etmek için ENTER'a basın...")
