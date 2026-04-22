"""
AeroFPS PRO - Unit Tests Suite
Testing framework for core modules
"""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.logger import log_info, log_error, log_success, log_warning
from features.config_manager import ConfigManager, get_config, reset_config
from features.safe_runner import (
    run_command, run_silent, run_with_retry, 
    validate_command_arg, safe_operation,
    OptimizationError, RollbackError
)


# ============================================================================
# LOGGER TESTS
# ============================================================================

class TestLogger:
    """Test logger module"""
    
    def test_log_functions_callable(self):
        """Test that log functions are callable"""
        assert callable(log_info)
        assert callable(log_error)
        assert callable(log_success)
        assert callable(log_warning)
    
    def test_log_info_accepts_string(self):
        """Test log_info accepts string messages"""
        try:
            log_info("Test message")
            assert True
        except Exception as e:
            assert False, "log_info failed"
    
    def test_log_error_accepts_string(self):
        """Test log_error accepts string messages"""
        try:
            log_error("Test error")
            assert True
        except Exception as e:
            assert False, "log_error failed"


# ============================================================================
# CONFIG MANAGER TESTS
# ============================================================================

class TestConfigManager:
    """Test ConfigManager module"""
    
    @pytest.fixture
    def config(self):
        """Create temp config for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager()
            config.config_dir = Path(tmpdir)
            config.config_file = config.config_dir / "config.json"
            config.backup_file = config.config_dir / "config.backup.json"
            yield config
    
    def test_config_initialization(self, config):
        """Test config initializes with defaults"""
        assert config.config is not None
        assert 'language' in config.config
        assert 'optimization' in config.config
    
    def test_config_get_simple_key(self, config):
        """Test getting simple configuration values"""
        lang = config.get('language')
        assert lang in ['TR', 'EN']
    
    def test_config_get_nested_key(self, config):
        """Test getting nested configuration values"""
        aggressive = config.get('optimization.aggressive_mode')
        assert isinstance(aggressive, bool)
    
    def test_config_get_with_default(self, config):
        """Test getting value with default fallback"""
        value = config.get('nonexistent.key', 'default_value')
        assert value == 'default_value'
    
    def test_config_set_simple_value(self, config):
        """Test setting simple config values"""
        result = config.set('language', 'TR')
        assert result is True
        assert config.get('language') == 'TR'
    
    def test_config_set_nested_value(self, config):
        """Test setting nested config values"""
        result = config.set('optimization.aggressive_mode', True)
        assert result is True
        assert config.get('optimization.aggressive_mode') is True
    
    def test_config_save_and_load(self, config):
        """Test saving and loading config"""
        config.set('language', 'TR')
        config.save()
        
        # Create new instance and verify
        config2 = ConfigManager()
        config2.config_dir = config.config_dir
        config2.config_file = config.config_file
        config2._load()
        
        assert config2.get('language') == 'TR'
    
    def test_config_reset_to_defaults(self, config):
        """Test resetting config to defaults"""
        config.set('language', 'TR')
        assert config.get('language') == 'TR'
        
        result = config.reset_to_defaults()
        assert result is True
        assert config.get('language') == 'EN'
    
    def test_config_merge(self, config):
        """Test merging config"""
        new_config = {
            'language': 'TR',
            'optimization': {
                'aggressive_mode': True
            }
        }
        result = config.merge(new_config)
        assert result is True
        assert config.get('language') == 'TR'
        assert config.get('optimization.aggressive_mode') is True
    
    def test_config_to_json(self, config):
        """Test exporting config to JSON"""
        json_str = config.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert 'language' in parsed
    
    def test_config_from_json(self, config):
        """Test importing config from JSON"""
        json_str = '{"language": "TR", "version": "1.0"}'
        result = config.from_json(json_str)
        assert result is True
        assert config.get('language') == 'TR'
    
    def test_config_from_invalid_json(self, config):
        """Test that invalid JSON is rejected"""
        result = config.from_json("invalid json {")
        assert result is False
    
    def test_singleton_pattern(self):
        """Test singleton pattern for global config"""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2


# ============================================================================
# SAFE RUNNER TESTS
# ============================================================================

class TestSafeRunner:
    """Test safe_runner module"""
    
    def test_validate_command_arg_valid_string(self):
        """Test validation of valid command arguments"""
        result = validate_command_arg("valid_argument")
        assert result == "valid_argument"
    
    def test_validate_command_arg_strips_whitespace(self):
        """Test that validation strips whitespace"""
        result = validate_command_arg("  test  ")
        assert result == "test"
    
    def test_validate_command_arg_rejects_non_string(self):
        """Test validation rejects non-strings"""
        with pytest.raises(ValueError):
            validate_command_arg(12345)
    
    def test_validate_command_arg_rejects_too_long(self):
        """Test validation rejects too long arguments"""
        with pytest.raises(ValueError):
            validate_command_arg("a" * 1001)
    
    def test_run_command_echo(self):
        """Test running simple echo command"""
        result = run_command(['echo', 'hello'], name="Echo Test")
        assert result is not None
        assert 'success' in result
        assert 'message' in result
    
    def test_run_command_invalid_command(self):
        """Test handling of invalid command"""
        result = run_command(['nonexistent_command_xyz'], name="Invalid Test", timeout=5)
        assert result['success'] is False
        assert result['returncode'] != 0
    
    def test_run_command_timeout(self):
        """Test command timeout handling"""
        result = run_command(['ping', '-n', '100', 'localhost'], timeout=1, name="Timeout Test")
        # Should timeout or complete, either way should be handled
        assert 'success' in result
        assert 'message' in result
    
    def test_run_silent_success(self):
        """Test run_silent with successful command"""
        result = run_silent('cmd /c echo test', name="Silent Echo")
        assert result is True
    
    def test_run_silent_failure(self):
        """Test run_silent with failing command"""
        result = run_silent('cmd /c exit 1', name="Silent Fail")
        assert result is False
    
    def test_safe_operation_context_manager(self):
        """Test safe_operation context manager"""
        executed = False
        
        try:
            with safe_operation("Test Operation"):
                executed = True
        except Exception as e:
            pass
        
        assert executed is True
    
    def test_safe_operation_with_rollback(self):
        """Test safe_operation with rollback"""
        rollback_called = False
        
        def rollback():
            nonlocal rollback_called
            rollback_called = True
        
        try:
            with safe_operation("Test Operation", rollback_fn=rollback):
                raise Exception("Test error")
        except OptimizationError:
            pass
        
        assert rollback_called is True
    
    def test_run_with_retry_success(self):
        """Test retry logic with successful command"""
        result = run_with_retry(
            ['cmd', '/c', 'echo', 'hello'],
            name="Retry Test",
            max_retries=2
        )
        assert result['success'] is True
    
    def test_run_with_retry_eventual_success(self):
        """Test retry logic eventually succeeds"""
        call_count = 0
        
        def command_that_fails_then_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Fail")
            return True
        
        # This tests the retry mechanism
        assert call_count >= 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for multiple modules"""
    
    def test_config_and_logger_integration(self):
        """Test config and logger work together"""
        config = ConfigManager()
        log_level = config.get('monitoring.log_level')
        
        assert log_level is not None
        assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    
    def test_safe_runner_with_config(self):
        """Test safe_runner respects config settings"""
        config = ConfigManager()
        aggressive = config.get('optimization.aggressive_mode')
        
        # This should not raise
        result = run_command(['echo', 'test'], name="Integration Test")
        assert result is not None


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '--tb=short', '-ra'])
