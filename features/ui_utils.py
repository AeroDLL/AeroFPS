"""
AeroFPS PRO - UI Utilities
Kullanıcı arayüzü ve terminal çizim yardımcı fonksiyonları
"""
from colorama import Fore, Style

def print_box(title: str, width: int = 50):
    """Standart menü başlığı kutusu çizer"""
    inner = f"       {title}"
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print(f"  ╔{'═' * width}╗")
    print(f"  ║{inner:<{width}}║")
    print(f"  ╚{'═' * width}╝\n")
