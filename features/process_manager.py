"""
AeroFPS PRO - Process Priority Manager
Oyun ve uygulama önceliklerini yönetir
"""

import subprocess
import psutil
from colorama import Fore

# Popüler oyunlar listesi
POPULAR_GAMES = [
    "csgo.exe", "cs2.exe", "valorant.exe", "valorant-win64-shipping.exe",
    "fortniteclient-win64-shipping.exe", "apexlegends.exe", "r5apex.exe",
    "league of legends.exe", "leagueclient.exe", "overwatch.exe",
    "cod.exe", "modernwarfare.exe", "warzone.exe", "gta5.exe",
    "pubg.exe", "tslgame.exe", "rainbow6.exe", "r6s.exe",
    "dota2.exe", "minecraft.exe", "javaw.exe", "rocketleague.exe"
]

# Kapatılacak gereksiz process'ler
BACKGROUND_APPS = [
    "discord.exe", "spotify.exe", "chrome.exe", "msedge.exe",
    "steam.exe", "epicgameslauncher.exe", "origin.exe",
    "skype.exe", "teams.exe", "onedrive.exe"
]

def get_running_games():
    """Çalışan oyunları tespit et"""
    running_games = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            proc_name = proc.info['name'].lower()
            if proc_name in [g.lower() for g in POPULAR_GAMES]:
                running_games.append({
                    'name': proc.info['name'],
                    'pid': proc.info['pid']
                })
    except Exception as e:
        print(f"❌ Hata: {e}")
    
    return running_games

def set_high_priority(pid):
    """Process'e yüksek öncelik ver"""
    try:
        # Windows: wmic ile priority değiştirme
        subprocess.run(
            f'wmic process where processid="{pid}" CALL setpriority "high priority"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except:
        # Alternatif: psutil ile
        try:
            p = psutil.Process(pid)
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            return True
        except:
            return False

def boost_game_priority():
    """Çalışan oyunları boost et"""
    print(Fore.YELLOW + "\n🎮 Çalışan Oyunlar Taranıyor...\n")
    
    games = get_running_games()
    
    if not games:
        print(Fore.RED + "❌ Aktif oyun bulunamadı.")
        print(Fore.CYAN + "\n💡 İpucu: Oyunu başlattıktan sonra bu özelliği kullanın.")
        return
    
    print(Fore.GREEN + f"✅ {len(games)} oyun tespit edildi:\n")
    
    for game in games:
        print(Fore.WHITE + f"   • {game['name']} (PID: {game['pid']})")
        if set_high_priority(game['pid']):
            print(Fore.GREEN + f"     ✓ Öncelik yükseltildi!")
        else:
            print(Fore.RED + f"     ✗ Öncelik değiştirilemedi")
    
    print(Fore.GREEN + f"\n✅ İşlem tamamlandı!")

def kill_background_apps():
    """Gereksiz arka plan uygulamalarını kapat"""
    print(Fore.YELLOW + "\n🔥 Arka Plan Uygulamaları Taranıyor...\n")
    
    killed = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if proc_name in [a.lower() for a in BACKGROUND_APPS]:
                print(Fore.YELLOW + f"   • {proc.info['name']} kapatılıyor...")
                proc.terminate()
                killed += 1
                print(Fore.GREEN + f"     ✓ Kapatıldı")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print(Fore.RED + f"     ✗ Hata: {e}")
    
    if killed > 0:
        print(Fore.GREEN + f"\n✅ {killed} uygulama kapatıldı!")
    else:
        print(Fore.CYAN + "\n💡 Kapatılacak gereksiz uygulama bulunamadı.")

def process_manager_menu():
    """Process Manager menüsü"""
    from colorama import init, Style
    init(autoreset=True)
    
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       PROCESS PRIORITY MANAGER                 ║")
    print("  ╚════════════════════════════════════════════════╝")
    print(Fore.WHITE + "\n  [1] 🎮 Oyun Önceliğini Yükselt")
    print(Fore.WHITE + "  [2] 🔥 Arka Plan Uygulamalarını Kapat")
    print(Fore.WHITE + "  [3] 📋 Çalışan Oyunları Listele")
    print(Fore.WHITE + "  [4] ⬅️  Geri Dön\n")
    
    choice = input(Fore.GREEN + "  Seçim (1-4): ")
    
    if choice == '1':
        boost_game_priority()
    elif choice == '2':
        print(Fore.RED + "\n⚠️  UYARI: Bazı uygulamalar kapatılacak!")
        confirm = input(Fore.YELLOW + "Devam etmek istiyor musunuz? (E/H): ").strip().upper()
        if confirm == 'E':
            kill_background_apps()
    elif choice == '3':
        games = get_running_games()
        if games:
            print(Fore.GREEN + f"\n✅ Çalışan Oyunlar ({len(games)}):\n")
            for g in games:
                print(Fore.WHITE + f"   • {g['name']} (PID: {g['pid']})")
        else:
            print(Fore.RED + "\n❌ Çalışan oyun bulunamadı.")
    elif choice == '4':
        return
    
    input(Fore.CYAN + "\n\nDevam etmek için ENTER'a basın...")

if __name__ == "__main__":
    # Test
    from colorama import init
    init(autoreset=True)
    process_manager_menu()
