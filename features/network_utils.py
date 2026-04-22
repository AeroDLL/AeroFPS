"""
AeroFPS PRO - Network Utilities
Ağ bağdaştırıcıları ve network işlemleri yardımcı fonksiyonları
"""
import subprocess

def get_connected_adapters() -> list[str]:
    """Bağlı network adapter isimlerini döndür"""
    try:
        output = subprocess.check_output(
            'netsh interface show interface', 
            shell=True, encoding='utf-8', errors='ignore'
        )
        adapters = []
        for line in output.split('\n'):
            if 'Connected' in line or 'Bağlı' in line:
                parts = line.split()
                if len(parts) >= 4:
                    adapters.append(' '.join(parts[3:]))
        return adapters or ["Ethernet", "Wi-Fi"]
    except Exception:
        return ["Ethernet", "Wi-Fi"]
