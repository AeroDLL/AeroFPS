"""
AeroFPS PRO - Scheduled Optimization
Zamanlanmış otomatik optimizasyon ve bakım görevleri
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from colorama import Fore, Style
from .logger import log_info, log_success, log_error

SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schedule.json")

# Varsayılan görevler
DEFAULT_TASKS = {
    'daily_cleanup': {
        'name': 'Günlük Temizlik',
        'description': 'Geçici dosyalar ve cache temizliği',
        'enabled': False,
        'time': '03:00',
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    },
    'weekly_optimization': {
        'name': 'Haftalık Optimizasyon',
        'description': 'Tam sistem optimizasyonu',
        'enabled': False,
        'time': '02:00',
        'days': ['Sunday']
    },
    'pre_gaming': {
        'name': 'Oyun Öncesi Hazırlık',
        'description': 'RAM temizliği ve process optimizasyonu',
        'enabled': False,
        'time': '18:00',
        'days': ['Friday', 'Saturday', 'Sunday']
    },
    'startup_optimization': {
        'name': 'Başlangıç Optimizasyonu',
        'description': 'Windows başlangıcında otomatik optimizasyon',
        'enabled': False,
        'trigger': 'startup'
    }
}

def load_schedule():
    """Zamanlama dosyasını yükle"""
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return DEFAULT_TASKS.copy()
    except:
        return DEFAULT_TASKS.copy()

def save_schedule(schedule):
    """Zamanlama dosyasını kaydet"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        log_error(f"Schedule kaydetme hatası: {e}")
        return False

def create_windows_task(task_id, task_data):
    """Windows Task Scheduler'da görev oluştur"""
    try:
        task_name = f"AeroFPS_{task_id}"
        script_path = os.path.abspath(__file__).replace('scheduler.py', f'../AeroFPS.py')
        
        # Görev türüne göre trigger
        if task_data.get('trigger') == 'startup':
            trigger = '/sc onstart'
        else:
            time = task_data.get('time', '03:00')
            days = ','.join(task_data.get('days', ['SUN']))
            trigger = f'/sc weekly /d {days} /st {time}'
        
        # Task oluştur
        cmd = f'schtasks /create /tn "{task_name}" /tr "python \\"{script_path}\\" --scheduled-task {task_id}" {trigger} /ru SYSTEM /rl HIGHEST /f'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        return result.returncode == 0
    except Exception as e:
        log_error(f"Windows task oluşturma hatası: {e}")
        return False

def delete_windows_task(task_id):
    """Windows Task Scheduler'dan görev sil"""
    try:
        task_name = f"AeroFPS_{task_id}"
        cmd = f'schtasks /delete /tn "{task_name}" /f'
        
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return result.returncode == 0
    except:
        return False

