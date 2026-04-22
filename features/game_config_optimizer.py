"""
AeroFPS PRO - Oyun İçi Ayar Önerileri
Popüler oyunlar için optimal grafik ayarları ve config dosyası optimizasyonu
"""

import os
import json
from colorama import Fore, Style
from .logger import log_info, log_success, log_warning

# Popüler oyunlar ve config dosyaları
GAME_CONFIGS = {
    'CS2': {
        'name': 'Counter-Strike 2',
        'config_path': r'%USERPROFILE%\AppData\Local\cs2\cfg\autoexec.cfg',
        'settings': {
            'Competitive (Max FPS)': {
                'fps_max': '0',
                'fps_max_menu': '120',
                'mat_queue_mode': '2',
                'r_dynamic': '0',
                'r_drawtracers_firstperson': '0',
                'cl_forcepreload': '1',
                'cl_showfps': '1',
                'cl_interp': '0',
                'cl_interp_ratio': '1',
                'rate': '786432',
                'cl_updaterate': '128',
                'cl_cmdrate': '128',
            },
            'Balanced (Quality + FPS)': {
                'fps_max': '300',
                'mat_queue_mode': '2',
                'r_dynamic': '1',
                'cl_forcepreload': '1',
                'cl_showfps': '1',
            }
        }
    },
    'Valorant': {
        'name': 'Valorant',
        'config_path': r'%LOCALAPPDATA%\VALORANT\Saved\Config\Windows\GameUserSettings.ini',
        'settings': {
            'Competitive (Max FPS)': {
                'ResolutionQuality': '100',
                'ViewDistanceQuality': '0',
                'AntiAliasingQuality': '0',
                'ShadowQuality': '0',
                'PostProcessQuality': '0',
                'TextureQuality': '0',
                'EffectsQuality': '0',
                'FoliageQuality': '0',
                'VSync': '0',
                'MotionBlur': '0',
            },
            'Balanced': {
                'ResolutionQuality': '100',
                'ViewDistanceQuality': '1',
                'AntiAliasingQuality': '1',
                'ShadowQuality': '1',
                'TextureQuality': '2',
                'VSync': '0',
                'MotionBlur': '0',
            }
        }
    },
    'Fortnite': {
        'name': 'Fortnite',
        'config_path': r'%LOCALAPPDATA%\FortniteGame\Saved\Config\WindowsClient\GameUserSettings.ini',
        'settings': {
            'Competitive (Max FPS)': {
                'sg.ResolutionQuality': '100',
                'sg.ViewDistanceQuality': '0',
                'sg.AntiAliasingQuality': '0',
                'sg.ShadowQuality': '0',
                'sg.PostProcessQuality': '0',
                'sg.TextureQuality': '0',
                'sg.EffectsQuality': '0',
                'sg.FoliageQuality': '0',
                'bMotionBlur': 'False',
                'bShowFPS': 'True',
            }
        }
    },
    'Apex Legends': {
        'name': 'Apex Legends',
        'config_path': r'%USERPROFILE%\Saved Games\Respawn\Apex\local\videoconfig.txt',
        'settings': {
            'Competitive (Max FPS)': {
                'setting.cl_gib_allow': '0',
                'setting.cl_particle_fallback_base': '0',
                'setting.cl_particle_fallback_multiplier': '0',
                'setting.cl_ragdoll_maxcount': '0',
                'setting.mat_picmip': '4',
                'setting.particle_cpu_level': '0',
                'setting.r_lod_switch_scale': '0.5',
                'setting.shadow_enable': '0',
                'setting.ssao_enabled': '0',
                'setting.dvs_enable': '0',
            }
        }
    }
}

