"""
AeroFPS PRO - Process Manager (Refactored)
Uses new abstraction layer for better architecture
"""

import psutil
from typing import Dict, Any, List
from .abstraction import Manager, OperationResult, OperationStatus
from .config_manager import get_config
from .logger import log_info, log_success, log_error
from .safe_runner import run_command


class ProcessManager(Manager):
    """
    Manages game processes and background applications
    Inherits from Manager base class
    """
    
    def __init__(self, config=None):
        super().__init__(name="ProcessManager", config=config)
        self.config = config or get_config()
        
        # Get from config
        self.popular_games = self.config.get('games.managed_games', [
            "cs2.exe", "valorant.exe",
            "fortniteclient-win64-shipping.exe", "apexlegends.exe",
            "leagueclient.exe", "dota2.exe", "overwatch.exe",
            "pubg.exe", "tslgame.exe", "rainbow6.exe",
            "modernwarfare.exe", "gta5.exe", "minecraft.exe"
        ])
        
        self.background_apps = [
            "discord.exe", "spotify.exe", "chrome.exe", "msedge.exe",
            "steam.exe", "epicgameslauncher.exe", "origin.exe",
            "skype.exe", "teams.exe", "onedrive.exe"
        ]
    
    def initialize(self) -> bool:
        """Initialize process manager"""
        try:
            self.log("info", "Initializing ProcessManager")
            self._initialized = True
            return True
        except Exception as e:
            self.log("error", f"Initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown process manager"""
        try:
            self.log("info", "Shutting down ProcessManager")
            self._initialized = False
            return True
        except Exception as e:
            self.log("error", f"Shutdown failed: {e}")
            return False
    
    def execute(self, action: str = "optimize", **kwargs) -> OperationResult:
        """Execute process management action"""
        try:
            if action == "optimize":
                return self.optimize_processes()
            elif action == "boost_games":
                return self.boost_game_priority()
            elif action == "kill_background":
                return self.kill_background_apps()
            elif action == "get_running":
                return self.get_running_games_result()
            else:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    success=False,
                    message=f"Unknown action: {action}"
                )
        
        except Exception as e:
            self.log("error", f"Execute failed: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=str(e),
                error=str(e)
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current process manager status"""
        return {
            'initialized': self._initialized,
            'games_monitored': len(self.popular_games),
            'background_apps': len(self.background_apps),
            'running_games': len(self.get_running_games())
        }
    
    def get_running_games(self) -> List[Dict[str, Any]]:
        """Get list of running games"""
        running_games = []
        _games_set = frozenset(g.lower() for g in self.popular_games)
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name in _games_set:
                        running_games.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.log("error", f"Failed to get running games: {e}")
        
        return running_games
    
    def get_running_games_result(self) -> OperationResult:
        """Get running games as operation result"""
        try:
            games = self.get_running_games()
            return OperationResult(
                status=OperationStatus.SUCCESS,
                success=True,
                message=f"Found {len(games)} running game(s)",
                data={'games': games}
            )
        except Exception as e:
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=str(e),
                error=str(e)
            )
    
    def set_process_priority(self, pid: int, priority: str = "high") -> bool:
        """
        Set process priority (high/normal/low)
        Windows uses: 128 (low), 32 (normal), 64 (high), 256 (realtime)
        """
        try:
            priority_map = {
                "high": "64",
                "normal": "32",
                "low": "128"
            }
            
            priority_value = priority_map.get(priority.lower(), "64")
            
            # Try with psutil first
            try:
                p = psutil.Process(pid)
                if priority.lower() == "high":
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                elif priority.lower() == "low":
                    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else:
                    p.nice(psutil.NORMAL_PRIORITY_CLASS)
                
                self.log("success", f"Set process {pid} priority to {priority}")
                return True
            
            except Exception as e:
                self.log("warning", f"psutil failed: {e}, trying wmic...")
                
                # Fallback to wmic
                result = run_command(
                    ['wmic', 'process', 'where', f'processid={pid}',
                     'CALL', 'setpriority', priority_value],
                    name=f"Set Priority {pid}",
                    timeout=10
                )
                
                return result['success']
        
        except Exception as e:
            self.log("error", f"Failed to set priority: {e}")
            return False
    
    def boost_game_priority(self) -> OperationResult:
        """Boost all running games to high priority"""
        try:
            games = self.get_running_games()
            
            if not games:
                return OperationResult(
                    status=OperationStatus.SUCCESS,
                    success=True,
                    message="No running games to boost",
                    data={'boosted': 0}
                )
            
            boosted = 0
            for game in games:
                if self.set_process_priority(game['pid'], 'high'):
                    boosted += 1
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                success=True,
                message=f"Boosted {boosted}/{len(games)} game(s)",
                data={'boosted': boosted, 'total': len(games)}
            )
        
        except Exception as e:
            self.log("error", f"Boost failed: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=str(e),
                error=str(e)
            )
    
    def kill_background_apps(self) -> OperationResult:
        """Kill unnecessary background applications"""
        try:
            killed = 0
            errors = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name in [a.lower() for a in self.background_apps]:
                        try:
                            proc.terminate()
                            killed += 1
                            self.log("success", f"Killed {proc.info['name']}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                            errors.append(f"{proc.info['name']}: {e}")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                success=True,
                message=f"Killed {killed} background app(s)",
                data={'killed': killed, 'errors': errors}
            )
        
        except Exception as e:
            self.log("error", f"Kill background apps failed: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=str(e),
                error=str(e)
            )
    
    def optimize_processes(self) -> OperationResult:
        """Full process optimization"""
        try:
            results = []
            
            # Boost games
            game_result = self.boost_game_priority()
            results.append(game_result)
            
            # Kill background
            bg_result = self.kill_background_apps()
            results.append(bg_result)
            
            all_success = all(r.success for r in results)
            
            return OperationResult(
                status=OperationStatus.SUCCESS if all_success else OperationStatus.FAILED,
                success=all_success,
                message="Process optimization completed",
                data={'results': [r.to_dict() for r in results]}
            )
        
        except Exception as e:
            self.log("error", f"Process optimization failed: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                success=False,
                message=str(e),
                error=str(e)
            )


if __name__ == "__main__":
    # Test
    print("Testing refactored ProcessManager...")
    
    pm = ProcessManager()
    pm.initialize()
    
    # Get status
    print(f"Status: {pm.get_status()}")
    
    # Get running games
    result = pm.get_running_games_result()
    print(f"Result: {result.to_dict()}")
    
    pm.shutdown()
    print("✅ ProcessManager test completed!")