def check_task_exists(task_id):
    """Windows Task Scheduler'da görev var mı kontrol et"""
    try:
        task_name = f"AeroFPS_{task_id}"
        result = subprocess.run(
            f'schtasks /query /tn "{task_name}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except:
        return False

def execute_scheduled_task(task_id):
    """Zamanlanmış görevi çalıştır"""
    log_info(f"Zamanlanmış görev çalıştırılıyor: {task_id}")
    
    if task_id == 'daily_cleanup':
        # Günlük temizlik
        subprocess.run('del /s /f /q "C:\\Windows\\Temp\\*.*"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('del /s /f /q "%temp%\\*.*"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('ipconfig /flushdns', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_success("Günlük temizlik tamamlandı")
    
    elif task_id == 'weekly_optimization':
        # Haftalık optimizasyon
        subprocess.run('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61', shell=True, stdout=subprocess.DEVNULL)
        subprocess.run('fsutil behavior set disabledeletenotify 0', shell=True, stdout=subprocess.DEVNULL)
        subprocess.run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f', shell=True, stdout=subprocess.DEVNULL)
        log_success("Haftalık optimizasyon tamamlandı")
    
    elif task_id == 'pre_gaming':
        # Oyun öncesi hazırlık
        try:
            import ctypes
            psapi = ctypes.WinDLL('psapi.dll')
            kernel = ctypes.WinDLL('kernel32.dll')
            psapi.EmptyWorkingSet(kernel.GetCurrentProcess())
        except:
            pass
        log_success("Oyun öncesi hazırlık tamamlandı")
    
    elif task_id == 'startup_optimization':
        # Başlangıç optimizasyonu
        subprocess.run('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61', shell=True, stdout=subprocess.DEVNULL)
        log_success("Başlangıç optimizasyonu tamamlandı")

def show_schedule_status():
    """Zamanlama durumunu göster"""
    schedule = load_schedule()
    
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       ZAMANLANMIŞ OPTİMİZASYON DURUMU          ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    for task_id, task_data in schedule.items():
        enabled = task_data.get('enabled', False)
        status_color = Fore.GREEN if enabled else Fore.RED
        status_text = "✓ Aktif" if enabled else "✗ Pasif"
        
        print(status_color + Style.BRIGHT + f"  {task_data['name']}")
        print(Fore.WHITE + "  " + "─" * 60)
        print(Fore.CYAN + f"  Açıklama: {task_data['description']}")
        print(status_color + f"  Durum: {status_text}")
        
        if task_data.get('trigger') == 'startup':
            print(Fore.YELLOW + "  Tetikleyici: Windows Başlangıcı")
        else:
            time = task_data.get('time', 'Belirtilmemiş')
            days = ', '.join(task_data.get('days', []))
            print(Fore.YELLOW + f"  Zaman: {time}")
            print(Fore.YELLOW + f"  Günler: {days}")
        
        # Windows Task durumu
        if enabled:
            task_exists = check_task_exists(task_id)
            if task_exists:
                print(Fore.GREEN + "  Windows Task: ✓ Kayıtlı")
            else:
                print(Fore.RED + "  Windows Task: ✗ Kayıtlı değil")
        
        print()

def configure_schedule():
    """Zamanlama yapılandırması"""
    schedule = load_schedule()
    
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       ZAMANLANMIŞ OPTİMİZASYON AYARLARI        ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    tasks_list = list(schedule.items())
    
    for i, (task_id, task_data) in enumerate(tasks_list, 1):
        enabled = task_data.get('enabled', False)
        status = "✓" if enabled else "✗"
        color = Fore.GREEN if enabled else Fore.RED
        
        print(color + f"  [{i}] {status} {task_data['name']}")
        print(Fore.WHITE + f"      {task_data['description']}")
    
    print(Fore.WHITE + f"\n  [0] Geri Dön")
    
    choice = input(Fore.GREEN + f"\n  Düzenlemek istediğiniz görev (0-{len(tasks_list)}): ")
    
    try:
        choice_idx = int(choice)
        if choice_idx == 0:
            return
        
        task_id, task_data = tasks_list[choice_idx - 1]
        
        print(Fore.CYAN + f"\n  ⚙️  {task_data['name']} Ayarları")
        print(Fore.WHITE + "  " + "─" * 60)
        
        # Aktif/Pasif
        current_status = "Aktif" if task_data.get('enabled', False) else "Pasif"
        print(Fore.YELLOW + f"  Mevcut Durum: {current_status}")
        
        toggle = input(Fore.GREEN + "  Durumu değiştir? (E/H): ").strip().upper()
        
        if toggle == 'E':
            new_status = not task_data.get('enabled', False)
            task_data['enabled'] = new_status
            
            if new_status:
                # Windows Task oluştur
                print(Fore.YELLOW + "\n  Windows Task Scheduler'a ekleniyor...")
                if create_windows_task(task_id, task_data):
                    print(Fore.GREEN + "  ✅ Görev başarıyla eklendi!")
                    log_success(f"Zamanlanmış görev aktif edildi: {task_data['name']}")
                else:
                    print(Fore.RED + "  ❌ Görev eklenemedi!")
                    task_data['enabled'] = False
            else:
                # Windows Task sil
                print(Fore.YELLOW + "\n  Windows Task Scheduler'dan kaldırılıyor...")
                if delete_windows_task(task_id):
                    print(Fore.GREEN + "  ✅ Görev başarıyla kaldırıldı!")
                    log_success(f"Zamanlanmış görev pasif edildi: {task_data['name']}")
                else:
                    print(Fore.YELLOW + "  ⚠️  Görev zaten kayıtlı değildi")
            
            # Kaydet
            schedule[task_id] = task_data
            save_schedule(schedule)
    
    except (ValueError, IndexError):
        print(Fore.RED + "\n  ❌ Geçersiz seçim!")

def scheduler_menu():
    """Scheduler ana menü"""
    from colorama import init
    init(autoreset=True)
    
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n")
        print("  ╔════════════════════════════════════════════════╗")
        print("  ║       ZAMANLANMIŞ OPTİMİZASYON                 ║")
        print("  ╚════════════════════════════════════════════════╝")
        print(Fore.WHITE + "\n  [1] 📊 Zamanlama Durumunu Görüntüle")
        print(Fore.WHITE + "  [2] ⚙️  Görevleri Yapılandır")
        print(Fore.WHITE + "  [3] ▶️  Görevi Şimdi Çalıştır (Test)")
        print(Fore.WHITE + "  [4] 🗑️  Tüm Görevleri Temizle")
        print(Fore.WHITE + "  [5] ⬅️  Geri Dön\n")
        
        choice = input(Fore.GREEN + "  Seçim (1-5): ")
        
        if choice == '1':
            show_schedule_status()
        
        elif choice == '2':
            configure_schedule()
        
        elif choice == '3':
            schedule = load_schedule()
            tasks_list = list(schedule.items())
            
            print(Fore.CYAN + "\n  ▶️  Test Edilecek Görevi Seçin:")
            for i, (task_id, task_data) in enumerate(tasks_list, 1):
                print(Fore.WHITE + f"  [{i}] {task_data['name']}")
            
            test_choice = input(Fore.GREEN + f"\n  Görev (1-{len(tasks_list)}): ")
            
            try:
                test_idx = int(test_choice) - 1
                task_id, task_data = tasks_list[test_idx]
                
                print(Fore.YELLOW + f"\n  ⚡ {task_data['name']} çalıştırılıyor...")
                execute_scheduled_task(task_id)
                print(Fore.GREEN + "  ✅ Görev tamamlandı!")
            except (ValueError, IndexError):
                print(Fore.RED + "\n  ❌ Geçersiz seçim!")
        
        elif choice == '4':
            confirm = input(Fore.RED + "\n  ⚠️  Tüm zamanlanmış görevler silinecek! Emin misiniz? (E/H): ").strip().upper()
            
            if confirm == 'E':
                schedule = load_schedule()
                for task_id in schedule.keys():
                    delete_windows_task(task_id)
                
                # Schedule dosyasını sıfırla
                save_schedule(DEFAULT_TASKS.copy())
                
                print(Fore.GREEN + "\n  ✅ Tüm görevler temizlendi!")
                log_success("Tüm zamanlanmış görevler temizlendi")
        
        elif choice == '5':
            break
        
        input(Fore.CYAN + "\n  Devam etmek için ENTER'a basın...")

if __name__ == "__main__":
    scheduler_menu()
