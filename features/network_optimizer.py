"""
AeroFPS PRO - Network Ping Optimizer
Gerçek zamanlı ping izleme, DNS optimizasyonu ve TCP/UDP tweaks
"""

import subprocess
import re
import time
from colorama import Fore, Style
from .logger import log_info, log_success, log_error

# Import constants
try:
    from .constants import GAME_SERVERS, TIMEOUT_MEDIUM, TIMEOUT_SHORT, PING_COUNT_DEFAULT
except ImportError:
    # Fallback values
    GAME_SERVERS = {
        'Valorant EU': 'riot-geo.ff.avast.com',
        'CS2 EU': 'valve.vo.llnwd.net',
        'Fortnite EU': 'qosping-aws-eu-west-1.ol.epicgames.com',
        'League EU': 'prod.euw1.lol.riotgames.com',
        'Cloudflare': '1.1.1.1',
        'Google DNS': '8.8.8.8',
    }
    TIMEOUT_MEDIUM = 10
    TIMEOUT_SHORT = 5
    PING_COUNT_DEFAULT = 4

def advanced_network_diagnostics():
    """Gelişmiş ağ diagnostikleri"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║      🔍 ADVANCED NETWORK DIAGNOSTICS         ║")
    print("  ╚════════════════════════════════════════════════╝\n")

    diagnostics = {
        'connectivity': check_internet_connectivity(),
        'dns_health': check_dns_health(),
        'latency_analysis': analyze_network_latency(),
        'packet_loss': measure_packet_loss(),
        'bandwidth_test': estimate_bandwidth(),
        'firewall_status': check_firewall_status(),
        'network_config': analyze_network_config()
    }

    # Sonuçları göster
    display_diagnostics_results(diagnostics)

    # Öneriler
    recommendations = generate_network_recommendations(diagnostics)
    if recommendations:
        print(Fore.YELLOW + "\n💡 AĞ OPTİMİZASYON ÖNERİLERİ:")
        print(Fore.WHITE + "  " + "─" * 60)
        for rec in recommendations:
            print(f"  {rec}")

def check_internet_connectivity():
    """İnternet bağlantısını kontrol et"""
    print(Fore.YELLOW + "🌐 İnternet bağlantısı kontrol ediliyor...")

    test_urls = [
        ('Google', '8.8.8.8'),
        ('Cloudflare', '1.1.1.1'),
        ('OpenDNS', '208.67.222.222')
    ]

    results = {}
    for name, ip in test_urls:
        try:
            result = ping_server(ip, 2)  # 2 ping
            if result:
                status = "✅" if result.get('avg', 999) < 100 else "⚠️"
                results[name] = {
                    'status': 'online',
                    'latency': result.get('avg', 0),
                    'icon': status
                }
            else:
                results[name] = {'status': 'offline', 'latency': 0, 'icon': '❌'}
        except:
            results[name] = {'status': 'error', 'latency': 0, 'icon': '❌'}

    return results

def check_dns_health():
    """DNS sağlığını kontrol et"""
    print(Fore.YELLOW + "🔍 DNS sağlığı kontrol ediliyor...")

    dns_servers = [
        ('Google DNS', '8.8.8.8'),
        ('Cloudflare DNS', '1.1.1.1'),
        ('OpenDNS', '208.67.222.222')
    ]

    results = {}
    test_domain = 'google.com'

    for name, dns_ip in dns_servers:
        try:
            # DNS resolution testi
            import socket
            resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            resolver.settimeout(2)

            # Basit DNS sorgu simülasyonu
            start_time = time.time()
            try:
                ip = socket.gethostbyname(test_domain)
                resolve_time = (time.time() - start_time) * 1000
                results[name] = {
                    'status': 'healthy',
                    'resolve_time': resolve_time,
                    'resolved_ip': ip,
                    'icon': '✅' if resolve_time < 50 else '⚠️'
                }
            except:
                results[name] = {'status': 'failed', 'resolve_time': 0, 'icon': '❌'}

        except:
            results[name] = {'status': 'error', 'resolve_time': 0, 'icon': '❌'}

    return results

def analyze_network_latency():
    """Ağ gecikmesini analiz et"""
    print(Fore.YELLOW + "📊 Ağ gecikme analizi yapılıyor...")

    regions = {
        'Yerel': ['192.168.1.1'],  # Router
        'Türkiye': ['8.8.8.8', '1.1.1.1'],
        'Avrupa': ['194.0.0.1', '8.8.4.4'],  # BTK DNS, Google EU
        'Dünya': ['208.67.222.222', '4.2.2.1']  # OpenDNS, Level3
    }

    results = {}
    for region, servers in regions.items():
        latencies = []
        for server in servers:
            result = ping_server(server, 3)
            if result and result.get('avg'):
                latencies.append(result['avg'])

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            results[region] = {
                'avg_latency': avg_latency,
                'min_latency': min(latencies),
                'max_latency': max(latencies),
                'quality': 'excellent' if avg_latency < 20 else 'good' if avg_latency < 50 else 'poor'
            }
        else:
            results[region] = {'quality': 'no_connection'}

    return results

def measure_packet_loss():
    """Paket kaybını ölç"""
    print(Fore.YELLOW + "📦 Paket kaybı ölçülüyor...")

    test_servers = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
    results = {}

    for server in test_servers:
        result = ping_server(server, 10)  # 10 ping
        if result:
            loss_percent = result.get('loss', 0)
            results[server] = {
                'packet_loss': loss_percent,
                'quality': 'excellent' if loss_percent == 0 else 'good' if loss_percent < 2 else 'poor'
            }
        else:
            results[server] = {'packet_loss': 100, 'quality': 'no_connection'}

    return results

def estimate_bandwidth():
    """Bant genişliğini tahmin et (basit test)"""
    print(Fore.YELLOW + "📈 Bant genişliği tahmin ediliyor...")

    # Basit download testi
    try:
        import urllib.request
        import io

        test_url = "http://speedtest.tele2.net/1MB.zip"  # 1MB test dosyası
        start_time = time.time()

        with urllib.request.urlopen(test_url, timeout=10) as response:
            data = response.read()
            download_time = time.time() - start_time
            size_mb = len(data) / (1024 * 1024)

            bandwidth_mbps = (size_mb * 8) / download_time  # Mbps

            return {
                'download_speed': bandwidth_mbps,
                'test_size': size_mb,
                'test_time': download_time,
                'quality': 'excellent' if bandwidth_mbps > 50 else 'good' if bandwidth_mbps > 10 else 'poor'
            }
    except:
        return {'quality': 'test_failed'}

def check_firewall_status():
    """Firewall durumunu kontrol et"""
    print(Fore.YELLOW + "🔥 Firewall durumu kontrol ediliyor...")

    try:
        # Windows Firewall kontrolü
        output = subprocess.check_output(
            'netsh advfirewall show currentprofile',
            shell=True,
            encoding='utf-8',
            errors='ignore',
            timeout=TIMEOUT_SHORT
        )

        if 'ON' in output.upper():
            return {'status': 'active', 'icon': '🛡️'}
        else:
            return {'status': 'inactive', 'icon': '⚠️'}
    except:
        return {'status': 'unknown', 'icon': '❓'}

def analyze_network_config():
    """Ağ yapılandırmasını analiz et"""
    print(Fore.YELLOW + "⚙️  Ağ yapılandırması analiz ediliyor...")

    try:
        # IP config al
        output = subprocess.check_output(
            'ipconfig',
            shell=True,
            encoding='cp1254',  # Turkish Windows encoding
            errors='ignore',
            timeout=TIMEOUT_SHORT
        )

        config = {
            'ip_address': 'Unknown',
            'subnet_mask': 'Unknown',
            'gateway': 'Unknown',
            'dns_servers': []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if 'IPv4 Address' in line or 'IP Address' in line:
                # IP adresini çıkar
                parts = line.split(':')
                if len(parts) > 1:
                    config['ip_address'] = parts[1].strip()
            elif 'Subnet Mask' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    config['subnet_mask'] = parts[1].strip()
            elif 'Default Gateway' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    config['gateway'] = parts[1].strip()
            elif 'DNS Servers' in line:
                # DNS sunucularını topla
                dns_lines = []
                i = lines.index(line) + 1
                while i < len(lines) and lines[i].strip():
                    dns_lines.append(lines[i].strip())
                    i += 1
                config['dns_servers'] = dns_lines

        return config

    except:
        return {'error': 'config_unavailable'}

def display_diagnostics_results(diagnostics):
    """Diagnostik sonuçlarını göster"""
    print(Fore.WHITE + "\n📋 AĞ DİAGNOSTİK RAPORU:")
    print(Fore.WHITE + "═" * 78)

    # Connectivity
    print(Fore.CYAN + "🌐 İNTERNET BAĞLANTISI:")
    for name, result in diagnostics['connectivity'].items():
        icon = result['icon']
        status = f"{result['latency']:.0f}ms" if result['status'] == 'online' else result['status']
        print(f"  {icon} {name}: {status}")

    # DNS Health
    print(Fore.CYAN + "\n🔍 DNS SAĞLIĞI:")
    for name, result in diagnostics['dns_health'].items():
        icon = result['icon']
        if result['status'] == 'healthy':
            status = f"{result['resolve_time']:.0f}ms"
        else:
            status = result['status']
        print(f"  {icon} {name}: {status}")

    # Latency Analysis
    print(Fore.CYAN + "\n📊 GECİKME ANALİZİ:")
    for region, result in diagnostics['latency_analysis'].items():
        if result.get('quality') != 'no_connection':
            quality_icon = {'excellent': '🟢', 'good': '🟡', 'poor': '🔴'}[result['quality']]
            avg_lat = result['avg_latency']
            print(f"  {quality_icon} {region}: {avg_lat:.0f}ms (min: {result['min_latency']:.0f}ms, max: {result['max_latency']:.0f}ms)")
        else:
            print(f"  ❌ {region}: Bağlantı yok")

    # Packet Loss
    print(Fore.CYAN + "\n📦 PAKET KAYBI:")
    for server, result in diagnostics['packet_loss'].items():
        quality_icon = {'excellent': '🟢', 'good': '🟡', 'poor': '🔴', 'no_connection': '❌'}[result['quality']]
        loss = result['packet_loss']
        print(f"  {quality_icon} {server}: %{loss:.1f} paket kaybı")

    # Bandwidth
    print(Fore.CYAN + "\n📈 BANT GENİŞLİĞİ:")
    if 'download_speed' in diagnostics['bandwidth_test']:
        speed = diagnostics['bandwidth_test']['download_speed']
        quality_icon = {'excellent': '🟢', 'good': '🟡', 'poor': '🔴'}[diagnostics['bandwidth_test']['quality']]
        print(f"  {quality_icon} Download: {speed:.1f} Mbps")
    else:
        print("  ❌ Bant genişliği testi başarısız")

    # Firewall
    print(Fore.CYAN + "\n🛡️  FIREWALL:")
    firewall = diagnostics['firewall_status']
    print(f"  {firewall['icon']} Durum: {firewall['status']}")

    # Network Config
    print(Fore.CYAN + "\n⚙️  AĞ YAPILANDIRMASI:")
    config = diagnostics['network_config']
    if 'error' not in config:
        print(f"  📍 IP Adresi: {config['ip_address']}")
        print(f"  🛣️  Gateway: {config['gateway']}")
        print(f"  🔍 DNS Sunucuları: {', '.join(config['dns_servers'][:2])}")  # İlk 2 DNS
    else:
        print("  ❌ Ağ yapılandırması alınamadı")

def generate_network_recommendations(diagnostics):
    """Ağ optimizasyon önerileri oluştur"""
    recommendations = []

    # Connectivity önerileri
    online_count = sum(1 for r in diagnostics['connectivity'].values() if r['status'] == 'online')
    if online_count < 2:
        recommendations.append("❌ İnternet bağlantınızı kontrol edin - çok az sunucuya erişim var")

    # DNS önerileri
    healthy_dns = sum(1 for r in diagnostics['dns_health'].values() if r['status'] == 'healthy')
    if healthy_dns < 2:
        recommendations.append("🔍 DNS ayarlarınızı kontrol edin - yavaş veya hatalı DNS")

    # Latency önerileri
    local_latency = diagnostics['latency_analysis'].get('Yerel', {}).get('avg_latency', 999)
    if local_latency > 50:
        recommendations.append("🏠 Yerel ağınızı optimize edin - router/WiFi sorunları olabilir")

    # Packet loss önerileri
    high_loss = any(r['packet_loss'] > 5 for r in diagnostics['packet_loss'].values())
    if high_loss:
        recommendations.append("📦 Paket kaybı yüksek - ağ donanımınızı kontrol edin")

    # Bandwidth önerileri
    if 'download_speed' in diagnostics['bandwidth_test']:
        speed = diagnostics['bandwidth_test']['download_speed']
        if speed < 10:
            recommendations.append("📈 Bant genişliğiniz düşük - internet paketini yükseltmeyi değerlendirin")

    # Firewall önerileri
    if diagnostics['firewall_status']['status'] == 'inactive':
        recommendations.append("🛡️ Firewall aktif değil - güvenliğiniz risk altında")

    return recommendations
    """Sunucuya ping at ve sonuçları döndür"""
    try:
        # Güvenlik kontrolü
        if not host or not isinstance(host, str):
            return None

        # Host name validation (basit)
        import re
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$|^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', host):
            return None

        cmd = f'ping -n {count} {host}'
        output = subprocess.check_output(
            cmd,
            shell=True,  # Ping için shell gerekli
            encoding='utf-8',
            errors='ignore',
            timeout=TIMEOUT_MEDIUM
        )
        
        # Ping değerlerini parse et
        pings = re.findall(r'time[=<](\d+)ms', output)
        pings = [int(p) for p in pings]
        
        if pings:
            import statistics  # Lazy import
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
                # Güvenli subprocess çağrısı - adapter name'ini validate et
                if adapter and isinstance(adapter, str) and len(adapter.strip()) > 0:
                    safe_adapter = adapter.strip().replace('"', '')  # Quote injection önleme
                    subprocess.run(
                        f'netsh interface ip set dns "{safe_adapter}" static {primary} primary',
                        shell=True,  # netsh için gerekli
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=TIMEOUT_SHORT
                    )
                    subprocess.run(
                        f'netsh interface ip add dns "{safe_adapter}" {secondary} index=2',
                        shell=True,  # netsh için gerekli
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=TIMEOUT_SHORT
                    )
            
            subprocess.run('ipconfig /flushdns', shell=True, stdout=subprocess.DEVNULL, timeout=TIMEOUT_SHORT)
            
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
            try:
                subprocess.run("netsh winsock reset", shell=True, stdout=subprocess.DEVNULL, timeout=TIMEOUT_MEDIUM)
                subprocess.run("netsh int ip reset", shell=True, stdout=subprocess.DEVNULL, timeout=TIMEOUT_MEDIUM)
                subprocess.run("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL, timeout=TIMEOUT_MEDIUM)
                print(Fore.GREEN + "  ✅ Network sıfırlandı! (Yeniden başlatma önerilir)")
                log_success("Network ayarları sıfırlandı")
            except subprocess.TimeoutExpired:
                print(Fore.RED + "  ❌ Network reset zaman aşımına uğradı")
                log_error("Network reset timeout")
        elif choice == '5':
            break
        
        input(Fore.CYAN + "\n  Devam etmek için ENTER'a basın...")

if __name__ == "__main__":
    network_optimizer_menu()