# Genel grafik ayarları önerileri
GENERAL_RECOMMENDATIONS = {
    'Low-End PC (4GB RAM, Integrated GPU)': {
        'resolution': '1280x720 veya 1600x900',
        'texture_quality': 'Low',
        'shadow_quality': 'Off/Low',
        'effects': 'Low',
        'anti_aliasing': 'Off/FXAA',
        'vsync': 'Off',
        'motion_blur': 'Off',
        'ambient_occlusion': 'Off',
        'expected_fps': '60-90 FPS'
    },
    'Mid-Range PC (8-16GB RAM, GTX 1660/RX 580)': {
        'resolution': '1920x1080',
        'texture_quality': 'Medium',
        'shadow_quality': 'Low/Medium',
        'effects': 'Medium',
        'anti_aliasing': 'FXAA/TAA',
        'vsync': 'Off',
        'motion_blur': 'Off',
        'ambient_occlusion': 'Low',
        'expected_fps': '100-144 FPS'
    },
    'High-End PC (16GB+ RAM, RTX 3060+/RX 6700+)': {
        'resolution': '1920x1080 veya 2560x1440',
        'texture_quality': 'High',
        'shadow_quality': 'Medium/High',
        'effects': 'High',
        'anti_aliasing': 'TAA/MSAA 2x',
        'vsync': 'Off (G-Sync/FreeSync kullanın)',
        'motion_blur': 'Personal Preference',
        'ambient_occlusion': 'Medium',
        'expected_fps': '144-240+ FPS'
    }
}

def detect_installed_games():
    """Yüklü oyunları tespit et"""
    installed = []
    
    for game_id, game_data in GAME_CONFIGS.items():
        config_path = os.path.expandvars(game_data['config_path'])
        config_dir = os.path.dirname(config_path)
        
        # Config klasörü varsa oyun yüklü demektir
        if os.path.exists(config_dir):
            installed.append({
                'id': game_id,
                'name': game_data['name'],
                'config_path': config_path,
                'config_exists': os.path.exists(config_path)
            })
    
    return installed

def show_general_recommendations():
    """Genel grafik ayarları önerilerini göster"""
    from features.ui_utils import print_box
    print_box("GENEL GRAFİK AYARLARI ÖNERİLERİ")
    
    for pc_type, settings in GENERAL_RECOMMENDATIONS.items():
        print(Fore.YELLOW + Style.BRIGHT + f"  📊 {pc_type}")
        print(Fore.WHITE + "  " + "─" * 60)
        
        for key, value in settings.items():
            key_display = key.replace('_', ' ').title()
            if key == 'expected_fps':
                print(Fore.GREEN + f"  ✓ {key_display:<25} {value}")
            else:
                print(Fore.CYAN + f"  • {key_display:<25} {value}")
        print()
    
    print(Fore.YELLOW + "  💡 GENEL İPUÇLARI:")
    print(Fore.WHITE + "  " + "─" * 60)
    print(Fore.WHITE + "  • V-Sync her zaman kapalı olmalı (input lag yaratır)")
    print(Fore.WHITE + "  • Motion Blur kapatın (netlik için)")
    print(Fore.WHITE + "  • Shadow Quality düşürün (en çok FPS kazancı)")
    print(Fore.WHITE + "  • Texture Quality yüksek tutabilirsiniz (VRAM yeterliyse)")
    print(Fore.WHITE + "  • Anti-Aliasing: FXAA (hızlı) veya TAA (kaliteli)")
    print(Fore.WHITE + "  • Render Scale: %100 (düşürmeyin, bulanıklaşır)")
    print(Fore.WHITE + "  • FPS limiti: Monitör Hz'in 2 katı (örn: 144Hz → 288 FPS)")

def show_game_specific_settings(game_id):
    """Belirli bir oyun için ayarları göster"""
    game = GAME_CONFIGS[game_id]
    
    from features.ui_utils import print_box
    print_box(f"{game['name'].upper()}")
    
    print(Fore.YELLOW + f"  📁 Config Dosyası:")
    print(Fore.WHITE + f"     {game['config_path']}\n")
    
    for profile_name, settings in game['settings'].items():
        print(Fore.GREEN + Style.BRIGHT + f"  ⚙️  {profile_name}")
        print(Fore.WHITE + "  " + "─" * 60)
        
        for key, value in settings.items():
            print(Fore.CYAN + f"  {key:<35} = {value}")
        print()

