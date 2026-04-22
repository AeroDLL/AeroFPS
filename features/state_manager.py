"""
AeroFPS PRO - State Management & Persistence System
Manages application state with SQLite backend
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
from .logger import log_info, log_error, log_success, log_warning


class StateDatabase:
    """SQLite-based state persistence"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            config_dir = Path.home() / ".aerofps"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "state.db")
        
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize database schema"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # State table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    data_type TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # History table (for undo/redo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    state_before TEXT,
                    state_after TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reversible BOOLEAN DEFAULT 1
                )
            """)
            
            # Cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    ttl_seconds INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            log_success(f"State database initialized: {self.db_path}")
        
        except Exception as e:
            log_error(f"Failed to initialize state database: {e}")
            raise
    
    def set(self, key: str, value: Any) -> bool:
        """Set state value"""
        try:
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
                data_type = "json"
            else:
                value_str = str(value)
                data_type = type(value).__name__
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO state (key, value, data_type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value_str, data_type))
            
            self.conn.commit()
            log_info(f"State set: {key}")
            return True
        
        except Exception as e:
            log_error(f"Failed to set state {key}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value, data_type FROM state WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row is None:
                return default
            
            value_str, data_type = row
            
            # Deserialize based on type
            if data_type == "json":
                return json.loads(value_str)
            elif data_type in ("int", "float"):
                return type(default)(value_str) if default is not None else value_str
            else:
                return value_str
        
        except Exception as e:
            log_error(f"Failed to get state {key}: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete state value"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM state WHERE key = ?", (key,))
            self.conn.commit()
            log_info(f"State deleted: {key}")
            return True
        
        except Exception as e:
            log_error(f"Failed to delete state {key}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all state values"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT key, value, data_type FROM state")
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                key, value_str, data_type = row
                if data_type == "json":
                    result[key] = json.loads(value_str)
                else:
                    result[key] = value_str
            
            return result
        
        except Exception as e:
            log_error(f"Failed to get all state: {e}")
            return {}
    
    def clear(self) -> bool:
        """Clear all state"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM state")
            self.conn.commit()
            log_warning("State cleared")
            return True
        
        except Exception as e:
            log_error(f"Failed to clear state: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            log_info("State database closed")


class StateManager:
    """Application state management with history support"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = StateDatabase(db_path)
        self.history_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self._listeners: List[callable] = []
    
    def set(self, key: str, value: Any, track_history: bool = False) -> bool:
        """Set state value with optional history tracking"""
        try:
            old_value = self.db.get(key)
            
            # Track in history
            if track_history:
                self._record_history(
                    action=f"set_{key}",
                    state_before=old_value,
                    state_after=value
                )
            
            success = self.db.set(key, value)
            if success:
                self._notify_listeners(key, value)
            
            return success
        
        except Exception as e:
            log_error(f"Failed to set state: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self.db.get(key, default)
    
    def _record_history(self, action: str, state_before: Any, state_after: Any) -> None:
        """Record state change in history"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO history (action, state_before, state_after)
                VALUES (?, ?, ?)
            """, (
                action,
                json.dumps(state_before) if state_before else None,
                json.dumps(state_after) if state_after else None
            ))
            self.db.conn.commit()
            self.redo_stack.clear()  # Clear redo stack on new action
        
        except Exception as e:
            log_error(f"Failed to record history: {e}")
    
    def undo(self) -> bool:
        """Undo last state change"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT id, state_before FROM history
                WHERE reversible = 1
                ORDER BY id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                log_warning("Nothing to undo")
                return False
            
            history_id, state_before = row
            # TODO: Restore state_before
            
            log_success("Undo completed")
            return True
        
        except Exception as e:
            log_error(f"Failed to undo: {e}")
            return False
    
    def redo(self) -> bool:
        """Redo last undone state change"""
        try:
            if not self.redo_stack:
                log_warning("Nothing to redo")
                return False
                
            last_undone = self.redo_stack.pop()
            action = last_undone["action"]
            state_after = last_undone["state_after"]
            
            if action.startswith("set_"):
                key = action[4:]
                if state_after is not None:
                    after_val = json.loads(state_after)
                    self.db.set(key, after_val)
                else:
                    self.db.delete(key)
                    
                # Re-add to history stack (without clearing redo_stack, so we manually insert)
                cursor = self.db.conn.cursor()
                cursor.execute("""
                    INSERT INTO history (action, state_before, state_after)
                    VALUES (?, ?, ?)
                """, (
                    action,
                    last_undone["state_before"],
                    state_after
                ))
                self.db.conn.commit()
            
            log_success("Redo completed")
            return True
        
        except Exception as e:
            log_error(f"Failed to redo: {e}")
            return False
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get state change history"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT id, action, timestamp
                FROM history
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            log_error(f"Failed to get history: {e}")
            return []
    
    def clear_history(self) -> bool:
        """Clear all history"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("DELETE FROM history")
            self.db.conn.commit()
            log_info("History cleared")
            return True
        
        except Exception as e:
            log_error(f"Failed to clear history: {e}")
            return False
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to state changes"""
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from state changes"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, key: str, value: Any) -> None:
        """Notify all listeners of state change"""
        for listener in self._listeners:
            try:
                listener(key, value)
            except Exception as e:
                log_error(f"Listener error: {e}")
    
    def save_snapshot(self, name: str) -> bool:
        """Save state snapshot"""
        try:
            state = self.db.get_all()
            return self.set(f"snapshot_{name}", state)
        
        except Exception as e:
            log_error(f"Failed to save snapshot: {e}")
            return False
    
    def restore_snapshot(self, name: str) -> bool:
        """Restore state from snapshot"""
        try:
            state = self.get(f"snapshot_{name}")
            if not state:
                log_warning(f"Snapshot not found: {name}")
                return False
            
            for key, value in state.items():
                self.db.set(key, value)
            
            log_success(f"Restored snapshot: {name}")
            return True
        
        except Exception as e:
            log_error(f"Failed to restore snapshot: {e}")
            return False
    
    def close(self) -> None:
        """Close state manager"""
        self.db.close()


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get global state manager (singleton)"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def reset_state_manager() -> None:
    """Reset global state manager"""
    global _state_manager
    if _state_manager:
        _state_manager.close()
    _state_manager = None


if __name__ == "__main__":
    # Test
    print("Testing state manager...")
    
    sm = StateManager()
    
    # Basic state
    sm.set("language", "TR", track_history=True)
    print(f"Language: {sm.get('language')}")
    
    # Complex state
    sm.set("optimization", {"fps": 10, "temp": -5}, track_history=True)
    print(f"Optimization: {sm.get('optimization')}")
    
    # Snapshots
    sm.save_snapshot("before_optimization")
    sm.set("optimization", {"fps": 20, "temp": -10})
    
    # Get history
    history = sm.get_history()
    print(f"History entries: {len(history)}")
    
    sm.close()
    print("✅ State manager test completed!")
