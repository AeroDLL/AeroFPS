"""
AeroFPS PRO - Safe Command Runner Module
Enhanced error handling, logging, and rollback support
"""

import subprocess
import shlex
import time
from contextlib import contextmanager
from typing import Callable, Optional, Dict, Any
from .logger import log_info, log_error, log_warning, log_success


class OptimizationError(Exception):
    """Base optimization error"""
    pass


class RollbackError(OptimizationError):
    """Rollback operation failed"""
    pass


@contextmanager
def safe_operation(
    name: str,
    rollback_fn: Optional[Callable] = None,
    timeout: int = 30
):
    """
    Context manager for safe operations with rollback support
    
    Usage:
        with safe_operation("My Operation", rollback_fn=cleanup):
            # do something
    """
    try:
        log_info(f"Starting: {name}")
        yield
        log_success(f"Completed: {name}")
    except subprocess.TimeoutExpired:
        log_warning(f"Timeout ({timeout}s): {name}")
        if rollback_fn:
            try:
                rollback_fn()
                log_info(f"Rolled back: {name}")
            except Exception as e:
                log_error(f"Rollback failed for {name}: {e}")
                raise RollbackError(f"Could not rollback {name}: {e}")
        raise OptimizationError(f"{name} timed out after {timeout}s")
    except Exception as e:
        log_error(f"Error in {name}: {e}")
        if rollback_fn:
            try:
                rollback_fn()
                log_info(f"Rolled back: {name}")
            except Exception as rb_err:
                log_error(f"Rollback failed for {name}: {rb_err}")
                raise RollbackError(f"Could not rollback {name}: {rb_err}")
        raise OptimizationError(f"{name} failed: {e}")


def validate_command_arg(arg: str, pattern: str = None) -> str:
    """Validate command argument to prevent injection"""
    if not isinstance(arg, str):
        raise ValueError(f"Command argument must be string, got {type(arg)}")
    
    if len(arg) > 1000:
        raise ValueError(f"Command argument too long: {len(arg)} > 1000")
    
    return arg.strip()


def run_command(
    cmd: list,
    name: str = "Command",
    timeout: int = 30,
    capture_output: bool = False,
    rollback_fn: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Safely run a command with error handling and logging
    
    Args:
        cmd: List form of command (safe, no shell=True)
        name: Operation name for logging
        timeout: Timeout in seconds
        capture_output: Capture stdout/stderr
        rollback_fn: Function to call on failure
    
    Returns:
        {
            'success': bool,
            'returncode': int,
            'stdout': str,
            'stderr': str,
            'message': str
        }
    """
    try:
        with safe_operation(name, rollback_fn=rollback_fn, timeout=timeout):
            log_info(f"Executing: {' '.join(cmd[:2])}")
            
            result = subprocess.run(
                cmd,
                shell=False,  # SAFE - no shell injection
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                log_warning(f"{name} returned {result.returncode}: {error_msg}")
                return {
                    'success': False,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'message': f"{name} failed with code {result.returncode}"
                }
            
            return {
                'success': True,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': f"{name} completed successfully"
            }
    
    except subprocess.TimeoutExpired:
        log_error(f"{name} timeout after {timeout}s")
        if rollback_fn:
            try:
                rollback_fn()
            except Exception as e:
                pass
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Timeout after {timeout}s',
            'message': f"{name} timed out"
        }
    
    except Exception as e:
        log_error(f"{name} exception: {e}")
        if rollback_fn:
            try:
                rollback_fn()
            except Exception as e:
                pass
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'message': f"{name} failed: {e}"
        }


def run_silent(cmd: str, name: str = "Operation", timeout: int = 30) -> bool:
    """
    Legacy compatible function - runs command silently
    Returns True if successful, False otherwise
    
    Args:
        cmd: Command string
        name: Operation name
        timeout: Timeout in seconds
    
    Returns:
        bool: Success status
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout
        )
        success = result.returncode == 0
        if success:
            log_success(f"{name} executed")
        else:
            log_warning(f"{name} returned code {result.returncode}")
        return success
    
    except subprocess.TimeoutExpired:
        log_warning(f"{name} timed out after {timeout}s")
        return False
    
    except Exception as e:
        log_error(f"{name} failed: {e}")
        return False


def run_with_retry(
    cmd: list,
    name: str = "Command",
    max_retries: int = 3,
    timeout: int = 30,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    Run command with automatic retry logic
    
    Args:
        cmd: List form of command
        name: Operation name
        max_retries: Maximum retry attempts
        timeout: Timeout per attempt
        delay: Delay between retries (seconds)
    
    Returns:
        Result dictionary (success/failure)
    """
    for attempt in range(max_retries):
        log_info(f"{name} - Attempt {attempt + 1}/{max_retries}")
        
        result = run_command(cmd, name=name, timeout=timeout)
        
        if result['success']:
            return result
        
        if attempt < max_retries - 1:
            log_warning(f"Retrying {name} after {delay}s...")
            time.sleep(delay)
    
    log_error(f"{name} failed after {max_retries} attempts")
    return result


# Registry operation wrappers (common patterns)
def run_registry_add(
    path: str,
    name: str,
    value_type: str,
    value: str,
    operation_name: str = "Registry Add"
) -> bool:
    """Safe registry add operation"""
    # Validate inputs
    if not all(isinstance(x, str) for x in [path, name, value_type, value]):
        log_error("Invalid registry operation inputs")
        return False
    
    cmd = [
        'reg', 'add', path,
        '/v', name,
        '/t', value_type,
        '/d', value,
        '/f'
    ]
    
    result = run_command(cmd, name=operation_name)
    return result['success']


def run_registry_delete(
    path: str,
    name: str,
    operation_name: str = "Registry Delete"
) -> bool:
    """Safe registry delete operation"""
    if not all(isinstance(x, str) for x in [path, name]):
        log_error("Invalid registry operation inputs")
        return False
    
    cmd = ['reg', 'delete', path, '/v', name, '/f']
    result = run_command(cmd, name=operation_name)
    return result['success']


# Service operation wrappers
def stop_service(service_name: str) -> bool:
    """Stop Windows service safely"""
    if not service_name or len(service_name) > 256:
        log_error("Invalid service name")
        return False
    
    cmd = ['sc', 'stop', service_name]
    result = run_command(cmd, name=f"Stop Service: {service_name}", timeout=15)
    return result['success']


def disable_service(service_name: str) -> bool:
    """Disable Windows service safely"""
    if not service_name or len(service_name) > 256:
        log_error("Invalid service name")
        return False
    
    cmd = ['sc', 'config', service_name, 'start=', 'disabled']
    result = run_command(cmd, name=f"Disable Service: {service_name}")
    return result['success']


def clean_all_ram():
    try:
        import ctypes, psutil
        psapi = ctypes.WinDLL('psapi.dll')
        kernel = ctypes.WinDLL('kernel32.dll')
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        for proc in psutil.process_iter(['pid']):
            try:
                handle = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, proc.info['pid'])
                if handle:
                    psapi.EmptyWorkingSet(handle)
                    kernel.CloseHandle(handle)
            except Exception:
                pass
    except Exception: pass


if __name__ == "__main__":
    # Test safe_runner
    print("Testing safe_runner module...")
    
    result = run_command(['cmd', '/c', 'echo', 'Hello World'], name="Echo Test")
    print(f"Result: {result}")
    
    # Test retry
    result = run_with_retry(
        ['ping', 'localhost'],
        name="Ping Test",
        max_retries=2
    )
    print(f"Retry Result: {result}")
