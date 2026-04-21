"""
AeroFPS PRO - Advanced Log Sistemi
Structured logging ile detaylı kayıt sistemi
"""

import os
import logging
import json
import sys
from datetime import datetime
from functools import wraps

# Import constants
try:
    from .constants import LOG_LEVELS, LOG_MAX_LINES
except ImportError:
    LOG_LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }
    LOG_MAX_LINES = 50

# Log klasörü
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "aerofps.log")
LOG_JSON_FILE = os.path.join(LOG_DIR, "aerofps.json")

class StructuredFormatter(logging.Formatter):
    """JSON formatlı structured logging formatter"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'pid': os.getpid(),
            'thread': record.thread,
        }

        # Ekstra field'ları ekle
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)

def setup_logger():
    """Gelişmiş logger'ı yapılandır"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        # Ana logger
        logger = logging.getLogger('AeroFPS')
        logger.setLevel(logging.DEBUG)  # Tüm seviyeleri yakala

        # Console handler (basit format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        # File handler (detaylı text format)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)-12s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # JSON handler (structured logging)
        json_handler = logging.FileHandler(LOG_JSON_FILE, encoding='utf-8')
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(StructuredFormatter())

        # Handler'ları ekle
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            logger.addHandler(json_handler)

        return logger
    except Exception as e:
        print(f"⚠️  Log sistemi başlatılamadı: {e}")
        return None

# Global logger
logger = setup_logger()

def log_with_context(level='INFO', extra_data=None):
    """Context ile loglama decorator'ı"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Başarılı işlem logla
                log_message = f"{func.__name__} completed successfully"
                if extra_data:
                    log_message += f" | {extra_data}"
                getattr(logger, level.lower())(log_message, extra={'extra_data': extra_data or {}})
                return result
            except Exception as e:
                # Hata logla
                error_msg = f"{func.__name__} failed: {str(e)}"
                logger.error(error_msg, extra={
                    'extra_data': {
                        'function': func.__name__,
                        'args': str(args)[:100],  # İlk 100 karakter
                        'error_type': type(e).__name__,
                        'error': str(e)
                    }
                })
                raise
        return wrapper
    return decorator

def log_info(message, extra_data=None):
    """Bilgi mesajı logla"""
    if logger:
        logger.info(message, extra={'extra_data': extra_data or {}})

def log_success(message, extra_data=None):
    """Başarı mesajı logla"""
    if logger:
        logger.info(f"✅ {message}", extra={'extra_data': extra_data or {}})

def log_error(message, extra_data=None):
    """Hata mesajı logla"""
    if logger:
        logger.error(f"❌ {message}", extra={'extra_data': extra_data or {}})

def log_warning(message, extra_data=None):
    """Uyarı mesajı logla"""
    if logger:
        logger.warning(f"⚠️  {message}", extra={'extra_data': extra_data or {}})

def log_debug(message, extra_data=None):
    """Debug mesajı logla"""
    if logger:
        logger.debug(message, extra={'extra_data': extra_data or {}})

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
