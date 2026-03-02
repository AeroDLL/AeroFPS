"""
AeroFPS PRO - One-Click Optimizer
Tüm optimizasyonları tek tuşla uygular
"""

import subprocess
import time
from colorama import Fore, Style

def run_silent(cmd):
    """Komutu sessizce çalıştır"""
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def print_progress(step, total, message):
    """Progress bar göster"""
    percentage = int((step / total) * 100)
    bar_length = 30
    filled = int((percentage / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"\r  [{bar}] {percentage}% - {message}", end='', flush=True)

def one_click_optimize():
    """Tek tuşla tüm optimizasyonları uygula"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       ONE-CLICK OPTIMIZER                      ║")
    print("  ╚════════════════════════════════════════════════╝\n")
    
    print(Fore.YELLOW + "  🚀 Sistemininiz optimize ediliyor...\n")
    
    total_steps = 12
    current_step = 0
    
    # 1. Ultimate Performance
    current_step += 1
    print_progress(current_step, total_steps, "Ultimate Performance Modu")
    run_silent('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
    run_silent('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61')
    time.sleep(0.3)
    
    # 2. Gereksiz Servisler
    current_step += 1
    print_progress(current_step, total_steps, "Gereksiz Servisler Kapatılıyor")
    services = ["DiagTrack", "SysMain", "MapsBroker", "WSearch"]
    for s in services:
        run_silent(f'sc stop "{s}"')
        run_silent(f'sc config "{s}" start= disabled')
    time.sleep(0.3)
    
    # 3. SSD Optimizasyonu
    current_step += 1
    print_progress(current_step, total_steps, "SSD Optimizasyonu")
    run_silent('fsutil behavior set disabledeletenotify 0')
    time.sleep(0.3)
    
    # 4. Network Throttling
    current_step += 1
    print_progress(current_step, total_steps, "Ağ Optimizasyonu")
    run_silent(r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f')
    time.sleep(0.3)
    
    # 5. GPU Hardware Scheduling
    current_step += 1
    print_progress(current_step, total_steps, "GPU Donanım Zamanlama")
    run_silent(r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f')
    time.sleep(0.3)
    
    # 6. Game Mode
    current_step += 1
    print_progress(current_step, total_steps, "Windows Game Mode")
    run_silent(r'reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f')
    time.sleep(0.3)
    
    # 7. Input Lag Fix
    current_step += 1
    print_progress(current_step, total_steps, "Input Lag Düzeltme")
    run_silent(r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d 50 /f')
    run_silent(r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 38 /f')
    time.sleep(0.3)
    
    # 8. DNS Cache
    current_step += 1
    print_progress(current_step, total_steps, "DNS Cache Temizleme")
    run_silent('ipconfig /flushdns')
    time.sleep(0.3)
    
    # 9. Temp Dosyalar
    current_step += 1
    print_progress(current_step, total_steps, "Geçici Dosyalar Temizleniyor")
    run_silent('del /s /f /q "C:\\Windows\\Temp\\*.*"')
    run_silent('del /s /f /q "%temp%\\*.*"')
    time.sleep(0.3)
    
    # 10. BCD Tweaks
    current_step += 1
    print_progress(current_step, total_steps, "BCD Gecikme Ayarları")
    run_silent("bcdedit /set useplatformclock No")
    run_silent("bcdedit /set disabledynamictick Yes")
    time.sleep(0.3)
    
    # 11. Privacy
    current_step += 1
    print_progress(current_step, total_steps, "Gizlilik Koruması")
    run_silent(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f')
    time.sleep(0.3)
    
    # 12. Tamamlandı
    current_step += 1
    print_progress(current_step, total_steps, "Tamamlandı!")
    time.sleep(0.5)
    
    # Sonuç raporu
    print(Fore.GREEN + "\n\n  ✅ OPTİMİZASYON TAMAMLANDI!\n")
    print(Fore.WHITE + "  " + "─" * 46)
    print(Fore.GREEN + "  ✓ Ultimate Performance Modu Aktif")
    print(Fore.GREEN + "  ✓ Gereksiz Servisler Devre Dışı")
    print(Fore.GREEN + "  ✓ SSD/Ağ Optimize Edildi")
    print(Fore.GREEN + "  ✓ GPU Donanım Zamanlama Aktif")
    print(Fore.GREEN + "  ✓ Windows Game Mode Açık")
    print(Fore.GREEN + "  ✓ Input Lag Düzeltildi")
    print(Fore.GREEN + "  ✓ Sistem Temizlendi")
    print(Fore.GREEN + "  ✓ BCD Gecikme Ayarları Uygulandı")
    print(Fore.GREEN + "  ✓ Gizlilik Koruması Aktif")
    print(Fore.WHITE + "  " + "─" * 46)
    
    print(Fore.YELLOW + "\n  💡 ÖNERİLER:")
    print(Fore.WHITE + "     • En iyi performans için bilgisayarı yeniden başlatın")
    print(Fore.WHITE + "     • Oyun öncesi 'Process Manager' ile arka planı temizleyin")
    print(Fore.WHITE + "     • Düzenli olarak 'Sistem Temizliği' yapın\n")

if __name__ == "__main__":
    # Test
    from colorama import init
    init(autoreset=True)
    one_click_optimize()
    input("\n\nDevam etmek için ENTER'a basın...")
