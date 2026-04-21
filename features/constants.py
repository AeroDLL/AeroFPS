"""
AeroFPS PRO - Constants and Configuration
Tüm sabitler ve yapılandırma değerleri burada toplanmıştır
"""

import os
import json
from pathlib import Path

# Config file path
CONFIG_FILE = Path(__file__).parent.parent / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "debug_mode": False,
    "auto_update": True,
    "backup_before_changes": True,
    "aggressive_optimization": False,
    "custom_game_servers": {},
    "excluded_processes": [],
    "log_level": "INFO",
    "max_cache_size": 100,
    "cache_timeout": 300
}

def load_runtime_config():
    """Runtime configuration yükle"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Default config ile birleştir
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        else:
            # Config dosyası yoksa oluştur
            save_runtime_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"⚠️  Config yüklenirken hata: {e}")
        return DEFAULT_CONFIG

def save_runtime_config(config):
    """Runtime configuration kaydet"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Config kaydedilirken hata: {e}")

# Global config
CONFIG = load_runtime_config()

# Timeout Constants

# Timeout Constants
TIMEOUT_SHORT = 5      # Kısa işlemler (registry, service)
TIMEOUT_MEDIUM = 10    # Orta işlemler (network, ping)
TIMEOUT_LONG = 30      # Uzun işlemler (download, complex tasks)
TIMEOUT_EXTRA_LONG = 60 # Çok uzun işlemler (system analysis)

# Process Management
PROCESS_WAIT_TIMEOUT = 3  # Process termination bekleme süresi
MAX_RETRY_ATTEMPTS = 3    # Maximum retry sayısı

# Network Settings
PING_COUNT_DEFAULT = 4    # Varsayılan ping sayısı
DNS_TIMEOUT = 10          # DNS resolution timeout

# Registry Values
REGISTRY_BACKUP_SUFFIX = "_backup.reg"
HW_SCH_MODE_VALUE = 2     # GPU Hardware Scheduling
GAME_MODE_VALUE = 1       # Windows Game Mode
NETWORK_THROTTLING_VALUE = 4294967295  # Disable throttling

# Temperature Thresholds
TEMP_COOL = 50    # Soğuk
TEMP_WARM = 70    # Ilık
TEMP_HOT = 85     # Sıcak

# Memory Thresholds (GB)
RAM_LOW = 8       # Minimum recommended RAM
RAM_CRITICAL = 4  # Critical RAM level

# CPU Thresholds
CPU_LOW_LOAD = 50     # Low CPU usage threshold
CPU_HIGH_LOAD = 80    # High CPU usage threshold

# File Sizes
EXE_SIZE_WARNING = 50 * 1024 * 1024  # 50MB warning threshold

# UI Constants
BANNER_WIDTH = 70
PROGRESS_BAR_WIDTH = 30
LOG_MAX_LINES = 50

# Log Levels
LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
}

# Dynamic constants based on config
LOG_MAX_LINES = CONFIG.get('max_cache_size', 50)
CACHE_TIMEOUT = CONFIG.get('cache_timeout', 300)
DEBUG_MODE = CONFIG.get('debug_mode', False)
UNNECESSARY_SERVICES = [
    "DiagTrack", "SysMain", "MapsBroker", "WSearch", "TabletInputService"
]

BACKGROUND_APPS = [
    "discord.exe", "spotify.exe", "chrome.exe", "msedge.exe",
    "steam.exe", "epicgameslauncher.exe", "origin.exe",
    "skype.exe", "teams.exe", "onedrive.exe"
]

# Game Servers for Ping Test
GAME_SERVERS = {
    'Valorant EU': 'riot-geo.ff.avast.com',
    'CS2 EU': 'valve.vo.llnwd.net',
    'Fortnite EU': 'qosping-aws-eu-west-1.ol.epicgames.com',
    'League EU': 'prod.euw1.lol.riotgames.com',
    'Cloudflare': '1.1.1.1',
    'Google DNS': '8.8.8.8',
}

# Registry Keys (commonly used)
REG_KEYS = {
    'gpu_hw_sch': r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
    'game_mode': r"HKCU\SOFTWARE\Microsoft\GameBar",
    'network_throttling': r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
}

# Color Codes for Temperature
TEMP_COLORS = {
    'cool': '\033[92m',    # Green
    'warm': '\033[93m',    # Yellow
    'hot': '\033[91m',     # Red
    'reset': '\033[0m'     # Reset
}

# Log Levels
LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
}

# Version Info
VERSION = "PRO v1.1"
AUTHOR = "AeroDLL"
GITHUB_URL = "https://github.com/AeroDLL/AeroFPS"