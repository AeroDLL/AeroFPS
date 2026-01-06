"""
AeroFPS PRO - Log Sistemi
Tüm işlemleri kaydeder ve görüntüler
"""

import os
import logging
from datetime import datetime

# Log klasörü
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "aerofps.log")

# Logger yapılandırması
def setup_logger():
    """Logger'ı yapılandır"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Logger oluştur
        logger = logging.getLogger('AeroFPS')
        logger.setLevel(logging.INFO)
        
        # Dosya handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Handler ekle
        if not logger.handlers:
            logger.addHandler(file_handler)
        
        return logger
    except Exception as e:
        print(f"⚠️  Log sistemi başlatılamadı: {e}")
        return None

# Global logger
logger = setup_logger()

def log_info(message):
    """Bilgi mesajı logla"""
    if logger:
        logger.info(message)

def log_success(message):
    """Başarı mesajı logla"""
    if logger:
        logger.info(f"✅ {message}")

def log_error(message):
    """Hata mesajı logla"""
    if logger:
        logger.error(f"❌ {message}")

def log_warning(message):
    """Uyarı mesajı logla"""
    if logger:
        logger.warning(f"⚠️  {message}")

def view_logs():
    """Log dosyasını görüntüle"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print("\n" + "="*80)
            print("  📋 AEROFPS PRO - LOG DOSYASI")
            print("="*80 + "\n")
            
            if len(lines) > 50:
                print(f"  (Son 50 satır gösteriliyor - Toplam: {len(lines)} satır)\n")
                lines = lines[-50:]
            
            for line in lines:
                print(f"  {line.rstrip()}")
            
            print("\n" + "="*80)
            print(f"  Log Dosyası: {LOG_FILE}")
            print("="*80)
        else:
            print("\n⚠️  Henüz log kaydı yok.")
    except Exception as e:
        print(f"\n❌ Log görüntüleme hatası: {e}")

def clear_logs():
    """Log dosyasını temizle"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(f"# AeroFPS PRO - Log Temizlendi - {datetime.now()}\n")
            print("\n✅ Log dosyası temizlendi!")
            log_info("Log dosyası kullanıcı tarafından temizlendi")
        else:
            print("\n⚠️  Temizlenecek log yok.")
    except Exception as e:
        print(f"\n❌ Log temizleme hatası: {e}")

if __name__ == "__main__":
    # Test
    log_info("Test mesajı")
    log_success("İşlem başarılı")
    log_error("Test hatası")
    log_warning("Test uyarısı")
    view_logs()
