"""
╔═══════════════════════════════════════════════════════════════════════╗
║                        AeroFPS PRO v1.0                                ║
║              Ultimate Windows Gaming Optimization Suite                ║
║                                                                        ║
║  Copyright © 2026 AeroDLL | github.com/AeroDLL/AeroFPS                ║
║  Tüm Hakları Saklıdır / All Rights Reserved                           ║
╚═══════════════════════════════════════════════════════════════════════╝

UYARI / WARNING:
Bu yazılım telif hakkı ile korunmaktadır. Yetkisiz değiştirme,
dağıtma veya satışı yasaktır.

This software is protected by copyright. Unauthorized modification,
distribution or sale is prohibited.
"""

import os
import sys
import ctypes
import subprocess
import time
import webbrowser
import platform
from colorama import init, Fore, Style

# İlk önce protection modülünü import et
try:
    from protection import first_run_setup, show_watermark
    from features.logger import log_info, log_success, log_error, log_warning, view_logs, clear_logs
    from features.win_compat import create_restore_point, get_cpu_info, get_gpu_info, get_monitor_refresh_rate, get_startup_programs, WMIC_AVAILABLE
except ImportError as e:
    print(f"⚠️  Modül import hatası: {e}")
    print("Lütfen tüm dosyaların doğru konumda olduğundan emin olun.")
    input("Çıkmak için ENTER'a basın...")
    sys.exit(1)

# Renkleri Başlat
init(autoreset=True)

# --- GLOBAL DİL DEĞİŞKENİ ---
LANGUAGE = "EN"  # Varsayılan / Default
VERSION = "PRO v1.1"

def T(tr_text, en_text):
    """Dil seçimine göre metin döndürür / Returns text based on language"""
    if LANGUAGE == "TR":
        return tr_text
    else:
        return en_text

# --- YÖNETİCİ KONTROLÜ / ADMIN CHECK ---
def is_admin():
    """Yönetici haklarını kontrol et"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """Yönetici hakları talep et (sonsuz döngü önleme ile)"""
    # Argüman kontrolü - tekrar başlatmayı önle
    if len(sys.argv) > 1 and sys.argv[1] == '--admin-requested':
        print(Fore.RED + "\n❌ Yönetici hakları alınamadı!")
        print(Fore.YELLOW + "\nBu programı kullanabilmek için:")
        print(Fore.WHITE + "  1. Programı sağ tıklayın")
        print(Fore.WHITE + "  2. 'Yönetici olarak çalıştır' seçeneğini seçin\n")
        input("Çıkmak için ENTER'a basın...")
        sys.exit(1)
    
    # Admin haklarıyla yeniden başlat
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join([*sys.argv, '--admin-requested']), 
            None, 
            1
        )
        sys.exit()
    except Exception as e:
        print(Fore.RED + f"\n❌ Hata: {e}")
        input("Çıkmak için ENTER'a basın...")
        sys.exit(1)

# Admin kontrolü
if not is_admin():
    request_admin()

# İlk çalıştırma kurulumu
try:
    if not first_run_setup():
        sys.exit(0)
except Exception as e:
    log_error(f"İlk kurulum hatası: {e}")

# --- YARDIMCI FONKSİYONLAR / HELPER FUNCTIONS ---
def clear():
    """Ekranı temizle"""
    os.system('cls' if os.name == 'nt' else 'clear')

def title(text):
    """Konsol başlığını değiştir"""
    try:
        os.system(f'title AeroFPS PRO | {text}')
    except:
        pass

def run(cmd, timeout=30):
    """
    Komutu çalıştır (hata yönetimi ile)
    Returns: True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log_warning(f"Komut zaman aşımı: {cmd}")
        return False
    except Exception as e:
        log_error(f"Komut hatası: {cmd} - {e}")
        return False

def print_success(msg):
    """Başarı mesajı"""
    print(Fore.GREEN + Style.BRIGHT + f" [OK] {msg}")
    log_success(msg)

def print_info(msg):
    """Bilgi mesajı"""
    print(Fore.YELLOW + f" [*] {msg}")
    log_info(msg)

