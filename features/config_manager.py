"""
AeroFPS PRO - Centralized Configuration Manager
Manages all settings, preferences, and configurations
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from .logger import log_info, log_error, log_warning, log_success


class ConfigManager:
    """Centralized configuration management system"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".aerofps"
        self.config_file = self.config_dir / "config.json"
        self.backup_file = self.config_dir / "config.backup.json"
        self.config = {}
        self._load()
    
    def _ensure_dir(self):
        """Ensure config directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            log_info(f"Config directory: {self.config_dir}")
        except Exception as e:
            log_error(f"Failed to create config directory: {e}")
    
    def _load(self):
        """Load configuration from file"""
        self._ensure_dir()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self._validate_schema(self.config)
                log_success(f"Config loaded from {self.config_file}")
            except json.JSONDecodeError:
                log_warning(f"Config file corrupted, using defaults")
                self.config = self._default_config()
            except Exception as e:
                log_error(f"Failed to load config: {e}")
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save()
            
    def _validate_schema(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration schema types and values"""
        if not isinstance(config_data.get('language'), str):
            config_data['language'] = "EN"
            log_warning("Config validation: 'language' must be a string. Reset to default.")
            
        if 'auto_start' in config_data and not isinstance(config_data['auto_start'], bool):
            config_data['auto_start'] = False
            log_warning("Config validation: 'auto_start' must be a boolean. Reset to default.")
            
        if 'games' in config_data and not isinstance(config_data['games'], (list, dict)):
            config_data['games'] = self._default_config()['games']
            log_warning("Config validation: 'games' must be a list or dict. Reset to default.")
    
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Default configuration structure"""
        return {
            "version": "1.0",
            "language": "EN",
            "theme": "dark",
            "auto_backup": True,
            
            # Optimization settings
            "optimization": {
                "one_click_enabled": True,
                "auto_cleanup": True,
                "aggressive_mode": False,
                "enable_rollback": True,
            },
            
            # Game-related settings
            "games": {
                "auto_detect": True,
                "managed_games": [
                    "cs2.exe", "valorant.exe", 
                    "fortniteclient-win64-shipping.exe", 
                    "apexlegends.exe"
                ],
                "config_backup": True,
            },
            
            # Network settings
            "network": {
                "use_cloudflare_dns": True,
                "use_google_dns": False,
                "ping_monitor_enabled": True,
                "packet_loss_alert": True,
            },
            
            # Process management
            "process_management": {
                "boost_game_priority": True,
                "kill_background_apps": True,
                "safe_kill_only": True,
            },
            
            # Monitoring
            "monitoring": {
                "temp_monitor_enabled": True,
                "temp_alert_cpu": 85,
                "temp_alert_gpu": 85,
                "log_level": "INFO",
            },
            
            # Scheduler
            "scheduler": {
                "daily_cleanup": {
                    "enabled": True,
                    "time": "02:00"
                },
                "weekly_optimization": {
                    "enabled": True,
                    "day": "Sunday",
                    "time": "03:00"
                },
                "startup_optimization": {
                    "enabled": False
                }
            },
            
            # Advanced
            "advanced": {
                "enable_telemetry": False,
                "crash_reports": True,
                "check_updates": True,
                "dev_mode": False,
            }
        }
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            self._ensure_dir()
            
            # Create backup
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as src:
                        with open(self.backup_file, 'w') as dst:
                            dst.write(src.read())
                except Exception as e:
                    pass
            
            # Write new config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            log_success(f"Config saved to {self.config_file}")
            return True
        
        except Exception as e:
            log_error(f"Failed to save config: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Restore configuration from backup"""
        try:
            if not self.backup_file.exists():
                log_warning("No backup file found")
                return False
            
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            log_success("Config restored from backup")
            return self.save()
        
        except Exception as e:
            log_error(f"Failed to restore backup: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value (supports nested keys with dots)
        
        Example:
            config.get("optimization.aggressive_mode")
        """
        try:
            parts = key.split('.')
            value = self.config
            
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return default
            
            return value if value is not None else default
        
        except Exception as e:
            log_warning(f"Error getting config key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value (supports nested keys with dots)
        
        Example:
            config.set("optimization.aggressive_mode", True)
        """
        try:
            parts = key.split('.')
            current = self.config
            
            # Navigate to the parent dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[parts[-1]] = value
            log_info(f"Config set: {key} = {value}")
            
            return self.save()
        
        except Exception as e:
            log_error(f"Failed to set config {key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all configuration to defaults"""
        try:
            self.config = self._default_config()
            log_warning("Config reset to defaults")
            return self.save()
        
        except Exception as e:
            log_error(f"Failed to reset config: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self.config.copy()
    
    def merge(self, new_config: Dict[str, Any]) -> bool:
        """Merge new config values without overwriting all"""
        try:
            self._deep_merge(self.config, new_config)
            log_info("Config merged successfully")
            return self.save()
        
        except Exception as e:
            log_error(f"Failed to merge config: {e}")
            return False
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        """Deep merge override dict into base dict"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigManager._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def to_json(self) -> str:
        """Export config as JSON string"""
        try:
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Failed to export config: {e}")
            return "{}"
    
    def from_json(self, json_str: str) -> bool:
        """Import config from JSON string"""
        try:
            new_config = json.loads(json_str)
            self.config = new_config
            log_success("Config imported from JSON")
            return self.save()
        
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON config: {e}")
            return False
        except Exception as e:
            log_error(f"Failed to import config: {e}")
            return False


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global config instance (singleton)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reset_config():
    """Reset global config instance"""
    global _config_instance
    _config_instance = None


if __name__ == "__main__":
    # Test ConfigManager
    print("Testing ConfigManager...")
    
    config = ConfigManager()
    
    # Get values
    print(f"Language: {config.get('language')}")
    print(f"Aggressive Mode: {config.get('optimization.aggressive_mode')}")
    
    # Set values
    config.set('language', 'TR')
    config.set('optimization.aggressive_mode', True)
    
    # Get all
    print(f"\nFull config:\n{config.to_json()}")
    
    print("\n✅ ConfigManager test completed!")
