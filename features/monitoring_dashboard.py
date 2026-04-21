"""
AeroFPS PRO - Real-Time Monitoring Dashboard
Canlı sistem izleme ve performans metrikleri
"""

import time
import threading
import psutil
from colorama import Fore, Style, init
from .logger import log_info, log_debug
from .smart_advisor import get_system_specs, ai_predictor

# Colorama init
init(autoreset=True)

class MonitoringDashboard:
    """Real-time monitoring dashboard"""

    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history = {
            'cpu': [],
            'ram': [],
            'fps': [],
            'network': []
        }
        self.max_history = 60  # 60 saniye veri

    def start_monitoring(self):
        """Monitoring'i başlat"""
        if self.is_monitoring:
            print(Fore.YELLOW + "⚠️  Monitoring zaten çalışıyor!")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        print(Fore.GREEN + "✅ Real-Time Monitoring başlatıldı!")
        print(Fore.CYAN + "Çıkmak için Ctrl+C basın...\n")

        try:
            self._display_dashboard()
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self):
        """Monitoring'i durdur"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print(Fore.YELLOW + "\n⚠️  Monitoring durduruldu.")

    def _monitor_loop(self):
        """Monitoring ana döngüsü"""
        while self.is_monitoring:
            try:
                # Sistem metriklerini topla
                metrics = self._collect_metrics()

                # Geçmişe ekle
                self._add_to_history(metrics)

                time.sleep(1)  # 1 saniye bekle

            except Exception as e:
                log_debug(f"Monitoring error: {e}")
                time.sleep(1)

    def _collect_metrics(self):
        """Sistem metriklerini topla"""
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'ram_percent': psutil.virtual_memory().percent,
            'ram_used_gb': round(psutil.virtual_memory().used / (1024**3), 1),
            'disk_read': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            'disk_write': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
            'network_sent': psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
            'network_recv': psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0,
            'active_processes': len(psutil.pids())
        }

    def _add_to_history(self, metrics):
        """Metrikleri geçmişe ekle"""
        for key, value in metrics.items():
            if key in self.metrics_history:
                self.metrics_history[key].append(value)
                # Maksimum history'yi koru
                if len(self.metrics_history[key]) > self.max_history:
                    self.metrics_history[key].pop(0)

    def _display_dashboard(self):
        """Dashboard'u göster"""
        while self.is_monitoring:
            # Ekranı temizle
            print("\033[2J\033[H", end="")

            # Header
            print(Fore.CYAN + Style.BRIGHT + "╔══════════════════════════════════════════════════════════════════════════════╗")
            print(Fore.CYAN + "║                        🚀 AERO FPS - MONITORING DASHBOARD                    ║")
            print(Fore.CYAN + "╚══════════════════════════════════════════════════════════════════════════════╝")

            # Sistem özeti
            specs = get_system_specs()
            print(Fore.WHITE + f"\n📊 SİSTEM: {specs['cpu_cores']}C/{specs['cpu_threads']}T CPU | {specs['ram_gb']}GB RAM | {specs['disk_type']}")

            # Real-time metrikler
            if self.metrics_history['cpu']:
                current = self.metrics_history['cpu'][-1]
                avg_10s = sum(self.metrics_history['cpu'][-10:]) / min(10, len(self.metrics_history['cpu']))

                print(Fore.WHITE + "\n" + "═" * 78)
                print(Fore.YELLOW + "🔥 REAL-TIME METRİKLER:")
                print(Fore.WHITE + "═" * 78)

                # CPU
                cpu_color = Fore.GREEN if current < 50 else Fore.YELLOW if current < 80 else Fore.RED
                print(f"CPU Kullanım: {cpu_color}{current:5.1f}%{Fore.WHITE} | 10sn Ort: {avg_10s:5.1f}% | Frekans: {self.metrics_history.get('cpu_freq', [0])[-1]:.0f}MHz")

                # RAM
                ram_current = self.metrics_history['ram'][-1] if self.metrics_history['ram'] else 0
                ram_used = self.metrics_history.get('ram_used_gb', [0])[-1]
                ram_color = Fore.GREEN if ram_current < 70 else Fore.YELLOW if ram_current < 85 else Fore.RED
                print(f"RAM Kullanım: {ram_color}{ram_current:5.1f}%{Fore.WHITE} | Kullanılan: {ram_used:.1f}GB / {specs['ram_gb']}GB")

                # Process
                proc_current = self.metrics_history.get('active_processes', [0])[-1]
                proc_color = Fore.GREEN if proc_current < 150 else Fore.YELLOW if proc_current < 200 else Fore.RED
                print(f"Aktif Process: {proc_color}{proc_current:4d}{Fore.WHITE}")

                # AI FPS Tahmini
                if hasattr(ai_predictor, 'is_trained') and ai_predictor.is_trained:
                    ai_fps = ai_predictor.predict_fps(specs)
                    if ai_fps:
                        fps_color = Fore.GREEN if ai_fps > 120 else Fore.YELLOW if ai_fps > 60 else Fore.RED
                        print(f"AI FPS Tahmini: {fps_color}{ai_fps:6.0f} FPS{Fore.WHITE} (ortalama oyunlarda)")

                # Grafik gösterimi (basit bar chart)
                print(Fore.WHITE + "\n" + "═" * 78)
                print(Fore.CYAN + "📈 SON 30 SANİYE GRAFİĞİ:")
                print(Fore.WHITE + "═" * 78)

                # CPU grafiği
                cpu_data = self.metrics_history['cpu'][-30:] if len(self.metrics_history['cpu']) >= 30 else self.metrics_history['cpu']
                if cpu_data:
                    print(Fore.YELLOW + "CPU: " + self._create_bar_chart(cpu_data, 50))

                # RAM grafiği
                ram_data = self.metrics_history['ram'][-30:] if len(self.metrics_history['ram']) >= 30 else self.metrics_history['ram']
                if ram_data:
                    print(Fore.BLUE + "RAM: " + self._create_bar_chart(ram_data, 50))

                # Alt bilgi
                print(Fore.WHITE + "\n" + "═" * 78)
                print(Fore.CYAN + "💡 İPUÇLARI:")
                print(Fore.WHITE + "• CPU > 80%: Arka plan uygulamalarını kapatın")
                print(Fore.WHITE + "• RAM > 85%: RAM temizleme yapın")
                print(Fore.WHITE + "• Process > 200: Sistem optimizasyonu yapın")
                print(Fore.WHITE + "• Ctrl+C ile çıkın")
                print(Fore.WHITE + "═" * 78)

            time.sleep(2)  # 2 saniyede bir güncelle

    def _create_bar_chart(self, data, width=50):
        """Basit bar chart oluştur"""
        if not data:
            return ""

        max_val = max(data) if data else 100
        min_val = min(data) if data else 0

        # Normalize et
        normalized = [(x - min_val) / (max_val - min_val) if max_val > min_val else 0.5 for x in data]

        # Bar oluştur
        bars = []
        for val in normalized:
            bar_length = int(val * width)
            bar = "█" * bar_length + "░" * (width - bar_length)
            bars.append(bar)

        return "".join(bars[-width:])  # Son width karakteri al

    def get_performance_report(self):
        """Performans raporu oluştur"""
        if not self.metrics_history['cpu']:
            return "Yeterli veri yok"

        report = {
            'avg_cpu': sum(self.metrics_history['cpu']) / len(self.metrics_history['cpu']),
            'max_cpu': max(self.metrics_history['cpu']),
            'avg_ram': sum(self.metrics_history['ram']) / len(self.metrics_history['ram']) if self.metrics_history['ram'] else 0,
            'max_ram': max(self.metrics_history['ram']) if self.metrics_history['ram'] else 0,
            'monitoring_duration': len(self.metrics_history['cpu'])
        }

        return report

# Global dashboard instance
dashboard = MonitoringDashboard()

def start_monitoring_dashboard():
    """Monitoring dashboard'u başlat"""
    dashboard.start_monitoring()

def get_monitoring_report():
    """Monitoring raporunu al"""
    return dashboard.get_performance_report()</content>
<parameter name="filePath">c:\Users\Cyberhan\Desktop\PROJELER\AeroFPS-main\features\monitoring_dashboard.py