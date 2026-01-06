"""
AeroFPS PRO - Sıcaklık İzleme Modülü  
CPU ve sistem sıcaklıklarını gösterir
Windows 11 uyumlu (WMIC yerine win_compat kullanır)
"""

import platform
from colorama import Fore, Style

# Win_compat import
try:
    from .win_compat import get_cpu_temperature, get_cpu_load, get_memory_info, WMIC_AVAILABLE
except (ImportError, ValueError):
    try:
        from win_compat import get_cpu_temperature, get_cpu_load, get_memory_info, WMIC_AVAILABLE
    except ImportError:
        # Fallback - basit psutil kullan
        try:
            import psutil
            WMIC_AVAILABLE = False
            get_cpu_temperature = lambda: None
            get_cpu_load = lambda: int(psutil.cpu_percent(interval=1))
            def get_memory_info():
                mem = psutil.virtual_memory()
                return f"TotalVisibleMemorySize : {int(mem.total/1024)}\nFreePhysicalMemory : {int(mem.available/1024)}"
        except:
            WMIC_AVAILABLE = False
            get_cpu_temperature = lambda: None
            get_cpu_load = lambda: None
            get_memory_info = lambda: None

def get_system_info():
    """Sistem bilgilerini al"""
    # CPU kullanımı
    cpu_usage = get_cpu_load()
    
    # RAM kullanımı
    mem_info_str = get_memory_info()
    mem_percent = None
    
    if mem_info_str:
        try:
            lines = [l.strip() for l in str(mem_info_str).split('\n') if l.strip()]
            free_mem = None
            total_mem = None
            
            for line in lines:
                if 'FreePhysicalMemory' in line or 'available' in line.lower():
                    try:
                        free_mem = float(line.split(':')[-1].strip()) / 1024  # MB
                    except:
                        pass
                elif 'TotalVisibleMemorySize' in line or 'total' in line.lower():
                    try:
                        total_mem = float(line.split(':')[-1].strip()) / 1024  # MB
                    except:
                        pass
            
            if free_mem and total_mem:
                used_mem = total_mem - free_mem
                mem_percent = (used_mem / total_mem) * 100
        except:
            pass
    
    return {
        'cpu_usage': cpu_usage,
        'mem_percent': mem_percent
    }

def get_temp_color(temp):
    """Sıcaklığa göre renk döndür"""
    if temp is None:
        return Fore.WHITE
    elif temp < 50:
        return Fore.GREEN
    elif temp < 70:
        return Fore.YELLOW
    elif temp < 85:
        return Fore.RED
    else:
        return Fore.RED + Style.BRIGHT

def display_temperature():
    """Sıcaklık ve sistem bilgilerini göster"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║          SİSTEM İZLEME PANELİ                  ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    # Sistem bilgileri
    info = get_system_info()
    
    print(Fore.WHITE + "  📊 SİSTEM KAYNAKLARI:")
    print(Fore.WHITE + "  " + "─" * 46)
    
    # CPU Kullanımı
    if info['cpu_usage'] is not None:
        cpu_color = Fore.GREEN if info['cpu_usage'] < 50 else Fore.YELLOW if info['cpu_usage'] < 80 else Fore.RED
        bar = "█" * (int(info['cpu_usage']) // 5)
        print(f"  {cpu_color}CPU Kullanımı:  {info['cpu_usage']:>3}% [{bar:<20}]")
    else:
        print(Fore.WHITE + "  CPU Kullanımı:  Okunamadı")
    
    # RAM Kullanımı
    if info['mem_percent'] is not None:
        mem_color = Fore.GREEN if info['mem_percent'] < 50 else Fore.YELLOW if info['mem_percent'] < 80 else Fore.RED
        bar = "█" * (int(info['mem_percent']) // 5)
        print(f"  {mem_color}RAM Kullanımı:  {info['mem_percent']:>3.0f}% [{bar:<20}]")
    else:
        print(Fore.WHITE + "  RAM Kullanımı:  Okunamadı")
    
    print(Fore.WHITE + "\n  🌡️  SICAKLIK BİLGİSİ:")
    print(Fore.WHITE + "  " + "─" * 46)
    
    # CPU Sıcaklığı
    temps = get_cpu_temperature()
    
    if temps:
        avg_temp = sum(temps) / len(temps)
        temp_color = get_temp_color(avg_temp)
        print(f"  {temp_color}CPU Sıcaklığı:  {avg_temp:.1f}°C")
        
        # Uyarı mesajları
        if avg_temp > 85:
            print(Fore.RED + Style.BRIGHT + "\n  ⚠️  UYARI: CPU sıcaklığı çok yüksek!")
            print(Fore.YELLOW + "  💡 Bilgisayarınızı soğutmak için:")
            print(Fore.WHITE + "     • Oyunu kapat ve sistemi dinlendir")
            print(Fore.WHITE + "     • Fan temizliği yap")
            print(Fore.WHITE + "     • Termal macun yenile")
        elif avg_temp > 70:
            print(Fore.YELLOW + "\n  💡 CPU sıcaklığı yüksek, soğutmayı kontrol edin.")
        else:
            print(Fore.GREEN + "\n  ✅ CPU sıcaklığı normal seviyede.")
    else:
        print(Fore.YELLOW + "  ⚠️  Sıcaklık sensörü okunamadı")
        print(Fore.CYAN + "\n  💡 İpucu: Sıcaklık okumak için:")
        print(Fore.WHITE + "     • BIOS/UEFI'den kontrol edebilirsiniz")
        print(Fore.WHITE + "     • HWMonitor gibi üçüncü parti araçlar kullanın")
        print(Fore.WHITE + "     • Üretici yazılımlarını (MSI Afterburner vb.) deneyin")
        if not WMIC_AVAILABLE:
            print(Fore.YELLOW + "     • Not: WMIC sisteminizde yok (Windows 11'de normal)")
    
    print(Fore.WHITE + "\n  " + "─" * 46)
    print(Fore.CYAN + "  Sistem: " + platform.system() + " " + platform.release())
    print(Fore.WHITE + "  ════════════════════════════════════════════════\n")

if __name__ == "__main__":
    # Test
    from colorama import init
    init(autoreset=True)
    display_temperature()
    input("\nDevam etmek için ENTER'a basın...")
