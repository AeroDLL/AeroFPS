"""
AeroFPS PRO - Module Abstraction Layer
Base classes and interfaces for all optimization modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from .logger import log_info, log_error, log_success, log_warning


class OperationStatus(Enum):
    """Operation status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Standard operation result format"""
    status: OperationStatus
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'status': self.status.value,
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'duration': self.duration
        }


class BaseModule(ABC):
    """Base class for all AeroFPS modules"""
    
    def __init__(self, name: str, config=None, logger=None):
        self.name = name
        self.config = config
        self.logger = logger or log_info
        self.status = OperationStatus.IDLE
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize module"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown module"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if module is initialized"""
        return self._initialized
    
    def log(self, level: str, message: str):
        """Unified logging"""
        full_message = f"[{self.name}] {message}"
        if level == "info":
            log_info(full_message)
        elif level == "warning":
            log_warning(full_message)
        elif level == "error":
            log_error(full_message)
        elif level == "success":
            log_success(full_message)


class Optimizer(BaseModule):
    """Base class for optimization modules"""
    
    def __init__(self, name: str, config=None, logger=None):
        super().__init__(name, config, logger)
        self.rollback_fn: Optional[Callable] = None
    
    @abstractmethod
    def optimize(self) -> OperationResult:
        """Execute optimization"""
        pass
    
    @abstractmethod
    def can_optimize(self) -> bool:
        """Check if optimization can be applied"""
        pass
    
    @abstractmethod
    def get_impact(self) -> Dict[str, Any]:
        """Get estimated impact of optimization
        
        Returns:
            {
                'fps_gain': estimated FPS improvement,
                'temp_reduction': estimated temp drop,
                'performance': 'high'|'medium'|'low',
                'risky': boolean,
                'rollback_support': boolean
            }
        """
        pass
    
    def set_rollback(self, rollback_fn: Callable) -> None:
        """Set rollback function"""
        self.rollback_fn = rollback_fn


class Monitor(BaseModule):
    """Base class for monitoring modules"""
    
    def __init__(self, name: str, config=None, logger=None):
        super().__init__(name, config, logger)
        self._metrics = {}
        self._listeners: list[Callable] = []
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """Start monitoring"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Stop monitoring"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        pass
    
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to metrics updates"""
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from metrics updates"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, metrics: Dict[str, Any]) -> None:
        """Notify all listeners of metric updates"""
        for listener in self._listeners:
            try:
                listener(metrics)
            except Exception as e:
                self.log("error", f"Listener error: {e}")


class Manager(BaseModule):
    """Base class for management modules"""
    
    def __init__(self, name: str, config=None, logger=None):
        super().__init__(name, config, logger)
        self._state: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, action: str, **kwargs) -> OperationResult:
        """Execute management action"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        pass
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value"""
        self._state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self._state.get(key, default)


class Analyzer(BaseModule):
    """Base class for analysis modules"""
    
    def __init__(self, name: str, config=None, logger=None):
        super().__init__(name, config, logger)
        self._analysis_cache: Dict[str, Any] = {}
    
    @abstractmethod
    def analyze(self) -> OperationResult:
        """Perform analysis"""
        pass
    
    @abstractmethod
    def get_recommendations(self) -> list[Dict[str, Any]]:
        """Get recommendations based on analysis"""
        pass
    
    def cache_analysis(self, key: str, value: Any) -> None:
        """Cache analysis result"""
        self._analysis_cache[key] = value
    
    def get_cached_analysis(self, key: str) -> Optional[Any]:
        """Get cached analysis"""
        return self._analysis_cache.get(key)


