"""
AeroFPS PRO - Değişiklik Kaydı Sistemi (ChangeTracker)
Yapılan optimizasyon ve değişiklikleri kayıt altına alır.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from .logger import log_info, log_error

class ChangeTracker:
    """Değişiklikleri JSON formatında yerel diske kaydeder"""
    
    def __init__(self):
        self.log_dir = Path.home() / ".aerofps" / "changes"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Aylık log dosyası
        self.log_file = self.log_dir / f"changes_{datetime.now().strftime('%Y%m')}.json"
        
    def _load_changes(self) -> List[Dict[str, Any]]:
        """Mevcut değişiklikleri yükle"""
        if not self.log_file.exists():
            return []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
        except Exception as e:
            log_error(f"Değişiklik geçmişi okunamadı: {e}")
            return []

    def record(self, module: str, action: str, details: str, status: str = "SUCCESS") -> bool:
        """Yeni bir değişiklik kaydı ekle"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "action": action,
            "details": details,
            "status": status
        }
        
        try:
            changes = self._load_changes()
            changes.append(entry)
            
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(changes, f, indent=4, ensure_ascii=False)
                
            log_info(f"Değişiklik kaydedildi: [{module}] {action}")
            return True
        except Exception as e:
            log_error(f"Değişiklik kaydedilemedi: {e}")
            return False

    def revert_all_changes(self) -> bool:
        """Geri alınabilecek tüm değişiklikleri geri almayı dener"""
        changes = self._load_changes()
        if not changes:
            log_info("Geri alınacak değişiklik bulunamadı.")
            return True
            
        success = True
        for change in reversed(changes):
            module = change.get("module")
            action = change.get("action")
            
            # Geri alma işlemi şimdilik simüle ediliyor veya loglanıyor
            log_warning(f"Geri alma simüle edildi (Manuel müdahale gerekebilir): [{module}] {action}")
            # İleride her modülün kendi revert fonksiyonu buraya entegre edilebilir.
            
        return success

# Global instance
tracker = ChangeTracker()

def record_change(module: str, action: str, details: str, status: str = "SUCCESS") -> bool:
    """Değişiklik kaydetmek için yardımcı fonksiyon"""
    return tracker.record(module, action, details, status)

def revert_all_changes() -> bool:
    """Tüm değişiklikleri geri almak için yardımcı fonksiyon"""
    return tracker.revert_all_changes()
