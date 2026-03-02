"""
AeroFPS PRO - Network Ping Optimizer
Gerçek zamanlı ping izleme, DNS optimizasyonu ve TCP/UDP tweaks
"""

import subprocess
import re
import time
import statistics
from colorama import Fore, Style
from .logger import log_info, log_success, log_error

# Popüler oyun sunucuları
GAME_SERVERS = {
    'Valorant EU': 'riot-geo.ff.avast.com',
    'CS2 EU': 'valve.vo.llnwd.net',
    'Fortnite EU': 'qosping-aws-eu-west-1.ol.epicgames.com',
    'League EU': 'prod.euw1.lol.riotgames.com',
    'Cloudflare': '1.1.1.1',
    'Google DNS': '8.8.8.8',
}

def ping_server(host, count=4):
    """Sunucuya ping at ve sonuçları döndür"""
    try:
        output = subprocess.check_output(
            f'ping -n {count} {host}',
            shell=True,
            encoding='utf-8',
            errors='ignore',
            timeout=10
        )
        
        # Ping değerlerini parse et
        pings = re.findall(r'time[=<](\d+)ms', output)
        pings = [int(p) for p in pings]
        
        if pings:
            return {
                'min': min(pings),
                'max': max(pings),
                'avg': statistics.mean(pings),
                'jitter': max(pings) - min(pings),
                'loss': count - len(pings)
            }
        return None
    except:
        return None

def get_ping_color(ping):
    """Ping değerine göre renk döndür"""
    if ping < 30:
        return Fore.GREEN
    elif ping < 60:
        return Fore.YELLOW
    elif ping < 100:
        return Fore.RED
    else:
        return Fore.RED + Style.BRIGHT

def display_ping_monitor():
    """Gerçek zamanlı ping monitörü"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       NETWORK PING MONITOR                     ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    print(Fore.YELLOW + "  🌐 Oyun sunucuları test ediliyor...\n")
    print(Fore.WHITE + "  " + "─" * 60)
    
    results = []
    
    for name, host in GAME_SERVERS.items():
        print(Fore.CYAN + f"  📡 {name:<20} ", end='', flush=True)
        
        result = ping_server(host, count=4)
        
        if result:
            color = get_ping_color(result['avg'])
            print(f"{color}{result['avg']:.0f}ms " + 
                  Fore.WHITE + f"(±{result['jitter']}ms)")
            
            if result['loss'] > 0:
                print(Fore.RED + f"     ⚠️  Packet Loss: {result['loss']}/4")
            
            results.append({
                'name': name,
                'host': host,
                'result': result
            })
        else:
            print(Fore.RED + "Timeout ❌")
    
    print(Fore.WHITE + "  " + "─" * 60)
    
    # En iyi sunucu önerisi
    if results:
        best = min(results, key=lambda x: x['result']['avg'])
        print(Fore.GREEN + f"\n  ✅ En İyi Bağlantı: {best['name']} ({best['result']['avg']:.0f}ms)")
        
        # Uyarılar
        high_ping = [r for r in results if r['result']['avg'] > 80]
        if high_ping:
            print(Fore.YELLOW + "\n  ⚠️  Yüksek Ping Tespit Edildi:")
            for r in high_ping:
                print(Fore.WHITE + f"     • {r['name']}: {r['result']['avg']:.0f}ms")
            print(Fore.CYAN + "\n  💡 Öneriler:")
            print(Fore.WHITE + "     • DNS ayarlarınızı optimize edin")
            print(Fore.WHITE + "     • Arka plan uygulamalarını kapatın")
            print(Fore.WHITE + "     • Kablolu bağlantı kullanın")

def apply_network_tweaks():
    """Gelişmiş network optimizasyonları"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       NETWORK OPTIMIZATION                     ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    print(Fore.YELLOW + "  ⚡ Network ayarları optimize ediliyor...\n")
    
    tweaks = [
        {
            'name': 'TCP Window Auto-Tuning',
            'cmd': 'netsh interface tcp set global autotuninglevel=normal'
        },
        {
            'name': 'Network Throttling Index',
            'cmd': 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f'
        },
        {
            'name': 'TCP Chimney Offload',
            'cmd': 'netsh interface tcp set global chimney=enabled'
        },
        {
            'name': 'RSS (Receive Side Scaling)',
            'cmd': 'netsh interface tcp set global rss=enabled'
        },
        {
            'name': 'Direct Cache Access',
            'cmd': 'netsh interface tcp set global dca=enabled'
        },
        {
            'name': 'ECN Capability',
            'cmd': 'netsh interface tcp set global ecncapability=enabled'
        },
        {
            'name': 'TCP Timestamps',
            'cmd': 'netsh interface tcp set global timestamps=enabled'
        },
        {
            'name': 'QoS Packet Scheduler',
            'cmd': 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f'
        }
    ]
    
    success_count = 0
    
    for tweak in tweaks:
        print(Fore.CYAN + f"  • {tweak['name']:<35} ", end='', flush=True)
        
        try:
            result = subprocess.run(
                tweak['cmd'],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10
            )
            
            if result.returncode == 0:
                print(Fore.GREEN + "✓")
                success_count += 1
                log_success(f"Network tweak uygulandı: {tweak['name']}")
            else:
                print(Fore.RED + "✗")
        except:
            print(Fore.RED + "✗")
    
    print(Fore.WHITE + "\n  " + "─" * 60)
    print(Fore.GREEN + f"  ✅ {success_count}/{len(tweaks)} optimizasyon uygulandı!")
    
    if success_count < len(tweaks):
        print(Fore.YELLOW + "\n  💡 Bazı ayarlar uygulanamadı (normal olabilir)")