def print_error(msg):
    """Hata mesajı"""
    print(Fore.RED + f" [!] {msg}")
    log_error(msg)

def pause():
    """Duraklatma"""
    print()
    input(Fore.CYAN + T(" Devam etmek icin Enter'a basin...", " Press Enter to continue..."))

# --- DİL SEÇİM EKRANI / LANGUAGE SELECTOR ---
def select_language():
    """Dil seçim ekranı"""
    global LANGUAGE
    clear()
    print(Fore.CYAN + Style.BRIGHT + """
    ╔════════════════════════════════════════════════╗
    ║          LANGUAGE SELECTION / DİL SEÇİMİ       ║
    ╚════════════════════════════════════════════════╝
    """)
    print(Fore.WHITE + "  [1] 🇹🇷 Türkçe (Turkish)")
    print(Fore.WHITE + "  [2] 🇬🇧 English (Global)")
    print()
    
    choice = input(Fore.GREEN + "  Select / Secim (1-2): ")
    if choice == '1':
        LANGUAGE = "TR"
        log_info("Dil: Türkçe seçildi")
    else:
        LANGUAGE = "EN"
        log_info("Language: English selected")

# --- MENÜ TASARIMI / BANNER ---
def banner():
    """Modern banner göster"""
    clear()
    print(Fore.CYAN + Style.BRIGHT + r"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║     █████╗ ███████╗██████╗  ██████╗ ███████╗██████╗ ███████╗          ║
║    ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔══██╗██╔════╝          ║
║    ███████║█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝███████╗          ║
║    ██╔══██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██╔═══╝ ╚════██║          ║
║    ██║  ██║███████╗██║  ██║╚██████╔╝██║     ██║     ███████║          ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚══════╝          ║
║                                                                        ║
╟────────────────────────────────────────────────────────────────────────╢
║                    🎮 ULTIMATE GAMING SUITE 🎮                        ║
║                          PRO EDITION v1.0                              ║
╟────────────────────────────────────────────────────────────────────────╢
║  ⚡ FPS Boost  │  🧹 System Clean  │  🛡️  Privacy  │  🔥 Performance  ║
╚════════════════════════════════════════════════════════════════════════╝
""")
    print(Fore.YELLOW + "    💻 Designed by AeroDLL | github.com/AeroDLL/AeroFPS")
    print(Fore.WHITE + f"    📊 Sistem: Windows {platform.release()} | Python {platform.python_version()}")
    print(Fore.CYAN + "    ⚖️  Copyright © 2026 - Tüm Hakları Saklıdır\n")

# --- ÖZELLİKLER / FEATURES ---

def restore_point():
    """Güvenlik yedeği oluştur"""
    title(T("Guvenlik Yedegi", "Security Backup"))
    print_info(T("Sistem Geri Yukleme Noktasi Olusturuluyor...", "Creating System Restore Point..."))
    
    if create_restore_point("AeroFPS_PRO_Backup"):
        print_success(T("Yedekleme Tamamlandi!", "Backup Created Successfully!"))
    else:
        print_error(T("Yedekleme basarisiz! (Windows 11'de bu normal olabilir)", "Backup failed! (This may be normal on Windows 11)"))
    
    pause()

def clean_disk():
    """Disk temizliği"""
    title(T("Derin Temizlik", "Deep Clean"))
    print_info(T("Gecici Dosyalar Siliniyor...", "Cleaning Temp Files..."))
    
    paths = [
        r'C:\Windows\Temp\*.*',
        r'C:\Windows\Prefetch\*.*',
        os.path.expandvars(r'%temp%\*.*')
    ]
    
    cleaned = 0
    for p in paths:
        if run(f'del /s /f /q "{p}"'):
            cleaned += 1
    
    run('ipconfig /flushdns')
    
    print_success(T(f"Sistem Temizlendi! ({cleaned}/3)", f"System Cleaned! ({cleaned}/3)"))
    pause()

def fps_boost():
    """FPS artırma optimizasyonları"""
    title(T("Oyun Modu", "Game Mode"))
    print_info(T("Ultimate Performance Modu Aciliyor...", "Activating Ultimate Performance Mode..."))
    
    # Ultimate Performance
    run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
    if run('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61'):
        print_success("Ultimate Performance Mode OK")
    
    print_info(T("Gereksiz Servisler Kapatiliyor...", "Disabling Unnecessary Services..."))
    services = ["DiagTrack", "SysMain", "MapsBroker", "WSearch", "TabletInputService"]
    disabled = 0
    
    for s in services:
        run(f'sc stop "{s}"')
        if run(f'sc config "{s}" start= disabled'):
            disabled += 1
            print(Fore.GREEN + f"  ✓ {s} disabled")
    
    print_success(T(f"FPS Boost Tamamlandi! ({disabled} servis)", f"FPS Boost Completed! ({disabled} services)"))
    pause()

def advanced_opt():
    """Gelişmiş optimizasyonlar"""
    title(T("Gelismis Ayarlar", "Advanced Tweaks"))
    print_info(T("SSD ve Ag Ayarlari Yapiliyor...", "Optimizing SSD and Network..."))
    
    # SSD TRIM
    if run('fsutil behavior set disabledeletenotify 0'):
        print_success("SSD TRIM enabled")
    
    # Network Throttling
    if run(r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f'):
        print_success("Network Throttling disabled")
    
    print_success(T("Optimize Edildi!", "Optimized!"))
    pause()

def dns_optimizer():
    """DNS optimizasyonu"""
    title("DNS Optimizer")
    
    # Aktif network adaptörlerini al
    try:
        output = subprocess.check_output('netsh interface show interface', shell=True).decode()
        adapters = []
        for line in output.split('\n'):
            if 'Connected' in line or 'Bağlı' in line:
                parts = line.split()
                if len(parts) >= 4:
                    adapter_name = ' '.join(parts[3:])
                    adapters.append(adapter_name)
    except:
        adapters = ["Ethernet", "Wi-Fi"]
    
    print(Fore.YELLOW + "\n [1] ☁️  Cloudflare (1.1.1.1 - Hızlı)")
    print(Fore.YELLOW + " [2] 🌐 Google (8.8.8.8 - Güvenilir)")
    print(Fore.YELLOW + " [3] 🔄 " + T("Otomatik (ISP)", "Automatic (ISP)"))
    print(Fore.YELLOW + " [4] 📡 " + T("Ping Testi", "Ping Test"))
    
    c = input(Fore.WHITE + "\n " + T("Secim: ", "Choice: "))
    
    if c in ['1', '2', '3']:
        dns = "1.1.1.1" if c == '1' else "8.8.8.8" if c == '2' else "dhcp"
        
        for adapter in adapters:
            if dns == "dhcp":
                run(f'netsh interface ip set dns "{adapter}" dhcp')
            else:
                run(f'netsh interface ip set dns "{adapter}" static {dns} primary')
        
        print_success(f"DNS {dns} OK!")
    elif c == '4':
        print("\n🌐 Cloudflare Ping:")
        os.system("ping -n 4 1.1.1.1")
        print("\n🌐 Google Ping:")
        os.system("ping -n 4 8.8.8.8")
    
    pause()

def gpu_turbo():
    """GPU optimizasyonu"""
    title("GPU Turbo")
    print_info(T("GPU Donanim Hizlandirma Aciliyor...", "Enabling Hardware GPU Scheduling..."))
    
    if run(r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f'):
        print_success("GPU Hardware Scheduling enabled")
    
    if run(r'reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f'):
        print_success("Game Mode enabled")
    
    print_success("GPU Optimized!")
    pause()

def system_analyze():
    """Sistem analizi"""
    title(T("Sistem Analizi", "System Analysis"))
    
    print(Fore.CYAN + "\n📊 SİSTEM BİLGİLERİ:\n")
    os.system('systeminfo | findstr /C:"OS Name" /C:"Total Physical Memory" /C:"System Type"')
    
    print(Fore.CYAN + "\n💻 CPU KULLANIMI:")
    cpu_info = get_cpu_info()
    if cpu_info:
        print(cpu_info)
    else:
        print(Fore.YELLOW + "  ⚠️  CPU bilgisi alınamadı")
    
    print(Fore.CYAN + "\n🖥️  GPU BİLGİSİ:")
    gpu_info = get_gpu_info()
    if gpu_info:
        print(gpu_info)
    else:
        print(Fore.YELLOW + "  ⚠️  GPU bilgisi alınamadı")
    
    pause()

def startup_manager():
    """Başlangıç yöneticisi"""
    title("Startup Manager")
    print(Fore.CYAN + "\n🔥 BAŞLANGIÇ PROGRAMLARI:\n")
    startup_info = get_startup_programs()
    if startup_info:
        print(startup_info)
    else:
        print(Fore.YELLOW + "  ⚠️  Başlangıç programları listesi alınamadı")
    pause()

def defender_toggle():
    """Defender kontrol"""
    title("Defender Control")
    print(Fore.YELLOW + T(" [1] Kapat (Oyun İçin)", " [1] Disable (For Gaming)"))
    print(Fore.YELLOW + T(" [2] Ac (Normal", " [2] Enable (Normal)"))
    print(Fore.RED + "\n⚠️  UYARI: Oyun bitince tekrar açmanız önerilir!")
    
    c = input("\n : ")
    key = r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection"
    
    if c == '1':
        if run(f'reg add "{key}" /v "DisableRealtimeMonitoring" /t REG_DWORD /d 1 /f'):
            print_success("Defender disabled")
    elif c == '2':
        if run(f'reg delete "{key}" /v "DisableRealtimeMonitoring" /f'):
            print_success("Defender enabled")
    
    pause()

def input_lag_fix():
    """Input lag düzeltme"""
    title("Input Lag Fix")
    
    if run(r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d 50 /f'):
        print_success("Mouse queue optimized")
    
    if run(r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 38 /f'):
        print_success("Process priority optimized")
    
    print_success("Input Lag Fix Applied!")
    pause()

def game_guides():
    """Oyun rehberleri"""
    webbrowser.open("https://www.nvidia.com/en-us/geforce/news/performance-tuning-guide/")
    print_success("Link Opened.")
    pause()

def stress_test():
    """Stres testi"""
    title("Stress Test")
    print_info("WinSAT Benchmark Running...")
    os.system("winsat formal")
    pause()

def ram_cleaner():
    """RAM temizleyici"""
    title("RAM Cleaner")
    try:
        psapi = ctypes.WinDLL('psapi.dll')
        kernel = ctypes.WinDLL('kernel32.dll')
        psapi.EmptyWorkingSet(kernel.GetCurrentProcess())
        print_success(T("RAM Cache Temizlendi!", "RAM Cache Cleared!"))
    except Exception as e:
        print_error(f"RAM Cleaner Error: {e}")
    pause()

def repair_station():
    """Onarım istasyonu"""
    title("Repair Station")
    print_info("SFC / DISM Running...")
    print(Fore.YELLOW + "Bu işlem uzun sürebilir...\n")
    
    os.system("sfc /scannow")
    os.system("DISM /Online /Cleanup-Image /RestoreHealth")
    
    print_success("Repair Done.")
    pause()

def software_update():
    """Yazılım güncelleyici"""
    title("Software Updater")
    print_info("Winget Upgrade...")
    os.system("winget upgrade --all --include-unknown")
    pause()

def network_repair():
    """Ağ onarımı"""
    title("Network Repair")
    print_info("Resetting TCP/IP & Winsock...")
    
    run("netsh winsock reset")
    run("netsh int ip reset")
    run("ipconfig /flushdns")
    
    print_success(T("Ag Ayarlari Sifirlandi!", "Network Reset Done!"))
    pause()

def privacy_shield():
    """Gizlilik koruması"""
    title("Privacy Shield")
    print_info(T("Telemetri Engelleniyor...", "Blocking Telemetry..."))
    
    if run(r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'):
        print_success("Advertising disabled")
    
    if run(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f'):
        print_success("Telemetry disabled")
    
    print_success("Privacy Protected!")
    pause()

def monitor_hz():
    """Monitör hz kontrolü"""
    title("Monitor Hz")
    print(Fore.CYAN + "\n🖥️  MONITÖR BİLGİSİ:\n")
    monitor_info = get_monitor_refresh_rate()
    if monitor_info:
        print(monitor_info)
    else:
        print(Fore.YELLOW + "  ⚠️  Monitör bilgisi alınamadı")
    pause()

def bcd_tweaks():
    """BCD gecikme ayarları"""
    title("BCD Latency Tweaks")
    print_info(T("Gecikme Ayarlari Yapiliyor...", "Applying Latency Tweaks..."))
    
    if run("bcdedit /set useplatformclock No"):
        print_success("Platform clock disabled")
    
    if run("bcdedit /set disabledynamictick Yes"):
        print_success("Dynamic tick disabled")
    
    if run("bcdedit /timeout 10"):
        print_success("Boot timeout optimized")
    
    print_success(T("BCD Ayarlari Uygulandi! (Restart Gerekli)", "BCD Tweaks Applied! (Restart Required)"))
    pause()

def gaming_runtimes():
    """Oyun bileşenleri"""
    title("Gaming Runtimes Installer")
    print_info(T("Oyun Bilesenleri Kontrol Ediliyor...", "Checking Game Runtimes..."))
    print(Fore.YELLOW + "⏳ Bu işlem biraz sürebilir...\n")
    
    os.system("winget install --id Microsoft.VCRedist.2015+.x64")
    os.system("winget install --id Microsoft.DirectX")
    
    print_success(T("Kurulumlar Tamamlandi!", "Installation Completed!"))
    pause()

def revert():
    """Ayarları geri al"""
    title(T("Fabrika Ayarlari", "Factory Reset"))
    print_error(T("DIKKAT: Tum optimizasyonlar geri alinacak.", "WARNING: All tweaks will be reverted."))
    
    c = input(T("\n Onay (e/h): ", "\n Confirm (y/n): "))
    if c.lower() in ['e', 'y']:
        run('sc config "SysMain" start= auto')
        run('sc start "SysMain"')
        run('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e')
        run('netsh interface ip set dns "Ethernet" dhcp')
        run('netsh interface ip set dns "Wi-Fi" dhcp')
        run("bcdedit /deletevalue useplatformclock")
        run("bcdedit /deletevalue disabledynamictick")
        
        print_success(T("Sifirlandi.", "Reverted."))
    
    pause()

# --- YENİ PRO ÖZELLİKLERİ ---

def one_click_optimize():
    """Tek tuşla optimizasyon"""
    from features.auto_optimizer import one_click_optimize as optimize
    optimize()
    pause()

def process_manager():
    """Process yöneticisi"""
    from features.process_manager import process_manager_menu
    process_manager_menu()

def temp_monitor():
    """Sıcaklık izleme"""
    from features.temp_monitor import display_temperature
    display_temperature()
    pause()

def check_updates():
    """Güncelleme kontrolü"""
    from features.updater import check_for_updates
    check_for_updates()
    pause()

def show_logs():
    """Logları göster"""
    view_logs()
    
    print(Fore.YELLOW + "\n [1] Geri Dön")
    print(Fore.RED + " [2] Logları Temizle")
    
    c = input(Fore.WHITE + "\n Seçim: ")
    if c == '2':
        clear_logs()

def network_optimizer():
    """Network ping optimizer"""
    from features.network_optimizer import network_optimizer_menu
    network_optimizer_menu()

def smart_advisor():
    """Akıllı öneri sistemi"""
    from features.smart_advisor import analyze_and_suggest
    analyze_and_suggest()
    pause()

def game_config_optimizer():
    """Oyun içi ayar önerileri"""
    from features.game_config_optimizer import game_config_menu
    game_config_menu()

def scheduled_optimization():
    """Zamanlanmış optimizasyon"""
    from features.scheduler import scheduler_menu
    scheduler_menu()

# --- ANA DÖNGÜ / MAIN LOOP ---
def main():
    """Ana program"""
    # Başlangıçta watermark göster
    log_info(f"AeroFPS PRO {VERSION} başlatıldı")
    
    # Dil seçimi
    select_language()
    
    while True:
        banner()
        
        # Dinamik Menü
        m1 = T("🚀 ONE-CLICK OPTIMIZE (YENİ)", "🚀 ONE-CLICK OPTIMIZE (NEW)")
        m2 = T("⚡ FPS BOOST MODU", "⚡ FPS BOOST MODE")
        m3 = T("🧹 DERİN TEMİZLİK", "🧹 DEEP CLEANER")
        m4 = T("🎮 PROCESS MANAGER (YENİ)", "🎮 PROCESS MANAGER (NEW)")
        m5 = T("🌡️  ISI & KAYNAK İZLEME (YENİ)", "🌡️  TEMP & RESOURCE MONITOR (NEW)")
        m6 = T("💾 GÜVENLİK YEDEĞİ", "💾 CREATE RESTORE POINT")
        m7 = T("🔧 GELİŞMİŞ OPTİMİZASYON", "🔧 ADVANCED OPTIMIZATION")
        m8 = T("🌐 DNS OPTIMIZER", "🌐 DNS OPTIMIZER")
        m9 = T("🎯 GPU TURBO MODE", "🎯 GPU TURBO MODE")
        m10 = T("📊 SİSTEM ANALİZİ", "📊 SYSTEM ANALYSIS")
        m11 = T("🔥 STARTUP MANAGER", "🔥 STARTUP MANAGER")
        m12 = T("🛡️  DEFENDER KONTROL", "🛡️  DEFENDER CONTROL")
        m13 = T("💻 INPUT LAG FIX", "💻 INPUT LAG FIX")
        m14 = T("⚡ BCD GECIKME TWEAK", "⚡ BCD LATENCY TWEAK")
        m15 = T("🎮 OYUN BİLEŞENLERİ", "🎮 GAME RUNTIMES")
        m16 = T("🧪 STRES TESTİ", "🧪 STRESS TEST")
        m17 = T("🧠 RAM CLEANER", "🧠 RAM CLEANER")
        m18 = T("🚑 TAMİR İSTASYONU", "🚑 REPAIR STATION")
        m19 = T("🔄 PROGRAM GÜNCELLE", "🔄 UPDATE SOFTWARE")
        m20 = T("🌐 İNTERNET TAMİRİ", "🌐 NETWORK REPAIR")
        m21 = T("🕵️  GİZLİLİK KALKANI", "🕵️  PRIVACY SHIELD")
        m22 = T("🖥️  MONITOR HZ", "🖥️  MONITOR HZ CHECK")
        m23 = T("📋 LOG GÖRÜNTÜLE (YENİ)", "📋 VIEW LOGS (NEW)")
        m24 = T("🔄 GÜNCELLEME KONTROL (YENİ)", "🔄 CHECK UPDATES (NEW)")
        m25 = T("⚙️  SIFIRLA", "⚙️  REVERT")
        m26 = T("❌ ÇIKIŞ", "❌ EXIT")
        m27 = T("🌐 NETWORK PING OPTIMIZER (YENİ)", "🌐 NETWORK PING OPTIMIZER (NEW)")
        m28 = T("🤖 AKILLI ÖNERİ SİSTEMİ (YENİ)", "🤖 SMART ADVISOR (NEW)")
        m29 = T("🎨 OYUN AYAR ÖNERİLERİ (YENİ)", "🎨 GAME CONFIG OPTIMIZER (NEW)")
        m30 = T("⏰ ZAMANLANMIŞ OPTİMİZASYON (YENİ)", "⏰ SCHEDULED OPTIMIZATION (NEW)")

        print(Fore.WHITE + "  ╔════════════════════════════════════════════════════════════════════╗")
        print(Fore.WHITE + "  ║                      🎯 ANA MENÜ / MAIN MENU                        ║")
        print(Fore.WHITE + "  ╚════════════════════════════════════════════════════════════════════╝\n")
        
        print(Fore.CYAN + Style.BRIGHT + f"  {m1}")
        print(Fore.WHITE + "  ────────────────────────────────────────────────────────────────────")
        print(Fore.WHITE + f"  [1]  {m2:<35} [14] {m14}")
        print(Fore.WHITE + f"  [2]  {m3:<35} [15] {m15}")
        print(Fore.WHITE + f"  [3]  {m4:<35} [16] {m16}")
        print(Fore.WHITE + f"  [4]  {m5:<35} [17] {m17}")
        print(Fore.WHITE + f"  [5]  {m6:<35} [18] {m18}")
        print(Fore.WHITE + f"  [6]  {m7:<35} [19] {m19}")
        print(Fore.WHITE + f"  [7]  {m8:<35} [20] {m20}")
        print(Fore.WHITE + f"  [8]  {m9:<35} [21] {m21}")
        print(Fore.WHITE + f"  [9]  {m10:<35} [22] {m22}")
        print(Fore.WHITE + f"  [10] {m11:<35} [23] {m23}")
        print(Fore.WHITE + f"  [11] {m12:<35} [24] {m24}")
        print(Fore.WHITE + f"  [12] {m13:<35} [25] {m25}")
        print(Fore.WHITE + f"  [13] 🎯 " + T("OYUN REHBERLERİ", "GAME GUIDES") + f"{'':<19} [26] {m26}")
        print(Fore.WHITE + f"  [27] {m27}")
        print(Fore.WHITE + f"  [28] {m28}")
        print(Fore.WHITE + f"  [29] {m29}")
        print(Fore.WHITE + f"  [30] {m30}")
        
        print(Fore.CYAN + "\n  ═══════════════════════════════════════════════════════════════════")
        
        secim = input(Fore.GREEN + f"  {T('Seçim', 'Choice')} (0-30): ")

        try:
            if secim == '0': one_click_optimize()
            elif secim == '1': fps_boost()
            elif secim == '2': clean_disk()
            elif secim == '3': process_manager()
            elif secim == '4': temp_monitor()
            elif secim == '5': restore_point()
            elif secim == '6': advanced_opt()
            elif secim == '7': dns_optimizer()
            elif secim == '8': gpu_turbo()
            elif secim == '9': system_analyze()
            elif secim == '10': startup_manager()
            elif secim == '11': defender_toggle()
            elif secim == '12': input_lag_fix()
            elif secim == '13': game_guides()
            elif secim == '14': bcd_tweaks()
            elif secim == '15': gaming_runtimes()
            elif secim == '16': stress_test()
            elif secim == '17': ram_cleaner()
            elif secim == '18': repair_station()
            elif secim == '19': software_update()
            elif secim == '20': network_repair()
            elif secim == '21': privacy_shield()
            elif secim == '22': monitor_hz()
            elif secim == '23': show_logs()
            elif secim == '24': check_updates()
            elif secim == '25': revert()
            elif secim == '26':
                print(Fore.CYAN + "\n👋 AeroFPS PRO'yu kullandığınız için teşekkürler!")
                log_info("Program kapatıldı")
                time.sleep(1)
                sys.exit()
            elif secim == '27': network_optimizer()
            elif secim == '28': smart_advisor()
            elif secim == '29': game_config_optimizer()
            elif secim == '30': scheduled_optimization()
            else:
                print_error(T("Geçersiz Seçim!", "Invalid Choice!"))
                time.sleep(1)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n⚠️  Program kullanıcı tarafından durduruldu.")
            log_warning("Program Ctrl+C ile durduruldu")
            sys.exit()
        except Exception as e:
            print_error(f"Hata: {e}")
            log_error(f"İşlem hatası: {e}")
            pause()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"\n❌ Kritik Hata: {e}")
        log_error(f"Kritik hata: {e}")
        input("\nÇıkmak için ENTER'a basın...")