def apply_game_config(game_id, profile_name):
    """Oyun config dosyasını uygula"""
    game = GAME_CONFIGS[game_id]
    config_path = os.path.expandvars(game['config_path'])
    
    print(Fore.YELLOW + f"\n  ⚡ {game['name']} config uygulanıyor...\n")
    
    # Config klasörünü oluştur
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    # Yedek al
    if os.path.exists(config_path):
        backup_path = config_path + '.backup'
        try:
            import shutil
            shutil.copy2(config_path, backup_path)
            print(Fore.GREEN + f"  ✓ Yedek oluşturuldu: {backup_path}")
        except Exception as e:
            print(Fore.YELLOW + "  ⚠️  Yedek oluşturulamadı")
    
    # Config dosyasını yaz
    try:
        settings = game['settings'][profile_name]
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(f"// AeroFPS PRO - {game['name']} Config\n")
            f.write(f"// Profile: {profile_name}\n")
            f.write(f"// Generated by AeroFPS PRO\n\n")
            
            for key, value in settings.items():
                if game_id == 'CS2' or game.get('name') == 'CS2':
                    f.write(f'{key} "{value}"\n')
                else:
                    f.write(f'{key}={value}\n')
        
        print(Fore.GREEN + f"\n  ✅ Config başarıyla uygulandı!")
        print(Fore.CYAN + f"  📝 Dosya: {config_path}")
        log_success(f"{game['name']} config uygulandı: {profile_name}")
        
        return True
    except Exception as e:
        print(Fore.RED + f"\n  ❌ Hata: {e}")
        log_warning(f"{game['name']} config hatası: {e}")
        return False

def game_config_menu():
    """Oyun config optimizer menüsü"""

    while True:
        from features.ui_utils import print_box
        print_box("OYUN İÇİ AYAR ÖNERİLERİ")
        
        print(Fore.WHITE + "\n  [1] 📊 Genel Grafik Ayarları Önerileri")
        print(Fore.WHITE + "  [2] 🎮 Yüklü Oyunları Tespit Et")
        print(Fore.WHITE + "  [3] ⚙️  Oyun Config Dosyası Oluştur")
        print(Fore.WHITE + "  [4] ⬅️  Geri Dön\n")
        
        choice = input(Fore.GREEN + "  Seçim (1-4): ")
        
        if choice == '1':
            show_general_recommendations()
        
        elif choice == '2':
            print(Fore.YELLOW + "\n  🔍 Yüklü oyunlar taranıyor...\n")
            installed = detect_installed_games()
            
            if installed:
                print(Fore.GREEN + f"  ✅ {len(installed)} oyun tespit edildi:\n")
                for game in installed:
                    status = "✓ Config var" if game['config_exists'] else "✗ Config yok"
                    color = Fore.GREEN if game['config_exists'] else Fore.YELLOW
                    print(color + f"  • {game['name']:<25} {status}")
                    print(Fore.WHITE + f"    {game['config_path']}\n")
            else:
                print(Fore.YELLOW + "  ⚠️  Desteklenen oyun bulunamadı")
                print(Fore.CYAN + "\n  💡 Desteklenen Oyunlar:")
                for game_id, game_data in GAME_CONFIGS.items():
                    print(Fore.WHITE + f"     • {game_data['name']}")
        
        elif choice == '3':
            installed = detect_installed_games()
            
            if not installed:
                print(Fore.RED + "\n  ❌ Yüklü oyun bulunamadı!")
                continue
            
            print(Fore.CYAN + "\n  🎮 Oyun Seçin:")
            for i, game in enumerate(installed, 1):
                print(Fore.WHITE + f"  [{i}] {game['name']}")
            
            game_choice = input(Fore.GREEN + f"\n  Oyun (1-{len(installed)}): ")
            
            try:
                game_idx = int(game_choice) - 1
                selected_game = installed[game_idx]
                game_id = selected_game['id']
                
                # Profil seçimi
                profiles = list(GAME_CONFIGS[game_id]['settings'].keys())
                print(Fore.CYAN + "\n  ⚙️  Profil Seçin:")
                for i, profile in enumerate(profiles, 1):
                    print(Fore.WHITE + f"  [{i}] {profile}")
                
                profile_choice = input(Fore.GREEN + f"\n  Profil (1-{len(profiles)}): ")
                profile_idx = int(profile_choice) - 1
                selected_profile = profiles[profile_idx]
                
                # Önizleme
                show_game_specific_settings(game_id)
                
                confirm = input(Fore.YELLOW + "\n  Bu ayarları uygulamak istiyor musunuz? (E/H): ").strip().upper()
                
                if confirm == 'E':
                    apply_game_config(game_id, selected_profile)
            except (ValueError, IndexError):
                print(Fore.RED + "\n  ❌ Geçersiz seçim!")
        
        elif choice == '4':
            break
        
        input(Fore.CYAN + "\n  Devam etmek için ENTER'a basın...")

if __name__ == "__main__":
    game_config_menu()
