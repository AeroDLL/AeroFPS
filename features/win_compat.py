"""
AeroFPS PRO - Windows Komut Uyumluluk Katmanı
WMIC deprecated olduğu için PowerShell alternatiflerini kullanır
"""

import subprocess
import platform

def is_wmic_available():
    """WMIC komutunun kullanılabilir olup olmadığını kontrol et"""
    try:
        result = subprocess.run(
            'wmic /?',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def run_powershell(command, timeout=30):
    """PowerShell komutu çalıştır"""
    try:
        # PowerShell komutunu UTF-8 encoding ile çalıştır
        ps_command = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{command}"'
        result = subprocess.run(
            ps_command,
            shell=True,
            capture_output=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'
        )
        return result.stdout if result.returncode == 0 else None
    except:
        return None

# Global değişken
WMIC_AVAILABLE = is_wmic_available()

def get_cpu_info():
    """CPU bilgisini al (WMIC alternatifi)"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic cpu get loadpercentage,name',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            return output
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = "Get-WmiObject Win32_Processor | Select-Object Name, LoadPercentage | Format-List"
    return run_powershell(ps_cmd)

def get_gpu_info():
    """GPU bilgisini al (WMIC alternatifi)"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic path win32_videocontroller get name,driverversion',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            return output
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = "Get-WmiObject Win32_VideoController | Select-Object Name, DriverVersion | Format-List"
    return run_powershell(ps_cmd)

def get_monitor_refresh_rate():
    """Monitör yenileme hızını al"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic path Win32_VideoController get CurrentRefreshRate,Name',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            return output
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = "Get-WmiObject Win32_VideoController | Select-Object Name, CurrentRefreshRate | Format-List"
    return run_powershell(ps_cmd)

def get_startup_programs():
    """Başlangıç programlarını al"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic startup get caption,command',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            return output
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = "Get-WmiObject Win32_StartupCommand | Select-Object Caption, Command | Format-List"
    return run_powershell(ps_cmd)

def create_restore_point(description="AeroFPS_PRO_Backup"):
    """Sistem geri yükleme noktası oluştur"""
    if WMIC_AVAILABLE:
        try:
            result = subprocess.run(
                f'wmic /Namespace:\\\\root\\default Path SystemRestore Call CreateRestorePoint "{description}", 100, 7',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60
            )
            return result.returncode == 0
        except:
            pass
    
    # PowerShell alternatifi (daha güvenilir)
    ps_cmd = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
    result = run_powershell(ps_cmd)
    return result is not None

def set_process_priority(pid, priority="High"):
    """Process önceliğini ayarla"""
    if WMIC_AVAILABLE:
        try:
            result = subprocess.run(
                f'wmic process where processid="{pid}" CALL setpriority "{priority} priority"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            return result.returncode == 0
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = f'(Get-Process -Id {pid}).PriorityClass = "{priority}"'
    result = run_powershell(ps_cmd)
    return result is not None

def get_cpu_temperature():
    """CPU sıcaklığını al"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature',
                shell=True,
                encoding='utf-8',
                errors='ignore',
                timeout=5
            )
            
            temps = []
            for line in output.split('\n'):
                line = line.strip()
                if line and line.isdigit():
                    celsius = (int(line) / 10) - 273.15
                    temps.append(celsius)
            return temps if temps else None
        except:
            pass
    
    # PowerShell alternatifi (OpenHardwareMonitor gerekebilir)
    ps_cmd = 'Get-WmiObject -Namespace "root/wmi" -Class MSAcpi_ThermalZoneTemperature | Select-Object CurrentTemperature'
    result = run_powershell(ps_cmd)
    if result:
        try:
            temps = []
            for line in result.split('\n'):
                if 'CurrentTemperature' in line or line.strip().isdigit():
                    line = line.split(':')[-1].strip()
                    if line.isdigit():
                        celsius = (int(line) / 10) - 273.15
                        temps.append(celsius)
            return temps if temps else None
        except:
            pass
    
    return None

def get_cpu_load():
    """CPU yük yüzdesini al"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic cpu get loadpercentage',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            for line in output.split('\n'):
                line = line.strip()
                if line and line.isdigit():
                    return int(line)
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = '(Get-WmiObject Win32_Processor).LoadPercentage'
    result = run_powershell(ps_cmd)
    if result:
        try:
            return int(result.strip())
        except:
            pass
    
    return None

def get_memory_info():
    """RAM bilgisini al"""
    if WMIC_AVAILABLE:
        try:
            output = subprocess.check_output(
                'wmic OS get FreePhysicalMemory,TotalVisibleMemorySize',
                shell=True,
                encoding='utf-8',
                errors='ignore'
            )
            return output
        except:
            pass
    
    # PowerShell alternatifi
    ps_cmd = 'Get-WmiObject Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize | Format-List'
    return run_powershell(ps_cmd)

if __name__ == "__main__":
    # Test
    print(f"WMIC Available: {WMIC_AVAILABLE}")
    print("\nTesting commands...")
    
    cpu = get_cpu_load()
    print(f"CPU Load: {cpu}%")
    
    temps = get_cpu_temperature()
    if temps:
        print(f"CPU Temp: {temps[0]:.1f}°C")
    else:
        print("CPU Temp: Not available")
