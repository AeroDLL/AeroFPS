"""
AeroFPS PRO - Cloud Backup & Sync
Konfigürasyon ve log dosyalarını bulut yedekleme sistemi
"""

import os
import json
import time
import hashlib
from pathlib import Path
from colorama import Fore, Style
from .logger import log_info, log_error, log_debug

class CloudBackup:
    """Cloud backup and sync system"""

    def __init__(self):
        self.backup_dir = Path.home() / "AeroFPS_Backup"
        self.config_file = self.backup_dir / "backup_config.json"
        self.backup_manifest = self.backup_dir / "backup_manifest.json"
        self.backup_dir.mkdir(exist_ok=True)
        self.load_config()

    def load_config(self):
        """Backup konfigürasyonunu yükle"""
        default_config = {
            'auto_backup': True,
            'backup_interval_hours': 24,
            'max_backups': 10,
            'compress_backups': True,
            'cloud_sync': False,
            'cloud_provider': 'local',  # local, dropbox, google_drive, onedrive
            'last_backup': 0,
            'backup_files': [
                'config.json',
                'logs/aerofps.log',
                'logs/aerofps.json',
                'models/performance_predictor.pkl',
                'training_data.json'
            ]
        }

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            log_debug(f"Backup config load error: {e}")

        self.config = default_config
        self.save_config()

    def save_config(self):
        """Backup konfigürasyonunu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Backup config save error: {e}")

    def should_backup(self):
        """Backup yapılıp yapılmayacağını kontrol et"""
        if not self.config['auto_backup']:
            return False

        current_time = time.time()
        time_since_last = current_time - self.config['last_backup']
        interval_seconds = self.config['backup_interval_hours'] * 3600

        return time_since_last >= interval_seconds

    def create_backup(self, force=False):
        """Backup oluştur"""
        if not force and not self.should_backup():
            return False

        print(Fore.CYAN + "\n☁️  Cloud Backup Sistemi\n")
        print(Fore.YELLOW + "Konfigürasyon ve log dosyaları yedekleniyor...")

        try:
            # Backup klasörü oluştur
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_folder = self.backup_dir / f"backup_{timestamp}"
            backup_folder.mkdir(exist_ok=True)

            # Dosyaları yedekle
            backed_up_files = []
            total_size = 0

            for file_path in self.config['backup_files']:
                src_path = Path(__file__).parent.parent / file_path

                if src_path.exists():
                    # Dosya hash hesapla (değişiklik kontrolü için)
                    file_hash = self._calculate_file_hash(src_path)

                    # Dosyayı kopyala
                    dest_path = backup_folder / src_path.name
                    with open(src_path, 'rb') as src, open(dest_path, 'wb') as dest:
                        dest.write(src.read())

                    backed_up_files.append({
                        'original_path': str(src_path),
                        'backup_path': str(dest_path),
                        'size': src_path.stat().st_size,
                        'hash': file_hash,
                        'timestamp': time.time()
                    })

                    total_size += src_path.stat().st_size
                    print(Fore.GREEN + f"  ✓ {file_path}")
                else:
                    print(Fore.YELLOW + f"  ⚠️  {file_path} bulunamadı")

            # Manifest oluştur
            manifest = {
                'timestamp': time.time(),
                'backup_id': timestamp,
                'total_files': len(backed_up_files),
                'total_size': total_size,
                'files': backed_up_files,
                'system_info': {
                    'platform': os.sys.platform,
                    'python_version': os.sys.version.split()[0]
                }
            }

            manifest_path = backup_folder / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            # Config'i güncelle
            self.config['last_backup'] = time.time()
            self.save_config()

            # Eski backup'ları temizle
            self._cleanup_old_backups()

            print(Fore.GREEN + f"\n✅ Backup tamamlandı!")
            print(Fore.CYAN + f"📁 Konum: {backup_folder}")
            print(Fore.CYAN + f"📊 Boyut: {total_size / 1024:.1f} KB")
            print(Fore.CYAN + f"📄 Dosya: {len(backed_up_files)} adet")

            return True

        except Exception as e:
            log_error(f"Backup creation error: {e}")
            print(Fore.RED + f"❌ Backup hatası: {e}")
            return False

    def restore_backup(self, backup_id=None):
        """Backup'tan geri yükle"""
        print(Fore.CYAN + "\n🔄 Backup Geri Yükleme\n")

        if not backup_id:
            # En son backup'ı bul
            backups = list(self.backup_dir.glob("backup_*"))
            if not backups:
                print(Fore.RED + "❌ Hiç backup bulunamadı!")
                return False

            backups.sort(reverse=True)
            backup_folder = backups[0]
            backup_id = backup_folder.name
        else:
            backup_folder = self.backup_dir / backup_id

        if not backup_folder.exists():
            print(Fore.RED + f"❌ Backup bulunamadı: {backup_id}")
            return False

        print(Fore.YELLOW + f"Seçilen backup: {backup_id}")
        print(Fore.YELLOW + "Bu işlem mevcut dosyaları değiştirecek!")

        # Onay al
        confirm = input(Fore.RED + "Devam etmek istiyor musunuz? (y/N): ").lower().strip()
        if confirm != 'y':
            print(Fore.YELLOW + "İptal edildi.")
            return False

        try:
            # Manifest oku
            manifest_path = backup_folder / "manifest.json"
            if not manifest_path.exists():
                print(Fore.RED + "❌ Manifest dosyası bulunamadı!")
                return False

            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # Dosyaları geri yükle
            restored_count = 0
            for file_info in manifest['files']:
                backup_path = Path(file_info['backup_path'])
                original_path = Path(file_info['original_path'])

                if backup_path.exists():
                    # Orijinal dosyanın yedeğini al
                    if original_path.exists():
                        backup_original = original_path.with_suffix(original_path.suffix + '.backup')
                        with open(original_path, 'rb') as src, open(backup_original, 'wb') as dest:
                            dest.write(src.read())

                    # Backup'tan geri yükle
                    with open(backup_path, 'rb') as src, open(original_path, 'wb') as dest:
                        dest.write(src.read())

                    restored_count += 1
                    print(Fore.GREEN + f"  ✓ {original_path.name}")

            print(Fore.GREEN + f"\n✅ Geri yükleme tamamlandı!")
            print(Fore.CYAN + f"📄 Geri yüklenen dosya: {restored_count} adet")
            print(Fore.YELLOW + "💡 Orijinal dosyalar .backup uzantısı ile yedeklendi")

            return True

        except Exception as e:
            log_error(f"Backup restore error: {e}")
            print(Fore.RED + f"❌ Geri yükleme hatası: {e}")
            return False

    def list_backups(self):
        """Mevcut backup'ları listele"""
        print(Fore.CYAN + "\n📋 Mevcut Backup'lar\n")

        backups = list(self.backup_dir.glob("backup_*"))
        if not backups:
            print(Fore.YELLOW + "Henüz hiç backup oluşturulmamış.")
            return []

        backups.sort(reverse=True)

        backup_list = []
        for i, backup in enumerate(backups[:10], 1):  # Son 10 backup
            try:
                manifest_path = backup / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)

                    size_mb = manifest['total_size'] / (1024 * 1024)
                    file_count = manifest['total_files']
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(manifest['timestamp']))

                    status = "✅" if i == 1 else "📁"
                    print(f"{status} {i}. {backup.name}")
                    print(f"      📅 {timestamp}")
                    print(f"      📊 {file_count} dosya, {size_mb:.1f} MB")
                    print()

                    backup_list.append({
                        'id': backup.name,
                        'timestamp': manifest['timestamp'],
                        'size': manifest['total_size'],
                        'files': file_count
                    })
                else:
                    print(f"📁 {i}. {backup.name} (Manifest eksik)")
                    print()
            except Exception as e:
                print(f"❌ {i}. {backup.name} (Okunamadı: {e})")
                print()

        return backup_list

    def _calculate_file_hash(self, file_path):
        """Dosya hash hesapla"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def _cleanup_old_backups(self):
        """Eski backup'ları temizle"""
        try:
            backups = list(self.backup_dir.glob("backup_*"))
            max_backups = self.config['max_backups']

            if len(backups) > max_backups:
                backups.sort()
                to_delete = backups[:-max_backups]  # En eski olanları sil

                for backup in to_delete:
                    import shutil
                    shutil.rmtree(backup)
                    log_debug(f"Old backup deleted: {backup.name}")

        except Exception as e:
            log_debug(f"Cleanup error: {e}")

    def sync_to_cloud(self):
        """Cloud'a senkronize et (gelecek özellik)"""
        if not self.config['cloud_sync']:
            return False

        provider = self.config['cloud_provider']
        print(Fore.CYAN + f"\n☁️  {provider.upper()} Cloud Sync\n")
        print(Fore.YELLOW + "Bu özellik henüz geliştirme aşamasında.")
        print(Fore.CYAN + "Desteklenen sağlayıcılar: Dropbox, Google Drive, OneDrive")

        return False

# Global backup instance
backup_system = CloudBackup()

def create_backup(force=False):
    """Backup oluştur"""
    return backup_system.create_backup(force)

def restore_backup(backup_id=None):
    """Backup'tan geri yükle"""
    return backup_system.restore_backup(backup_id)

def list_backups():
    """Backup'ları listele"""
    return backup_system.list_backups()

def configure_backup():
    """Backup ayarlarını yapılandır"""
    print(Fore.CYAN + "\n⚙️  Backup Yapılandırması\n")

    print(Fore.WHITE + "Mevcut ayarlar:")
    config = backup_system.config
    print(f"  Otomatik backup: {config['auto_backup']}")
    print(f"  Backup aralığı: {config['backup_interval_hours']} saat")
    print(f"  Maksimum backup: {config['max_backups']} adet")
    print(f"  Cloud sync: {config['cloud_sync']}")

    print(Fore.YELLOW + "\nBu özellik henüz geliştirme aşamasında.")
    print(Fore.CYAN + "Şimdilik sadece yerel backup destekleniyor.")</content>
<parameter name="filePath">c:\Users\Cyberhan\Desktop\PROJELER\AeroFPS-main\features\cloud_backup.py