class Pipeline:
    """Module pipeline for sequential operations"""
    
    def __init__(self, name: str, logger=None):
        self.name = name
        self.logger = logger or log_info
        self.modules: list[BaseModule] = []
        self.results: list[OperationResult] = []
    
    def add_module(self, module: BaseModule) -> "Pipeline":
        """Add module to pipeline"""
        if not module.is_initialized():
            if module.initialize():
                self.modules.append(module)
                self.log("success", f"Added {module.name}")
            else:
                self.log("error", f"Failed to initialize {module.name}")
        else:
            self.modules.append(module)
        return self
    
    def execute(self) -> list[OperationResult]:
        """Execute all modules in pipeline"""
        self.results.clear()
        
        for module in self.modules:
            if isinstance(module, Optimizer):
                result = module.optimize()
            elif isinstance(module, Manager):
                result = module.execute("auto")
            elif isinstance(module, Analyzer):
                result = module.analyze()
            else:
                result = OperationResult(
                    status=OperationStatus.IDLE,
                    success=False,
                    message="Unknown module type"
                )
            
            self.results.append(result)
            
            if not result.success:
                self.log("warning", f"{module.name} failed: {result.message}")
        
        return self.results
    
    def rollback(self) -> bool:
        """Rollback all operations"""
        success = True
        for module, result in reversed(list(zip(self.modules, self.results))):
            if result.success:
                if isinstance(module, Optimizer) and module.rollback_fn:
                    try:
                        module.rollback_fn()
                        self.log("info", f"Rollback successful for {module.name}")
                    except Exception as e:
                        self.log("error", f"Rollback failed for {module.name}: {e}")
                        success = False
                elif hasattr(module, "undo") and callable(getattr(module, "undo")):
                    try:
                        module.undo()
                        self.log("info", f"Undo successful for {module.name}")
                    except Exception as e:
                        self.log("error", f"Undo failed for {module.name}: {e}")
                        success = False
                elif hasattr(module, "revert") and callable(getattr(module, "revert")):
                    try:
                        module.revert()
                        self.log("info", f"Revert successful for {module.name}")
                    except Exception as e:
                        self.log("error", f"Revert failed for {module.name}: {e}")
                        success = False
        return success
    
    def log(self, level: str, message: str) -> None:
        """Pipeline logging"""
        full_message = f"[Pipeline: {self.name}] {message}"
        if level == "info":
            log_info(full_message)
        elif level == "warning":
            log_warning(full_message)
        elif level == "error":
            log_error(full_message)
        elif level == "success":
            log_success(full_message)


class ModuleRegistry:
    """Registry for managing all modules"""
    
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
    
    def register(self, module: BaseModule) -> None:
        """Register module"""
        self._modules[module.name] = module
        log_success(f"Registered module: {module.name}")
    
    def unregister(self, name: str) -> None:
        """Unregister module"""
        if name in self._modules:
            del self._modules[name]
            log_info(f"Unregistered module: {name}")
    
    def get(self, name: str) -> Optional[BaseModule]:
        """Get module by name"""
        return self._modules.get(name)
    
    def get_all(self) -> Dict[str, BaseModule]:
        """Get all modules"""
        return self._modules.copy()
    
    def get_by_type(self, module_type: type) -> list[BaseModule]:
        """Get modules by type"""
        return [m for m in self._modules.values() if isinstance(m, module_type)]


# Global module registry
_registry = ModuleRegistry()


def get_registry() -> ModuleRegistry:
    """Get global module registry"""
    return _registry


if __name__ == "__main__":
    # Test
    print("Testing module abstraction layer...")
    
    class TestOptimizer(Optimizer):
        def initialize(self) -> bool:
            self._initialized = True
            return True
        
        def shutdown(self) -> bool:
            self._initialized = False
            return True
        
        def optimize(self) -> OperationResult:
            return OperationResult(
                status=OperationStatus.SUCCESS,
                success=True,
                message="Test optimization completed"
            )
        
        def can_optimize(self) -> bool:
            return True
        
        def get_impact(self) -> Dict[str, Any]:
            return {
                'fps_gain': 10,
                'performance': 'high',
                'risky': False
            }
    
    opt = TestOptimizer("TestOptimizer")
    opt.initialize()
    result = opt.optimize()
    print(f"Result: {result.to_dict()}")
    print("✅ Module abstraction layer test completed!")