def optimize_dns_for_gaming():
    """Oyun için en iyi DNS'i bul ve uygula"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       DNS OPTIMIZER FOR GAMING                 ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    dns_providers = {
        'Cloudflare': ('1.1.1.1', '1.0.0.1'),
        'Google': ('8.8.8.8', '8.8.4.4'),
        'Quad9': ('9.9.9.9', '149.112.112.112'),
        'OpenDNS': ('208.67.222.222', '208.67.220.220'),
    }
    
    print(Fore.YELLOW + "  🔍 En hızlı DNS bulunuyor...\n")
    
    results = {}
    
    for name, (primary, _) in dns_providers.items():
        print(Fore.CYAN + f"  Testing {name:<15} ", end='', flush=True)
        result = ping_server(primary, count=3)
        
        if result:
            results[name] = result['avg']
            color = get_ping_color(result['avg'])
            print(f"{color}{result['avg']:.0f}ms")
        else:
            print(Fore.RED + "Timeout")
    
    if results:
        best_dns = min(results, key=results.get)
        best_ping = results[best_dns]
        
        print(Fore.GREEN + f"\n  ✅ En Hızlı DNS: {best_dns} ({best_ping:.0f}ms)")
        
        choice = input(Fore.YELLOW + f"\n  {best_dns} DNS'ini uygulamak ister misiniz? (E/H): ").strip().upper()
        
        if choice == 'E':
            primary, secondary = dns_providers[best_dns]
            
            # Aktif adaptörleri al
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
            
            print(Fore.CYAN + "\n  Uygulanıyor...")
            
            for adapter in adapters:
                subprocess.run(
                    f'netsh interface ip set dns "{adapter}" static {primary} primary',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                subprocess.run(
                    f'netsh interface ip add dns "{adapter}" {secondary} index=2',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            subprocess.run('ipconfig /flushdns', shell=True, stdout=subprocess.DEVNULL)
            
            print(Fore.GREEN + f"  ✅ {best_dns} DNS uygulandı!")
            log_success(f"DNS değiştirildi: {best_dns}")

def network_optimizer_menu():
    """Network optimizer ana menü"""
    from colorama import init
    init(autoreset=True)
    
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n")
        print("  ╔════════════════════════════════════════════════╗")
        print("  ║       NETWORK PING OPTIMIZER                   ║")
        print("  ╚════════════════════════════════════════════════╝")
        print(Fore.WHITE + "\n  [1] 📊 Ping Monitör (Gerçek Zamanlı)")
        print(Fore.WHITE + "  [2] ⚡ Network Tweaks Uygula")
        print(Fore.WHITE + "  [3] 🌐 DNS Optimizer (Otomatik)")
        print(Fore.WHITE + "  [4] 🔄 Network Reset")
        print(Fore.WHITE + "  [5] ⬅️  Geri Dön\n")
        
        choice = input(Fore.GREEN + "  Seçim (1-5): ")
        
        if choice == '1':
            display_ping_monitor()
        elif choice == '2':
            apply_network_tweaks()
        elif choice == '3':
            optimize_dns_for_gaming()
        elif choice == '4':
            print(Fore.YELLOW + "\n  🔄 Network ayarları sıfırlanıyor...")
            subprocess.run("netsh winsock reset", shell=True, stdout=subprocess.DEVNULL)
            subprocess.run("netsh int ip reset", shell=True, stdout=subprocess.DEVNULL)
            subprocess.run("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL)
            print(Fore.GREEN + "  ✅ Network sıfırlandı! (Yeniden başlatma önerilir)")
            log_success("Network ayarları sıfırlandı")
        elif choice == '5':
            break
        
        input(Fore.CYAN + "\n  Devam etmek için ENTER'a basın...")

if __name__ == "__main__":
    network_optimizer_menu()
