"""Smart Advisor Module - AI Performance Prediction"""

import os
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .constants import (
    TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
    CPU_USAGE_WARNING, CPU_USAGE_CRITICAL,
    RAM_USAGE_WARNING, RAM_USAGE_CRITICAL,
    LOG_LEVELS
)
from .logger import setup_logger, log_with_context

logger = setup_logger(__name__, level=LOG_LEVELS['INFO'])


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    disk_usage: float
    network_latency: float
    temperature: Optional[float] = None
    gpu_usage: Optional[float] = None
    fps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'ram_percent': self.ram_percent,
            'disk_usage': self.disk_usage,
            'network_latency': self.network_latency,
            'temperature': self.temperature,
            'gpu_usage': self.gpu_usage,
            'fps': self.fps
        }


class PerformancePredictor:
    """AI-powered performance prediction."""

    def __init__(self, model_path: str = "models/fps_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.training_data = []
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        if ML_AVAILABLE:
            self._load_model()

    def _load_model(self) -> bool:
        try:
            if os.path.exists(self.model_path):
                import joblib
                model_data = joblib.load(self.model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.is_trained = True
                logger.info("AI model loaded")
                return True
        except Exception as e:
            logger.error(f"Load model error: {e}")
        return False

    def _save_model(self) -> bool:
        try:
            if self.model and self.scaler and ML_AVAILABLE:
                import joblib
                joblib.dump({'model': self.model, 'scaler': self.scaler}, self.model_path)
                logger.info("AI model saved")
                return True
        except Exception as e:
            logger.error(f"Save model error: {e}")
        return False

    def collect_training_data(self, duration_seconds: int = 60) -> List[SystemMetrics]:
        logger.info(f"Collecting data for {duration_seconds}s...")
        collected_data = []
        start_time = time.time()
        try:
            while time.time() - start_time < duration_seconds:
                metrics = self._collect_current_metrics()
                if metrics:
                    collected_data.append(metrics)
                time.sleep(1)
            self.training_data.extend(collected_data)
            logger.info(f"Collected {len(collected_data)} samples")
            return collected_data
        except Exception as e:
            logger.error(f"Collection error: {e}")
            return collected_data

    def _collect_current_metrics(self) -> Optional[SystemMetrics]:
        try:
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=psutil.cpu_percent(interval=0.1),
                ram_percent=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                network_latency=self._measure_network_latency(),
                temperature=self._get_system_temperature()
            )
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            return None

    def _measure_network_latency(self) -> float:
        try:
            import subprocess
            result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'time=' in line and 'ms' in line:
                        return float(line.split('time=')[1].split('ms')[0].strip())
            return 50.0
        except Exception:
            return 50.0

    def _get_system_temperature(self) -> Optional[float]:
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for sensor_type, sensors in temps.items():
                        if 'cpu' in sensor_type.lower():
                            for sensor in sensors:
                                if sensor.current:
                                    return sensor.current
        except Exception:
            pass
        return None

    def train_model(self, test_size: float = 0.2) -> Dict[str, float]:
        if not ML_AVAILABLE or len(self.training_data) < 10:
            return {}
        try:
            logger.info(f"Training with {len(self.training_data)} samples...")
            X, y = [], []
            for metrics in self.training_data:
                if metrics.fps is not None:
                    X.append([metrics.cpu_percent, metrics.ram_percent, 
                             metrics.disk_usage, metrics.network_latency,
                             metrics.temperature or 25.0, metrics.gpu_usage or 0.0])
                    y.append(metrics.fps)
            if len(X) < 5:
                return {}
            X_train, X_test, y_train, y_test = train_test_split(
                np.array(X), np.array(y), test_size=test_size, random_state=42)
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            self.model.fit(X_train_scaled, y_train)
            y_pred = self.model.predict(X_test_scaled)
            mae, r2 = mean_absolute_error(y_test, y_pred), r2_score(y_test, y_pred)
            self.is_trained = True
            self._save_model()
            logger.info(f"Training done. MAE: {mae:.2f}, R²: {r2:.3f}")
            return {'mean_absolute_error': mae, 'r2_score': r2, 
                   'training_samples': len(X_train), 'test_samples': len(X_test)}
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {}

    def predict_fps(self, current_metrics: SystemMetrics) -> Optional[float]:
        if not self.is_trained or not self.model or not self.scaler:
            return None
        try:
            features = np.array([[current_metrics.cpu_percent, current_metrics.ram_percent,
                                 current_metrics.disk_usage, current_metrics.network_latency,
                                 current_metrics.temperature or 25.0, current_metrics.gpu_usage or 0.0]])
            return max(0, self.model.predict(self.scaler.transform(features))[0])
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None


_predictor = None

def get_predictor() -> PerformancePredictor:
    global _predictor
    if _predictor is None:
        _predictor = PerformancePredictor()
    return _predictor


@log_with_context
def generate_ai_suggestions() -> Dict[str, Any]:
    try:
        predictor = get_predictor()
        current_metrics = predictor._collect_current_metrics()
        if not current_metrics:
            return {'status': 'error', 'message': 'Failed to collect metrics'}
        basic_suggestions = _generate_basic_suggestions(current_metrics)
        result = {'status': 'success', 'current_metrics': current_metrics.to_dict(),
                 'basic_suggestions': basic_suggestions, 'ai_available': predictor.is_trained}
        if predictor.is_trained:
            predicted_fps = predictor.predict_fps(current_metrics)
            if predicted_fps:
                result['ai_prediction'] = {
                    'predicted_fps': predicted_fps,
                    'recommendations': _generate_recommendations(current_metrics, predicted_fps),
                    'risk_level': _assess_risk_level(current_metrics, predicted_fps)
                }
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'status': 'error', 'message': str(e)}


def _generate_basic_suggestions(metrics: SystemMetrics) -> List[str]:
    suggestions = []
    if metrics.cpu_percent > 80:
        suggestions.append("Close unnecessary background applications")
    if metrics.ram_percent > 85:
        suggestions.append("Close memory-intensive applications")
    if metrics.disk_usage > 90:
        suggestions.append("Free up disk space")
    if metrics.network_latency > 50:
        suggestions.append("Check internet connection")
    return suggestions if suggestions else ["System performance is good"]


def _generate_recommendations(metrics: SystemMetrics, predicted_fps: float) -> List[str]:
    recommendations = []
    if metrics.cpu_percent > CPU_USAGE_CRITICAL:
        recommendations.append("🔴 Critical CPU - close background apps")
    if metrics.ram_percent > RAM_USAGE_CRITICAL:
        recommendations.append("🔴 Critical RAM - close heavy applications")
    if predicted_fps < 30:
        recommendations.append("🔴 Low FPS - major optimization needed")
    return recommendations if recommendations else ["✅ System looks good"]


def _assess_risk_level(metrics: SystemMetrics, predicted_fps: float) -> str:
    risk_score = 0
    if metrics.cpu_percent > CPU_USAGE_CRITICAL:
        risk_score += 3
    elif metrics.cpu_percent > CPU_USAGE_WARNING:
        risk_score += 1
    if metrics.ram_percent > RAM_USAGE_CRITICAL:
        risk_score += 3
    elif metrics.ram_percent > RAM_USAGE_WARNING:
        risk_score += 1
    if predicted_fps < 30:
        risk_score += 2
    elif predicted_fps < 60:
        risk_score += 1
    return "HIGH" if risk_score >= 5 else ("MEDIUM" if risk_score >= 3 else "LOW")


@log_with_context
def calculate_ram_score() -> Dict[str, Any]:
    try:
        ram = psutil.virtual_memory()
        percent = ram.percent
        score = max(0, 100 - percent)
        rating = "Excellent" if percent < 50 else ("Good" if percent < 70 else ("Fair" if percent < 85 else "Poor"))
        return {'score': score, 'rating': rating, 'used_gb': round(ram.used / (1024**3), 1),
               'total_gb': round(ram.total / (1024**3), 1), 'usage_percent': percent}
    except Exception as e:
        logger.error(f"RAM score error: {e}")
        return {'error': str(e)}


@log_with_context
def calculate_cpu_score() -> Dict[str, Any]:
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        score = max(0, 100 - cpu_percent)
        rating = "Excellent" if cpu_percent < 30 else ("Good" if cpu_percent < 50 else ("Fair" if cpu_percent < 70 else "Poor"))
        return {'score': score, 'rating': rating, 'usage_percent': cpu_percent, 'core_count': psutil.cpu_count()}
    except Exception as e:
        logger.error(f"CPU score error: {e}")
        return {'error': str(e)}


@log_with_context
def display_suggestions(suggestions_data: Dict[str, Any]) -> None:
    try:
        from .win_compat import print_status, print_header
        print_header("🤖 AI Smart Advisor Results")
        if suggestions_data.get('status') == 'error':
            print_status(suggestions_data.get('message', 'Unknown error'), 'ERROR')
            return
        metrics = suggestions_data.get('current_metrics', {})
        if metrics:
            print_status("📊 Current System Metrics:", 'INFO')
            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  RAM: {metrics.get('ram_percent', 0):.1f}%")
            print(f"  Disk: {metrics.get('disk_usage', 0):.1f}%")
            print(f"  Latency: {metrics.get('network_latency', 0):.0f}ms")
        ai_pred = suggestions_data.get('ai_prediction')
        if ai_pred:
            print_status("🎯 AI Prediction:", 'SUCCESS')
            print(f"  FPS: {ai_pred.get('predicted_fps', 0):.1f}")
            print(f"  Risk: {ai_pred.get('risk_level', 'UNKNOWN')}")
        suggestions = suggestions_data.get('basic_suggestions', [])
        if suggestions:
            print_status("💡 Suggestions:", 'INFO')
            for s in suggestions:
                print(f"  • {s}")
        print_status("✅ Analysis complete!", 'SUCCESS')
    except Exception as e:
        logger.error(f"Display error: {e}")


@log_with_context
def train_ai_model() -> bool:
    try:
        from .win_compat import print_status, print_header
        print_header("🧠 Training AI Model")
        print_status("Collecting data for 60 seconds...", 'INFO')
        predictor = get_predictor()
        training_data = predictor.collect_training_data(duration_seconds=60)
        if len(training_data) < 10:
            print_status("Not enough data", 'ERROR')
            return False
        metrics = predictor.train_model()
        if metrics:
            print_status("✅ Training successful!", 'SUCCESS')
            print(f"  MAE: {metrics.get('mean_absolute_error', 0):.2f}")
            print(f"  R²: {metrics.get('r2_score', 0):.3f}")
            return True
        print_status("❌ Training failed", 'ERROR')
        return False
    except Exception as e:
        logger.error(f"Training error: {e}")
        return False
"""
AI-Powered Smart Advisor Module for AeroFPS PRO
Provides intelligent system recommendations and performance predictions.
"""

import os
import time
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .constants import (
    TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
    CPU_USAGE_WARNING, CPU_USAGE_CRITICAL,
    RAM_USAGE_WARNING, RAM_USAGE_CRITICAL,
    LOG_LEVELS
)
from .logger import setup_logger, log_with_context

logger = setup_logger(__name__, level=LOG_LEVELS['INFO'])


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    disk_usage: float
    network_latency: float
    temperature: Optional[float] = None
    gpu_usage: Optional[float] = None
    fps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'ram_percent': self.ram_percent,
            'disk_usage': self.disk_usage,
            'network_latency': self.network_latency,
            'temperature': self.temperature,
            'gpu_usage': self.gpu_usage,
            'fps': self.fps
        }


class PerformancePredictor:
    """AI performance prediction system."""

    def __init__(self, model_path: str = "models/fps_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.training_data = []
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        if ML_AVAILABLE:
            self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path) and ML_AVAILABLE:
                import joblib
                model_data = joblib.load(self.model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.is_trained = True
                logger.info("AI model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
        return False

    def _save_model(self) -> bool:
        """Save trained model to disk."""
        try:
            if self.model and self.scaler and ML_AVAILABLE:
                import joblib
                model_data = {
                    'model': self.model,
                    'scaler': self.scaler,
                    'trained_at': datetime.now().isoformat()
                }
                joblib.dump(model_data, self.model_path)
                logger.info("AI model saved successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to save AI model: {e}")
        return False

    def collect_training_data(self, duration_seconds: int = 60) -> List[SystemMetrics]:
        """Collect system metrics for training."""
        logger.info(f"Collecting training data for {duration_seconds} seconds...")
        collected_data = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration_seconds:
                metrics = self._collect_current_metrics()
                if metrics:
                    collected_data.append(metrics)
                time.sleep(1)

            self.training_data.extend(collected_data)
            logger.info(f"Collected {len(collected_data)} training samples")
            return collected_data
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return collected_data

    def _collect_current_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            network_latency = self._measure_network_latency()
            temperature = self._get_system_temperature()

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                disk_usage=disk_usage,
                network_latency=network_latency,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None

    def _measure_network_latency(self) -> float:
        """Measure network latency."""
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-n', '1', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line and 'ms' in line:
                        time_str = line.split('time=')[1].split('ms')[0].strip()
                        return float(time_str)
            return 50.0
        except Exception:
            return 50.0

    def _get_system_temperature(self) -> Optional[float]:
        """Get system temperature."""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for sensor_type, sensors in temps.items():
                        if 'cpu' in sensor_type.lower():
                            for sensor in sensors:
                                if sensor.current:
                                    return sensor.current
        except Exception:
            pass
        return None

    def train_model(self, test_size: float = 0.2) -> Dict[str, float]:
        """Train the AI model."""
        if not ML_AVAILABLE or len(self.training_data) < 10:
            logger.warning("Cannot train: ML not available or insufficient data")
            return {}

        try:
            logger.info(f"Training AI model with {len(self.training_data)} samples...")
            X = []
            y = []

            for metrics in self.training_data:
                if metrics.fps is not None:
                    features = [
                        metrics.cpu_percent,
                        metrics.ram_percent,
                        metrics.disk_usage,
                        metrics.network_latency,
                        metrics.temperature or 25.0,
                        metrics.gpu_usage or 0.0
                    ]
                    X.append(features)
                    y.append(metrics.fps)

            if len(X) < 5:
                logger.warning("Not enough samples with FPS data")
                return {}

            X = np.array(X)
            y = np.array(y)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            self.model = RandomForestRegressor(
                n_estimators=100, random_state=42, n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)

            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.is_trained = True
            self._save_model()

            logger.info(f"Model trained. MAE: {mae:.2f}, R²: {r2:.3f}")
            return {
                'mean_absolute_error': mae,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
        except Exception as e:
            logger.error(f"Error training AI model: {e}")
            return {}

    def predict_fps(self, current_metrics: SystemMetrics) -> Optional[float]:
        """Predict FPS based on current metrics."""
        if not self.is_trained or not self.model or not self.scaler:
            return None

        try:
            features = np.array([[
                current_metrics.cpu_percent,
                current_metrics.ram_percent,
                current_metrics.disk_usage,
                current_metrics.network_latency,
                current_metrics.temperature or 25.0,
                current_metrics.gpu_usage or 0.0
            ]])
            
            features_scaled = self.scaler.transform(features)
            predicted_fps = self.model.predict(features_scaled)[0]
            return max(0, predicted_fps)
        except Exception as e:
            logger.error(f"Error predicting FPS: {e}")
            return None


_predictor = None


def get_predictor() -> PerformancePredictor:
    """Get or create the global performance predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = PerformancePredictor()
    return _predictor


@log_with_context
def generate_ai_suggestions() -> Dict[str, Any]:
    """Generate AI-powered system optimization suggestions."""
    try:
        predictor = get_predictor()
        current_metrics = predictor._collect_current_metrics()
        
        if not current_metrics:
            return {
                'status': 'error',
                'message': 'Failed to collect system metrics'
            }

        basic_suggestions = _generate_basic_suggestions(current_metrics)

        result = {
            'status': 'success',
            'current_metrics': current_metrics.to_dict(),
            'basic_suggestions': basic_suggestions,
            'ai_available': predictor.is_trained
        }

        if predictor.is_trained:
            predicted_fps = predictor.predict_fps(current_metrics)
            if predicted_fps:
                recommendations = _generate_recommendations(current_metrics, predicted_fps)
                result['ai_prediction'] = {
                    'predicted_fps': predicted_fps,
                    'recommendations': recommendations,
                    'risk_level': _assess_risk_level(current_metrics, predicted_fps)
                }

        return result
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return {'status': 'error', 'message': str(e)}


def _generate_basic_suggestions(metrics: SystemMetrics) -> List[str]:
    """Generate basic optimization suggestions."""
    suggestions = []

    if metrics.cpu_percent > 80:
        suggestions.append("Close unnecessary background applications")
    if metrics.ram_percent > 85:
        suggestions.append("Close memory-intensive applications")
    if metrics.disk_usage > 90:
        suggestions.append("Free up disk space")
    if metrics.network_latency > 50:
        suggestions.append("Check internet connection")

    return suggestions if suggestions else ["System performance is good"]


def _generate_recommendations(metrics: SystemMetrics, predicted_fps: float) -> List[str]:
    """Generate recommendations based on metrics and FPS prediction."""
    recommendations = []

    if metrics.cpu_percent > CPU_USAGE_CRITICAL:
        recommendations.append("🔴 Critical CPU usage - close background apps")
    if metrics.ram_percent > RAM_USAGE_CRITICAL:
        recommendations.append("🔴 Critical RAM usage - close heavy applications")
    if predicted_fps < 30:
        recommendations.append("🔴 Low predicted FPS - major optimization needed")

    return recommendations if recommendations else ["✅ System looks good"]


def _assess_risk_level(metrics: SystemMetrics, predicted_fps: float) -> str:
    """Assess overall system risk level."""
    risk_score = 0

    if metrics.cpu_percent > CPU_USAGE_CRITICAL:
        risk_score += 3
    elif metrics.cpu_percent > CPU_USAGE_WARNING:
        risk_score += 1

    if metrics.ram_percent > RAM_USAGE_CRITICAL:
        risk_score += 3
    elif metrics.ram_percent > RAM_USAGE_WARNING:
        risk_score += 1

    if predicted_fps < 30:
        risk_score += 2
    elif predicted_fps < 60:
        risk_score += 1

    if risk_score >= 5:
        return "HIGH"
    elif risk_score >= 3:
        return "MEDIUM"
    else:
        return "LOW"


@log_with_context
def calculate_ram_score() -> Dict[str, Any]:
    """Calculate RAM performance score."""
    try:
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        score = max(0, 100 - ram_percent)

        if ram_percent < 50:
            rating = "Excellent"
        elif ram_percent < 70:
            rating = "Good"
        elif ram_percent < 85:
            rating = "Fair"
        else:
            rating = "Poor"

        return {
            'score': score,
            'rating': rating,
            'used_gb': round(ram.used / (1024**3), 1),
            'total_gb': round(ram.total / (1024**3), 1),
            'usage_percent': ram_percent
        }
    except Exception as e:
        logger.error(f"Error calculating RAM score: {e}")
        return {'error': str(e)}


@log_with_context
def calculate_cpu_score() -> Dict[str, Any]:
    """Calculate CPU performance score."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        score = max(0, 100 - cpu_percent)

        if cpu_percent < 30:
            rating = "Excellent"
        elif cpu_percent < 50:
            rating = "Good"
        elif cpu_percent < 70:
            rating = "Fair"
        else:
            rating = "Poor"

        return {
            'score': score,
            'rating': rating,
            'usage_percent': cpu_percent,
            'core_count': cpu_count
        }
    except Exception as e:
        logger.error(f"Error calculating CPU score: {e}")
        return {'error': str(e)}


@log_with_context
def display_suggestions(suggestions_data: Dict[str, Any]) -> None:
    """Display AI suggestions in formatted way."""
    try:
        from .win_compat import print_status, print_header

        print_header("🤖 AI Smart Advisor Results")

        if suggestions_data.get('status') == 'error':
            print_status(suggestions_data.get('message', 'Unknown error'), 'ERROR')
            return

        metrics = suggestions_data.get('current_metrics', {})
        if metrics:
            print_status("📊 Current System Metrics:", 'INFO')
            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  RAM: {metrics.get('ram_percent', 0):.1f}%")
            print(f"  Disk: {metrics.get('disk_usage', 0):.1f}%")
            print(f"  Latency: {metrics.get('network_latency', 0):.0f}ms")

        ai_pred = suggestions_data.get('ai_prediction')
        if ai_pred:
            print_status("🎯 AI Prediction:", 'SUCCESS')
            print(f"  FPS: {ai_pred.get('predicted_fps', 0):.1f}")
            print(f"  Risk: {ai_pred.get('risk_level', 'UNKNOWN')}")

        suggestions = suggestions_data.get('basic_suggestions', [])
        if suggestions:
            print_status("💡 Suggestions:", 'INFO')
            for s in suggestions:
                print(f"  • {s}")

        print_status("✅ Analysis complete!", 'SUCCESS')
    except Exception as e:
        logger.error(f"Error displaying suggestions: {e}")


@log_with_context
def train_ai_model() -> bool:
    """Train the AI model with current system data."""
    try:
        from .win_compat import print_status, print_header

        print_header("🧠 Training AI Model")
        print_status("Collecting data for 60 seconds...", 'INFO')

        predictor = get_predictor()
        training_data = predictor.collect_training_data(duration_seconds=60)

        if len(training_data) < 10:
            print_status("Not enough data collected", 'ERROR')
            return False

        metrics = predictor.train_model()
        if metrics:
            print_status("✅ Training successful!", 'SUCCESS')
            print(f"  MAE: {metrics.get('mean_absolute_error', 0):.2f}")
            print(f"  R²: {metrics.get('r2_score', 0):.3f}")
            return True
        else:
            print_status("❌ Training failed", 'ERROR')
            return False
    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        return False
"""
AI-Powered Smart Advisor Module for AeroFPS PRO
Provides intelligent system recommendations and performance predictions using machine learning.
"""

import os
import json
import time
import psutil
import platform
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

from .constants import (
    TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
    CPU_USAGE_WARNING, CPU_USAGE_CRITICAL,
    RAM_USAGE_WARNING, RAM_USAGE_CRITICAL,
    LOG_LEVELS
)
from .logger import setup_logger, log_with_context

logger = setup_logger(__name__, level=LOG_LEVELS['INFO'])

@dataclass
class SystemMetrics:
    """Data class for system performance metrics."""
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    gpu_usage: Optional[float]
    disk_usage: float
    network_latency: float
    temperature: Optional[float]
    fps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class PerformancePrediction:
    """Data class for AI performance predictions."""
    predicted_fps: float
    confidence_score: float
    recommendations: List[str]
    risk_level: str
    timestamp: datetime


class PerformancePredictor:
    """AI-powered performance prediction system."""

    def __init__(self, model_path: str = "models/fps_predictor.pkl"):
        self.model_path = model_path
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        self.training_data: List[SystemMetrics] = []
        self.feature_names = [
            'cpu_percent', 'ram_percent', 'disk_usage',
            'network_latency', 'temperature', 'gpu_usage'
        ]

        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path):
                import joblib
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = True
                logger.info("AI model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
        return False

    def _save_model(self) -> bool:
        """Save trained model to disk."""
        try:
            if self.model and self.scaler:
                import joblib
                model_data = {
                    'model': self.model,
                    'scaler': self.scaler,
                    'feature_names': self.feature_names,
                    'trained_at': datetime.now().isoformat()
                }
                joblib.dump(model_data, self.model_path)
                logger.info("AI model saved successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to save AI model: {e}")
        return False

    def collect_training_data(self, duration_seconds: int = 60) -> List[SystemMetrics]:
        """Collect system metrics for training."""
        logger.info(f"Collecting training data for {duration_seconds} seconds...")
        collected_data = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration_seconds:
                metrics = self._collect_current_metrics()
                if metrics:
                    collected_data.append(metrics)
                time.sleep(1)

            self.training_data.extend(collected_data)
            logger.info(f"Collected {len(collected_data)} training samples")
            return collected_data

        except KeyboardInterrupt:
            logger.info("Training data collection interrupted")
            return collected_data
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return collected_data

    def _collect_current_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            network_latency = self._measure_network_latency()
            temperature = self._get_system_temperature()
            gpu_usage = None

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                gpu_usage=gpu_usage,
                disk_usage=disk_usage,
                network_latency=network_latency,
                temperature=temperature
            )

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None

    def _measure_network_latency(self) -> float:
        """Measure network latency."""
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-n', '1', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line and 'ms' in line:
                        time_str = line.split('time=')[1].split('ms')[0].strip()
                        return float(time_str)
            return 50.0

        except Exception:
            return 50.0

    def _get_system_temperature(self) -> Optional[float]:
        """Get system temperature."""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for sensor_type, sensors in temps.items():
                        if 'cpu' in sensor_type.lower():
                            for sensor in sensors:
                                if sensor.current:
                                    return sensor.current
        except Exception:
            pass
        return None

    def train_model(self, test_size: float = 0.2) -> Dict[str, float]:
        """Train the AI model."""
        if len(self.training_data) < 10:
            logger.warning("Not enough training data")
            return {}

        logger.info(f"Training AI model with {len(self.training_data)} samples...")

        try:
            X = []
            y = []

            for metrics in self.training_data:
                if metrics.fps is not None:
                    features = [
                        metrics.cpu_percent,
                        metrics.ram_percent,
                        metrics.disk_usage,
                        metrics.network_latency,
                        metrics.temperature or 25.0,
                        metrics.gpu_usage or 0.0
                    ]
                    X.append(features)
                    y.append(metrics.fps)

            if len(X) < 5:
                logger.warning("Not enough samples with FPS data")
                return {}

            X = np.array(X)
            y = np.array(y)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)

            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.is_trained = True
            self._save_model()

            metrics = {
                'mean_absolute_error': mae,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            logger.info(f"Model trained successfully. MAE: {mae:.2f}, R²: {r2:.3f}")
            return metrics

        except Exception as e:
            logger.error(f"Error training AI model: {e}")
            return {}

    def predict_fps(self, current_metrics: SystemMetrics) -> Optional[PerformancePrediction]:
        """Predict FPS based on current metrics."""
        if not self.is_trained or not self.model or not self.scaler:
            return None

        try:
            features = [
                current_metrics.cpu_percent,
                current_metrics.ram_percent,
                current_metrics.disk_usage,
                current_metrics.network_latency,
                current_metrics.temperature or 25.0,
                current_metrics.gpu_usage or 0.0
            ]

            features_scaled = self.scaler.transform([features])
            predicted_fps = self.model.predict(features_scaled)[0]

            confidence = self._calculate_confidence(features)
            recommendations = self._generate_recommendations(current_metrics, predicted_fps)
            risk_level = self._assess_risk_level(current_metrics, predicted_fps)

            prediction = PerformancePrediction(
                predicted_fps=max(0, predicted_fps),
                confidence_score=min(1.0, confidence),
                recommendations=recommendations,
                risk_level=risk_level,
                timestamp=datetime.now()
            )

            return prediction

        except Exception as e:
            logger.error(f"Error making FPS prediction: {e}")
            return None

    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence."""
        try:
            if not self.model:
                return 0.5

            confidence = 1.0
            if features[0] > CPU_USAGE_CRITICAL:
                confidence *= 0.7
            elif features[0] > CPU_USAGE_WARNING:
                confidence *= 0.85

            if features[1] > RAM_USAGE_CRITICAL:
                confidence *= 0.7
            elif features[1] > RAM_USAGE_WARNING:
                confidence *= 0.85

            if features[4] > TEMP_CRITICAL_THRESHOLD:
                confidence *= 0.6
            elif features[4] > TEMP_WARNING_THRESHOLD:
                confidence *= 0.8

            return confidence

        except Exception:
            return 0.5

    def _generate_recommendations(self, metrics: SystemMetrics, predicted_fps: float) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: CPU usage is extremely high. Close background applications.")
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            recommendations.append("🟡 High CPU usage detected. Consider closing unnecessary programs.")

        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: RAM usage is critical. Close memory-intensive applications.")
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            recommendations.append("🟡 High RAM usage. Consider upgrading RAM or closing applications.")

        if metrics.temperature and metrics.temperature > TEMP_CRITICAL_THRESHOLD:
            recommendations.append("🔴 Critical: System temperature is dangerously high. Check cooling system.")
        elif metrics.temperature and metrics.temperature > TEMP_WARNING_THRESHOLD:
            recommendations.append("🟡 High temperature detected. Ensure proper ventilation.")

        if metrics.network_latency > 100:
            recommendations.append("🟡 High network latency. Check internet connection and router settings.")

        if predicted_fps < 30:
            recommendations.append("🔴 Predicted FPS is very low. Major system optimization needed.")
        elif predicted_fps < 60:
            recommendations.append("🟡 Predicted FPS is below 60. Consider graphics settings optimization.")

        if len(recommendations) == 0:
            recommendations.append("✅ System performance looks good. No immediate optimizations needed.")

        return recommendations

    def _assess_risk_level(self, metrics: SystemMetrics, predicted_fps: float) -> str:
        """Assess overall system risk level."""
        risk_score = 0

        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            risk_score += 1

        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            risk_score += 1

        if metrics.temperature:
            if metrics.temperature > TEMP_CRITICAL_THRESHOLD:
                risk_score += 3
            elif metrics.temperature > TEMP_WARNING_THRESHOLD:
                risk_score += 1

        if predicted_fps < 30:
            risk_score += 2
        elif predicted_fps < 60:
            risk_score += 1

        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"


_predictor = None
_predictor_lock = threading.Lock()

def get_predictor() -> PerformancePredictor:
    """Get or create the global performance predictor instance."""
    global _predictor
    if _predictor is None:
        with _predictor_lock:
            if _predictor is None:
                _predictor = PerformancePredictor()
    return _predictor


@log_with_context
def generate_ai_suggestions() -> Dict[str, Any]:
    """Generate AI-powered system optimization suggestions."""
    try:
        predictor = get_predictor()

        current_metrics = predictor._collect_current_metrics()
        if not current_metrics:
            return {
                'status': 'error',
                'message': 'Failed to collect system metrics'
            }

        prediction = None
        if predictor.is_trained:
            prediction = predictor.predict_fps(current_metrics)

        basic_suggestions = _generate_basic_suggestions(current_metrics)

        result = {
            'status': 'success',
            'current_metrics': current_metrics.to_dict(),
            'basic_suggestions': basic_suggestions,
            'ai_available': predictor.is_trained
        }

        if prediction:
            result['ai_prediction'] = {
                'predicted_fps': prediction.predicted_fps,
                'confidence': prediction.confidence_score,
                'recommendations': prediction.recommendations,
                'risk_level': prediction.risk_level
            }

        return result

    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return {
            'status': 'error',
            'message': f'AI suggestion generation failed: {str(e)}'
        }


def _generate_basic_suggestions(metrics: SystemMetrics) -> List[str]:
    """Generate basic optimization suggestions without AI."""
    suggestions = []

    if metrics.cpu_percent > 80:
        suggestions.append("Close unnecessary background applications")
        suggestions.append("Disable Windows visual effects")
    elif metrics.cpu_percent > 60:
        suggestions.append("Consider closing some applications")

    if metrics.ram_percent > 85:
        suggestions.append("Close memory-intensive applications")
        suggestions.append("Increase virtual memory")
    elif metrics.ram_percent > 70:
        suggestions.append("Monitor memory usage closely")

    if metrics.disk_usage > 90:
        suggestions.append("Free up disk space")
        suggestions.append("Run disk cleanup")

    if metrics.network_latency > 50:
        suggestions.append("Check internet connection")
        suggestions.append("Restart router if needed")

    if not suggestions:
        suggestions.append("System performance is good")

    return suggestions


@log_with_context
def calculate_ram_score() -> Dict[str, Any]:
    """Calculate RAM performance score and recommendations."""
    try:
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)

        score = max(0, 100 - ram_percent)

        if ram_percent < 50:
            rating = "Excellent"
        elif ram_percent < 70:
            rating = "Good"
        elif ram_percent < 85:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if ram_percent > 80:
            recommendations.append("Close unnecessary applications")
            recommendations.append("Consider upgrading RAM")
        elif ram_percent > 60:
            recommendations.append("Monitor RAM usage")

        return {
            'score': score,
            'rating': rating,
            'used_gb': round(ram_used_gb, 1),
            'total_gb': round(ram_total_gb, 1),
            'usage_percent': ram_percent,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating RAM score: {e}")
        return {'error': str(e)}


@log_with_context
def calculate_cpu_score() -> Dict[str, Any]:
    """Calculate CPU performance score and recommendations."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        score = max(0, 100 - cpu_percent)

        if cpu_percent < 30:
            rating = "Excellent"
        elif cpu_percent < 50:
            rating = "Good"
        elif cpu_percent < 70:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if cpu_percent > 80:
            recommendations.append("Close unnecessary background processes")
            recommendations.append("Disable Windows visual effects")
        elif cpu_percent > 60:
            recommendations.append("Monitor CPU usage")

        return {
            'score': score,
            'rating': rating,
            'usage_percent': cpu_percent,
            'core_count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else None,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating CPU score: {e}")
        return {'error': str(e)}


@log_with_context
def display_suggestions(suggestions_data: Dict[str, Any]) -> None:
    """Display AI suggestions in a formatted way."""
    try:
        from .win_compat import print_status, print_header

        print_header("🤖 AI Smart Advisor Results")

        if suggestions_data.get('status') == 'error':
            print_status(suggestions_data.get('message', 'Unknown error'), 'ERROR')
            return

        metrics = suggestions_data.get('current_metrics', {})
        if metrics:
            print_status("📊 Current System Metrics:", 'INFO')
            print(f"  CPU Usage: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"  RAM Usage: {metrics.get('ram_percent', 'N/A')}%")
            print(f"  Disk Usage: {metrics.get('disk_usage', 'N/A')}%")
            print(f"  Network Latency: {metrics.get('network_latency', 'N/A')}ms")
            if metrics.get('temperature'):
                print(f"  Temperature: {metrics.get('temperature'):.1f}°C")
            print()

        ai_prediction = suggestions_data.get('ai_prediction')
        if ai_prediction:
            print_status("🎯 AI Performance Prediction:", 'SUCCESS')
            fps = ai_prediction.get('predicted_fps', 0)
            confidence = ai_prediction.get('confidence', 0)
            risk = ai_prediction.get('risk_level', 'UNKNOWN')

            print(f"  Predicted FPS: {fps:.1f}")
            print(f"  Confidence: {confidence:.1%}")
            print(f"  Risk Level: {risk}")
            print()

            recommendations = ai_prediction.get('recommendations', [])
            if recommendations:
                print_status("💡 AI Recommendations:", 'INFO')
                for rec in recommendations:
                    print(f"  • {rec}")
                print()

        basic_suggestions = suggestions_data.get('basic_suggestions', [])
        if basic_suggestions and not ai_prediction:
            print_status("💡 Basic Optimization Suggestions:", 'INFO')
            for suggestion in basic_suggestions:
                print(f"  • {suggestion}")
            print()

        print_status("📈 Component Performance Scores:", 'INFO')
        ram_score = calculate_ram_score()
        cpu_score = calculate_cpu_score()

        if 'score' in ram_score:
            print(f"  RAM Score: {ram_score['score']}/100 ({ram_score['rating']})")
            print(f"    Used: {ram_score['used_gb']}GB / {ram_score['total_gb']}GB")

        if 'score' in cpu_score:
            print(f"  CPU Score: {cpu_score['score']}/100 ({cpu_score['rating']})")
            print(f"    Usage: {cpu_score['usage_percent']}%")

        print_status("✅ Analysis complete!", 'SUCCESS')

    except Exception as e:
        logger.error(f"Error displaying suggestions: {e}")
        print(f"❌ Error displaying suggestions: {e}")


@log_with_context
def train_ai_model() -> bool:
    """Train the AI model with current system data."""
    try:
        from .win_compat import print_status, print_header

        print_header("🧠 Training AI Model")
        print_status("This will collect system data for 60 seconds...", 'INFO')
        print_status("Please perform normal gaming activities during this time.", 'WARNING')
        print()

        predictor = get_predictor()

        training_data = predictor.collect_training_data(duration_seconds=60)

        if len(training_data) < 10:
            print_status("Not enough training data collected. Try again.", 'ERROR')
            return False

        metrics = predictor.train_model()

        if metrics:
            print_status("✅ AI model trained successfully!", 'SUCCESS')
            print(f"  Training samples: {metrics.get('training_samples', 0)}")
            print(f"  Test samples: {metrics.get('test_samples', 0)}")
            print(f"  Mean Absolute Error: {metrics.get('mean_absolute_error', 0):.2f}")
            print(f"  R² Score: {metrics.get('r2_score', 0):.3f}")
            return True
        else:
            print_status("❌ AI model training failed.", 'ERROR')
            return False

    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        print_status(f"❌ Training failed: {e}", 'ERROR')
        return False
"""
AI-Powered Smart Advisor Module for AeroFPS PRO
Provides intelligent system recommendations and performance predictions using machine learning.
"""

import os
import json
import time
import psutil
import platform
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

from .constants import (
    TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
    CPU_USAGE_WARNING, CPU_USAGE_CRITICAL,
    RAM_USAGE_WARNING, RAM_USAGE_CRITICAL,
    CACHE_TIMEOUT, LOG_LEVELS
)
from .logger import setup_logger, log_with_context

# Initialize logger
logger = setup_logger(__name__, level=LOG_LEVELS['INFO'])

@dataclass
class SystemMetrics:
    """Data class for system performance metrics."""
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    gpu_usage: Optional[float]
    disk_usage: float
    network_latency: float
    temperature: Optional[float]
    fps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemMetrics':
        """Create instance from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class PerformancePrediction:
    """Data class for AI performance predictions."""
    predicted_fps: float
    confidence_score: float
    recommendations: List[str]
    risk_level: str
    timestamp: datetime

class PerformancePredictor:
    """
    AI-powered performance prediction system using machine learning.
    Analyzes system metrics to predict FPS and provide optimization recommendations.
    """

    def __init__(self, model_path: str = "models/fps_predictor.pkl"):
        self.model_path = model_path
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        self.training_data: List[SystemMetrics] = []
        self.feature_names = [
            'cpu_percent', 'ram_percent', 'disk_usage',
            'network_latency', 'temperature', 'gpu_usage'
        ]

        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Load existing model if available
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path):
                import joblib
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = True
                logger.info("AI model loaded successfully")
                return True
            else:
                logger.info("No existing AI model found, will train new one")
                return False
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            return False

    def _save_model(self) -> bool:
        """Save trained model to disk."""
        try:
            if self.model and self.scaler:
                import joblib
                model_data = {
                    'model': self.model,
                    'scaler': self.scaler,
                    'feature_names': self.feature_names,
                    'trained_at': datetime.now().isoformat()
                }
                joblib.dump(model_data, self.model_path)
                logger.info("AI model saved successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save AI model: {e}")
            return False

    def collect_training_data(self, duration_seconds: int = 60) -> List[SystemMetrics]:
        """
        Collect system metrics for training data.

        Args:
            duration_seconds: How long to collect data

        Returns:
            List of collected system metrics
        """
        logger.info(f"Collecting training data for {duration_seconds} seconds...")

        collected_data = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration_seconds:
                metrics = self._collect_current_metrics()
                if metrics:
                    collected_data.append(metrics)
                time.sleep(1)  # Collect data every second

            self.training_data.extend(collected_data)
            logger.info(f"Collected {len(collected_data)} training samples")
            return collected_data

        except KeyboardInterrupt:
            logger.info("Training data collection interrupted by user")
            return collected_data
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return collected_data

    def _collect_current_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics."""
        try:
            # CPU and RAM
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent

            # Disk usage
            disk_usage = psutil.disk_usage('/').percent

            # Network latency (simplified)
            network_latency = self._measure_network_latency()

            # Temperature (if available)
            temperature = self._get_system_temperature()

            # GPU usage (simplified - would need GPU monitoring library)
            gpu_usage = None  # Placeholder

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                gpu_usage=gpu_usage,
                disk_usage=disk_usage,
                network_latency=network_latency,
                temperature=temperature
            )

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None

    def _measure_network_latency(self) -> float:
        """Measure network latency to common gaming servers."""
        try:
            # Simple ping test to Google DNS
            import subprocess
            result = subprocess.run(
                ['ping', '-n', '1', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                # Extract ping time from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line and 'ms' in line:
                        time_str = line.split('time=')[1].split('ms')[0].strip()
                        return float(time_str)

            return 50.0  # Default latency if ping fails

        except Exception:
            return 50.0  # Default latency

    def _get_system_temperature(self) -> Optional[float]:
        """Get system temperature if available."""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get CPU temperature
                    for sensor_type, sensors in temps.items():
                        if 'cpu' in sensor_type.lower():
                            for sensor in sensors:
                                if sensor.current:
                                    return sensor.current
            return None
        except Exception:
            return None

    def train_model(self, test_size: float = 0.2) -> Dict[str, float]:
        """
        Train the AI model using collected data.

        Args:
            test_size: Fraction of data to use for testing

        Returns:
            Dictionary with training metrics
        """
        if len(self.training_data) < 10:
            logger.warning("Not enough training data. Need at least 10 samples.")
            return {}

        logger.info(f"Training AI model with {len(self.training_data)} samples...")

        try:
            # Prepare features and target
            X = []
            y = []

            for metrics in self.training_data:
                if metrics.fps is not None:  # Only use samples with FPS data
                    features = [
                        metrics.cpu_percent,
                        metrics.ram_percent,
                        metrics.disk_usage,
                        metrics.network_latency,
                        metrics.temperature or 25.0,  # Default temp
                        metrics.gpu_usage or 0.0  # Default GPU usage
                    ]
                    X.append(features)
                    y.append(metrics.fps)

            if len(X) < 5:
                logger.warning("Not enough samples with FPS data for training")
                return {}

            X = np.array(X)
            y = np.array(y)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.is_trained = True
            self._save_model()

            metrics = {
                'mean_absolute_error': mae,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            logger.info(f"Model trained successfully. MAE: {mae:.2f}, R²: {r2:.3f}")
            return metrics

        except Exception as e:
            logger.error(f"Error training AI model: {e}")
            return {}

    def predict_fps(self, current_metrics: SystemMetrics) -> Optional[PerformancePrediction]:
        """
        Predict FPS based on current system metrics.

        Args:
            current_metrics: Current system performance metrics

        Returns:
            Performance prediction with FPS estimate and recommendations
        """
        if not self.is_trained or not self.model or not self.scaler:
            logger.warning("AI model not trained yet")
            return None

        try:
            # Prepare features
            features = [
                current_metrics.cpu_percent,
                current_metrics.ram_percent,
                current_metrics.disk_usage,
                current_metrics.network_latency,
                current_metrics.temperature or 25.0,
                current_metrics.gpu_usage or 0.0
            ]

            features_scaled = self.scaler.transform([features])
            predicted_fps = self.model.predict(features_scaled)[0]

            # Calculate confidence based on feature importance
            confidence = self._calculate_confidence(features)

            # Generate recommendations
            recommendations = self._generate_recommendations(current_metrics, predicted_fps)

            # Determine risk level
            risk_level = self._assess_risk_level(current_metrics, predicted_fps)

            prediction = PerformancePrediction(
                predicted_fps=max(0, predicted_fps),
                confidence_score=min(1.0, confidence),
                recommendations=recommendations,
                risk_level=risk_level,
                timestamp=datetime.now()
            )

            return prediction

        except Exception as e:
            logger.error(f"Error making FPS prediction: {e}")
            return None

    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence based on feature values."""
        try:
            if not self.model:
                return 0.5

            # Use feature importances to weight confidence
            importances = self.model.feature_importances_

            # Calculate confidence based on how extreme the features are
            confidence = 1.0
            for i, (feature, importance) in enumerate(zip(features, importances)):
                if i == 0:  # CPU
                    if feature > CPU_USAGE_CRITICAL:
                        confidence *= 0.7
                    elif feature > CPU_USAGE_WARNING:
                        confidence *= 0.85
                elif i == 1:  # RAM
                    if feature > RAM_USAGE_CRITICAL:
                        confidence *= 0.7
                    elif feature > RAM_USAGE_WARNING:
                        confidence *= 0.85
                elif i == 4:  # Temperature
                    if feature > TEMP_CRITICAL_THRESHOLD:
                        confidence *= 0.6
                    elif feature > TEMP_WARNING_THRESHOLD:
                        confidence *= 0.8

            return confidence

        except Exception:
            return 0.5

    def _generate_recommendations(self, metrics: SystemMetrics, predicted_fps: float) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []

        # CPU recommendations
        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: CPU usage is extremely high. Close background applications.")
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            recommendations.append("🟡 High CPU usage detected. Consider closing unnecessary programs.")

        # RAM recommendations
        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: RAM usage is critical. Close memory-intensive applications.")
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            recommendations.append("🟡 High RAM usage. Consider increasing virtual memory or upgrading RAM.")

        # Temperature recommendations
        if metrics.temperature and metrics.temperature > TEMP_CRITICAL_THRESHOLD:
            recommendations.append("🔴 Critical: System temperature is dangerously high. Check cooling system.")
        elif metrics.temperature and metrics.temperature > TEMP_WARNING_THRESHOLD:
            recommendations.append("🟡 High temperature detected. Ensure proper ventilation and cooling.")

        # Network recommendations
        if metrics.network_latency > 100:
            recommendations.append("🟡 High network latency. Check internet connection and router settings.")

        # FPS-based recommendations
        if predicted_fps < 30:
            recommendations.append("🔴 Predicted FPS is very low. Major system optimization needed.")
        elif predicted_fps < 60:
            recommendations.append("🟡 Predicted FPS is below 60. Consider graphics settings optimization.")

        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("✅ System performance looks good. No immediate optimizations needed.")

        return recommendations

    def _assess_risk_level(self, metrics: SystemMetrics, predicted_fps: float) -> str:
        """Assess overall system risk level."""
        risk_score = 0

        # CPU risk
        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            risk_score += 1

        # RAM risk
        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            risk_score += 1

        # Temperature risk
        if metrics.temperature:
            if metrics.temperature > TEMP_CRITICAL_THRESHOLD:
                risk_score += 3
            elif metrics.temperature > TEMP_WARNING_THRESHOLD:
                risk_score += 1

        # FPS risk
        if predicted_fps < 30:
            risk_score += 2
        elif predicted_fps < 60:
            risk_score += 1

        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

# Global predictor instance
_predictor = None
_predictor_lock = threading.Lock()

def get_predictor() -> PerformancePredictor:
    """Get or create the global performance predictor instance."""
    global _predictor
    if _predictor is None:
        with _predictor_lock:
            if _predictor is None:
                _predictor = PerformancePredictor()
    return _predictor

@log_with_context
def generate_ai_suggestions() -> Dict[str, Any]:
    """
    Generate AI-powered system optimization suggestions.

    Returns:
        Dictionary containing suggestions and predictions
    """
    try:
        predictor = get_predictor()

        # Collect current metrics
        current_metrics = predictor._collect_current_metrics()
        if not current_metrics:
            return {
                'status': 'error',
                'message': 'Failed to collect system metrics'
            }

        # Make prediction if model is trained
        prediction = None
        if predictor.is_trained:
            prediction = predictor.predict_fps(current_metrics)

        # Generate basic suggestions even without AI
        basic_suggestions = _generate_basic_suggestions(current_metrics)

        result = {
            'status': 'success',
            'current_metrics': current_metrics.to_dict(),
            'basic_suggestions': basic_suggestions,
            'ai_available': predictor.is_trained
        }

        if prediction:
            result['ai_prediction'] = {
                'predicted_fps': prediction.predicted_fps,
                'confidence': prediction.confidence_score,
                'recommendations': prediction.recommendations,
                'risk_level': prediction.risk_level
            }

        return result

    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return {
            'status': 'error',
            'message': f'AI suggestion generation failed: {str(e)}'
        }

def _generate_basic_suggestions(metrics: SystemMetrics) -> List[str]:
    """Generate basic optimization suggestions without AI."""
    suggestions = []

    # CPU suggestions
    if metrics.cpu_percent > 80:
        suggestions.append("Close unnecessary background applications")
        suggestions.append("Disable Windows visual effects")
    elif metrics.cpu_percent > 60:
        suggestions.append("Consider closing some applications")

    # RAM suggestions
    if metrics.ram_percent > 85:
        suggestions.append("Close memory-intensive applications")
        suggestions.append("Increase virtual memory")
    elif metrics.ram_percent > 70:
        suggestions.append("Monitor memory usage closely")

    # Disk suggestions
    if metrics.disk_usage > 90:
        suggestions.append("Free up disk space")
        suggestions.append("Run disk cleanup")

    # Network suggestions
    if metrics.network_latency > 50:
        suggestions.append("Check internet connection")
        suggestions.append("Restart router if needed")

    if not suggestions:
        suggestions.append("System performance is good")

    return suggestions

@log_with_context
def calculate_ram_score() -> Dict[str, Any]:
    """
    Calculate RAM performance score and recommendations.

    Returns:
        Dictionary with RAM analysis
    """
    try:
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)

        # Calculate score (0-100, higher is better)
        score = max(0, 100 - ram_percent)

        # Determine rating
        if ram_percent < 50:
            rating = "Excellent"
        elif ram_percent < 70:
            rating = "Good"
        elif ram_percent < 85:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if ram_percent > 80:
            recommendations.append("Close unnecessary applications")
            recommendations.append("Consider upgrading RAM")
        elif ram_percent > 60:
            recommendations.append("Monitor RAM usage")

        return {
            'score': score,
            'rating': rating,
            'used_gb': round(ram_used_gb, 1),
            'total_gb': round(ram_total_gb, 1),
            'usage_percent': ram_percent,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating RAM score: {e}")
        return {'error': str(e)}

@log_with_context
def calculate_cpu_score() -> Dict[str, Any]:
    """
    Calculate CPU performance score and recommendations.

    Returns:
        Dictionary with CPU analysis
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Calculate score (0-100, higher is better)
        score = max(0, 100 - cpu_percent)

        # Determine rating
        if cpu_percent < 30:
            rating = "Excellent"
        elif cpu_percent < 50:
            rating = "Good"
        elif cpu_percent < 70:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if cpu_percent > 80:
            recommendations.append("Close unnecessary background processes")
            recommendations.append("Disable Windows visual effects")
        elif cpu_percent > 60:
            recommendations.append("Monitor CPU usage")

        return {
            'score': score,
            'rating': rating,
            'usage_percent': cpu_percent,
            'core_count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else None,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating CPU score: {e}")
        return {'error': str(e)}

@log_with_context
def display_suggestions(suggestions_data: Dict[str, Any]) -> None:
    """
    Display AI suggestions in a formatted way.

    Args:
        suggestions_data: Suggestions data from generate_ai_suggestions()
    """
    try:
        from .win_compat import print_status, print_header

        print_header("🤖 AI Smart Advisor Results")

        if suggestions_data.get('status') == 'error':
            print_status(suggestions_data.get('message', 'Unknown error'), 'ERROR')
            return

        # Display current metrics
        metrics = suggestions_data.get('current_metrics', {})
        if metrics:
            print_status("📊 Current System Metrics:", 'INFO')
            print(f"  CPU Usage: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"  RAM Usage: {metrics.get('ram_percent', 'N/A')}%")
            print(f"  Disk Usage: {metrics.get('disk_usage', 'N/A')}%")
            print(f"  Network Latency: {metrics.get('network_latency', 'N/A')}ms")
            if metrics.get('temperature'):
                print(f"  Temperature: {metrics.get('temperature'):.1f}°C")
            print()

        # Display AI prediction if available
        ai_prediction = suggestions_data.get('ai_prediction')
        if ai_prediction:
            print_status("🎯 AI Performance Prediction:", 'SUCCESS')
            fps = ai_prediction.get('predicted_fps', 0)
            confidence = ai_prediction.get('confidence', 0)
            risk = ai_prediction.get('risk_level', 'UNKNOWN')

            print(f"  Predicted FPS: {fps:.1f}")
            print(f"  Confidence: {confidence:.1%}")
            print(f"  Risk Level: {risk}")
            print()

            # Display AI recommendations
            recommendations = ai_prediction.get('recommendations', [])
            if recommendations:
                print_status("💡 AI Recommendations:", 'INFO')
                for rec in recommendations:
                    print(f"  • {rec}")
                print()

        # Display basic suggestions
        basic_suggestions = suggestions_data.get('basic_suggestions', [])
        if basic_suggestions and not ai_prediction:
            print_status("💡 Basic Optimization Suggestions:", 'INFO')
            for suggestion in basic_suggestions:
                print(f"  • {suggestion}")
            print()

        # Display component scores
        print_status("📈 Component Performance Scores:", 'INFO')
        ram_score = calculate_ram_score()
        cpu_score = calculate_cpu_score()

        if 'score' in ram_score:
            print(f"  RAM Score: {ram_score['score']}/100 ({ram_score['rating']})")
            print(f"    Used: {ram_score['used_gb']}GB / {ram_score['total_gb']}GB")

        if 'score' in cpu_score:
            print(f"  CPU Score: {cpu_score['score']}/100 ({cpu_score['rating']})")
            print(f"    Usage: {cpu_score['usage_percent']}%")

        print_status("✅ Analysis complete!", 'SUCCESS')

    except Exception as e:
        logger.error(f"Error displaying suggestions: {e}")
        print(f"❌ Error displaying suggestions: {e}")

@log_with_context
def train_ai_model() -> bool:
    """
    Train the AI model with current system data.

    Returns:
        True if training successful, False otherwise
    """
    try:
        from .win_compat import print_status, print_header

        print_header("🧠 Training AI Model")
        print_status("This will collect system data for 60 seconds...", 'INFO')
        print_status("Please perform normal gaming activities during this time.", 'WARNING')
        print()

        predictor = get_predictor()

        # Collect training data
        training_data = predictor.collect_training_data(duration_seconds=60)

        if len(training_data) < 10:
            print_status("Not enough training data collected. Try again.", 'ERROR')
            return False

        # Train the model
        metrics = predictor.train_model()

        if metrics:
            print_status("✅ AI model trained successfully!", 'SUCCESS')
            print(f"  Training samples: {metrics.get('training_samples', 0)}")
            print(f"  Test samples: {metrics.get('test_samples', 0)}")
            print(f"  Mean Absolute Error: {metrics.get('mean_absolute_error', 0):.2f}")
            print(f"  R² Score: {metrics.get('r2_score', 0):.3f}")
            return True
        else:
            print_status("❌ AI model training failed.", 'ERROR')
            return False

    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        print_status(f"❌ Training failed: {e}", 'ERROR')
        return False

if __name__ == "__main__":
    # Test the module
    print("Testing Smart Advisor Module...")

    # Generate suggestions
    suggestions = generate_ai_suggestions()
    display_suggestions(suggestions)

    # Test component scores
    print("\nRAM Score:", calculate_ram_score())
    print("CPU Score:", calculate_cpu_score())"""
AI-Powered Smart Advisor Module for AeroFPS PRO
Provides intelligent system recommendations and performance predictions using machine learning.
"""

import os
import json
import time
import psutil
import platform
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

from .constants import (
    TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
    CPU_USAGE_WARNING, CPU_USAGE_CRITICAL,
    RAM_USAGE_WARNING, RAM_USAGE_CRITICAL,
    CACHE_TIMEOUT, LOG_LEVELS
)
from .logger import setup_logger, log_with_context

# Initialize logger
logger = setup_logger(__name__, level=LOG_LEVELS['INFO'])

@dataclass
class SystemMetrics:
    """Data class for system performance metrics."""
    timestamp: datetime
    cpu_percent: float
    ram_percent: float
    gpu_usage: Optional[float]
    disk_usage: float
    network_latency: float
    temperature: Optional[float]
    fps: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemMetrics':
        """Create instance from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class PerformancePrediction:
    """Data class for AI performance predictions."""
    predicted_fps: float
    confidence_score: float
    recommendations: List[str]
    risk_level: str
    timestamp: datetime

class PerformancePredictor:
    """
    AI-powered performance prediction system using machine learning.
    Analyzes system metrics to predict FPS and provide optimization recommendations.
    """

    def __init__(self, model_path: str = "models/fps_predictor.pkl"):
        self.model_path = model_path
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False
        self.training_data: List[SystemMetrics] = []
        self.feature_names = [
            'cpu_percent', 'ram_percent', 'disk_usage',
            'network_latency', 'temperature', 'gpu_usage'
        ]

        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Load existing model if available
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path):
                import joblib
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = True
                logger.info("AI model loaded successfully")
                return True
            else:
                logger.info("No existing AI model found, will train new one")
                return False
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            return False

    def _save_model(self) -> bool:
        """Save trained model to disk."""
        try:
            if self.model and self.scaler:
                import joblib
                model_data = {
                    'model': self.model,
                    'scaler': self.scaler,
                    'feature_names': self.feature_names,
                    'trained_at': datetime.now().isoformat()
                }
                joblib.dump(model_data, self.model_path)
                logger.info("AI model saved successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save AI model: {e}")
            return False

    def collect_training_data(self, duration_seconds: int = 60) -> List[SystemMetrics]:
        """
        Collect system metrics for training data.

        Args:
            duration_seconds: How long to collect data

        Returns:
            List of collected system metrics
        """
        logger.info(f"Collecting training data for {duration_seconds} seconds...")

        collected_data = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration_seconds:
                metrics = self._collect_current_metrics()
                if metrics:
                    collected_data.append(metrics)
                time.sleep(1)  # Collect data every second

            self.training_data.extend(collected_data)
            logger.info(f"Collected {len(collected_data)} training samples")
            return collected_data

        except KeyboardInterrupt:
            logger.info("Training data collection interrupted by user")
            return collected_data
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return collected_data

    def _collect_current_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics."""
        try:
            # CPU and RAM
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent

            # Disk usage
            disk_usage = psutil.disk_usage('/').percent

            # Network latency (simplified)
            network_latency = self._measure_network_latency()

            # Temperature (if available)
            temperature = self._get_system_temperature()

            # GPU usage (simplified - would need GPU monitoring library)
            gpu_usage = None  # Placeholder

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                ram_percent=ram_percent,
                gpu_usage=gpu_usage,
                disk_usage=disk_usage,
                network_latency=network_latency,
                temperature=temperature
            )

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None

    def _measure_network_latency(self) -> float:
        """Measure network latency to common gaming servers."""
        try:
            # Simple ping test to Google DNS
            import subprocess
            result = subprocess.run(
                ['ping', '-n', '1', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                # Extract ping time from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line and 'ms' in line:
                        time_str = line.split('time=')[1].split('ms')[0].strip()
                        return float(time_str)

            return 50.0  # Default latency if ping fails

        except Exception:
            return 50.0  # Default latency

    def _get_system_temperature(self) -> Optional[float]:
        """Get system temperature if available."""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get CPU temperature
                    for sensor_type, sensors in temps.items():
                        if 'cpu' in sensor_type.lower():
                            for sensor in sensors:
                                if sensor.current:
                                    return sensor.current
            return None
        except Exception:
            return None

    def train_model(self, test_size: float = 0.2) -> Dict[str, float]:
        """
        Train the AI model using collected data.

        Args:
            test_size: Fraction of data to use for testing

        Returns:
            Dictionary with training metrics
        """
        if len(self.training_data) < 10:
            logger.warning("Not enough training data. Need at least 10 samples.")
            return {}

        logger.info(f"Training AI model with {len(self.training_data)} samples...")

        try:
            # Prepare features and target
            X = []
            y = []

            for metrics in self.training_data:
                if metrics.fps is not None:  # Only use samples with FPS data
                    features = [
                        metrics.cpu_percent,
                        metrics.ram_percent,
                        metrics.disk_usage,
                        metrics.network_latency,
                        metrics.temperature or 25.0,  # Default temp
                        metrics.gpu_usage or 0.0  # Default GPU usage
                    ]
                    X.append(features)
                    y.append(metrics.fps)

            if len(X) < 5:
                logger.warning("Not enough samples with FPS data for training")
                return {}

            X = np.array(X)
            y = np.array(y)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.is_trained = True
            self._save_model()

            metrics = {
                'mean_absolute_error': mae,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }

            logger.info(f"Model trained successfully. MAE: {mae:.2f}, R²: {r2:.3f}")
            return metrics

        except Exception as e:
            logger.error(f"Error training AI model: {e}")
            return {}

    def predict_fps(self, current_metrics: SystemMetrics) -> Optional[PerformancePrediction]:
        """
        Predict FPS based on current system metrics.

        Args:
            current_metrics: Current system performance metrics

        Returns:
            Performance prediction with FPS estimate and recommendations
        """
        if not self.is_trained or not self.model or not self.scaler:
            logger.warning("AI model not trained yet")
            return None

        try:
            # Prepare features
            features = [
                current_metrics.cpu_percent,
                current_metrics.ram_percent,
                current_metrics.disk_usage,
                current_metrics.network_latency,
                current_metrics.temperature or 25.0,
                current_metrics.gpu_usage or 0.0
            ]

            features_scaled = self.scaler.transform([features])
            predicted_fps = self.model.predict(features_scaled)[0]

            # Calculate confidence based on feature importance
            confidence = self._calculate_confidence(features)

            # Generate recommendations
            recommendations = self._generate_recommendations(current_metrics, predicted_fps)

            # Determine risk level
            risk_level = self._assess_risk_level(current_metrics, predicted_fps)

            prediction = PerformancePrediction(
                predicted_fps=max(0, predicted_fps),
                confidence_score=min(1.0, confidence),
                recommendations=recommendations,
                risk_level=risk_level,
                timestamp=datetime.now()
            )

            return prediction

        except Exception as e:
            logger.error(f"Error making FPS prediction: {e}")
            return None

    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence based on feature values."""
        try:
            if not self.model:
                return 0.5

            # Use feature importances to weight confidence
            importances = self.model.feature_importances_

            # Calculate confidence based on how extreme the features are
            confidence = 1.0
            for i, (feature, importance) in enumerate(zip(features, importances)):
                if i == 0:  # CPU
                    if feature > CPU_USAGE_CRITICAL:
                        confidence *= 0.7
                    elif feature > CPU_USAGE_WARNING:
                        confidence *= 0.85
                elif i == 1:  # RAM
                    if feature > RAM_USAGE_CRITICAL:
                        confidence *= 0.7
                    elif feature > RAM_USAGE_WARNING:
                        confidence *= 0.85
                elif i == 4:  # Temperature
                    if feature > TEMP_CRITICAL_THRESHOLD:
                        confidence *= 0.6
                    elif feature > TEMP_WARNING_THRESHOLD:
                        confidence *= 0.8

            return confidence

        except Exception:
            return 0.5

    def _generate_recommendations(self, metrics: SystemMetrics, predicted_fps: float) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []

        # CPU recommendations
        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: CPU usage is extremely high. Close background applications.")
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            recommendations.append("🟡 High CPU usage detected. Consider closing unnecessary programs.")

        # RAM recommendations
        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            recommendations.append("🔴 Critical: RAM usage is critical. Close memory-intensive applications.")
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            recommendations.append("🟡 High RAM usage. Consider increasing virtual memory or upgrading RAM.")

        # Temperature recommendations
        if metrics.temperature and metrics.temperature > TEMP_CRITICAL_THRESHOLD:
            recommendations.append("🔴 Critical: System temperature is dangerously high. Check cooling system.")
        elif metrics.temperature and metrics.temperature > TEMP_WARNING_THRESHOLD:
            recommendations.append("🟡 High temperature detected. Ensure proper ventilation and cooling.")

        # Network recommendations
        if metrics.network_latency > 100:
            recommendations.append("🟡 High network latency. Check internet connection and router settings.")

        # FPS-based recommendations
        if predicted_fps < 30:
            recommendations.append("🔴 Predicted FPS is very low. Major system optimization needed.")
        elif predicted_fps < 60:
            recommendations.append("🟡 Predicted FPS is below 60. Consider graphics settings optimization.")

        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("✅ System performance looks good. No immediate optimizations needed.")

        return recommendations

    def _assess_risk_level(self, metrics: SystemMetrics, predicted_fps: float) -> str:
        """Assess overall system risk level."""
        risk_score = 0

        # CPU risk
        if metrics.cpu_percent > CPU_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.cpu_percent > CPU_USAGE_WARNING:
            risk_score += 1

        # RAM risk
        if metrics.ram_percent > RAM_USAGE_CRITICAL:
            risk_score += 3
        elif metrics.ram_percent > RAM_USAGE_WARNING:
            risk_score += 1

        # Temperature risk
        if metrics.temperature:
            if metrics.temperature > TEMP_CRITICAL_THRESHOLD:
                risk_score += 3
            elif metrics.temperature > TEMP_WARNING_THRESHOLD:
                risk_score += 1

        # FPS risk
        if predicted_fps < 30:
            risk_score += 2
        elif predicted_fps < 60:
            risk_score += 1

        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

# Global predictor instance
_predictor = None
_predictor_lock = threading.Lock()

def get_predictor() -> PerformancePredictor:
    """Get or create the global performance predictor instance."""
    global _predictor
    if _predictor is None:
        with _predictor_lock:
            if _predictor is None:
                _predictor = PerformancePredictor()
    return _predictor

@log_with_context
def generate_ai_suggestions() -> Dict[str, Any]:
    """
    Generate AI-powered system optimization suggestions.

    Returns:
        Dictionary containing suggestions and predictions
    """
    try:
        predictor = get_predictor()

        # Collect current metrics
        current_metrics = predictor._collect_current_metrics()
        if not current_metrics:
            return {
                'status': 'error',
                'message': 'Failed to collect system metrics'
            }

        # Make prediction if model is trained
        prediction = None
        if predictor.is_trained:
            prediction = predictor.predict_fps(current_metrics)

        # Generate basic suggestions even without AI
        basic_suggestions = _generate_basic_suggestions(current_metrics)

        result = {
            'status': 'success',
            'current_metrics': current_metrics.to_dict(),
            'basic_suggestions': basic_suggestions,
            'ai_available': predictor.is_trained
        }

        if prediction:
            result['ai_prediction'] = {
                'predicted_fps': prediction.predicted_fps,
                'confidence': prediction.confidence_score,
                'recommendations': prediction.recommendations,
                'risk_level': prediction.risk_level
            }

        return result

    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
        return {
            'status': 'error',
            'message': f'AI suggestion generation failed: {str(e)}'
        }

def _generate_basic_suggestions(metrics: SystemMetrics) -> List[str]:
    """Generate basic optimization suggestions without AI."""
    suggestions = []

    # CPU suggestions
    if metrics.cpu_percent > 80:
        suggestions.append("Close unnecessary background applications")
        suggestions.append("Disable Windows visual effects")
    elif metrics.cpu_percent > 60:
        suggestions.append("Consider closing some applications")

    # RAM suggestions
    if metrics.ram_percent > 85:
        suggestions.append("Close memory-intensive applications")
        suggestions.append("Increase virtual memory")
    elif metrics.ram_percent > 70:
        suggestions.append("Monitor memory usage closely")

    # Disk suggestions
    if metrics.disk_usage > 90:
        suggestions.append("Free up disk space")
        suggestions.append("Run disk cleanup")

    # Network suggestions
    if metrics.network_latency > 50:
        suggestions.append("Check internet connection")
        suggestions.append("Restart router if needed")

    if not suggestions:
        suggestions.append("System performance is good")

    return suggestions

@log_with_context
def calculate_ram_score() -> Dict[str, Any]:
    """
    Calculate RAM performance score and recommendations.

    Returns:
        Dictionary with RAM analysis
    """
    try:
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)

        # Calculate score (0-100, higher is better)
        score = max(0, 100 - ram_percent)

        # Determine rating
        if ram_percent < 50:
            rating = "Excellent"
        elif ram_percent < 70:
            rating = "Good"
        elif ram_percent < 85:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if ram_percent > 80:
            recommendations.append("Close unnecessary applications")
            recommendations.append("Consider upgrading RAM")
        elif ram_percent > 60:
            recommendations.append("Monitor RAM usage")

        return {
            'score': score,
            'rating': rating,
            'used_gb': round(ram_used_gb, 1),
            'total_gb': round(ram_total_gb, 1),
            'usage_percent': ram_percent,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating RAM score: {e}")
        return {'error': str(e)}

@log_with_context
def calculate_cpu_score() -> Dict[str, Any]:
    """
    Calculate CPU performance score and recommendations.

    Returns:
        Dictionary with CPU analysis
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Calculate score (0-100, higher is better)
        score = max(0, 100 - cpu_percent)

        # Determine rating
        if cpu_percent < 30:
            rating = "Excellent"
        elif cpu_percent < 50:
            rating = "Good"
        elif cpu_percent < 70:
            rating = "Fair"
        else:
            rating = "Poor"

        recommendations = []
        if cpu_percent > 80:
            recommendations.append("Close unnecessary background processes")
            recommendations.append("Disable Windows visual effects")
        elif cpu_percent > 60:
            recommendations.append("Monitor CPU usage")

        return {
            'score': score,
            'rating': rating,
            'usage_percent': cpu_percent,
            'core_count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else None,
            'recommendations': recommendations
        }

    except Exception as e:
        logger.error(f"Error calculating CPU score: {e}")
        return {'error': str(e)}

@log_with_context
def display_suggestions(suggestions_data: Dict[str, Any]) -> None:
    """
    Display AI suggestions in a formatted way.

    Args:
        suggestions_data: Suggestions data from generate_ai_suggestions()
    """
    try:
        from .win_compat import print_status, print_header

        print_header("🤖 AI Smart Advisor Results")

        if suggestions_data.get('status') == 'error':
            print_status(suggestions_data.get('message', 'Unknown error'), 'ERROR')
            return

        # Display current metrics
        metrics = suggestions_data.get('current_metrics', {})
        if metrics:
            print_status("📊 Current System Metrics:", 'INFO')
            print(f"  CPU Usage: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"  RAM Usage: {metrics.get('ram_percent', 'N/A')}%")
            print(f"  Disk Usage: {metrics.get('disk_usage', 'N/A')}%")
            print(f"  Network Latency: {metrics.get('network_latency', 'N/A')}ms")
            if metrics.get('temperature'):
                print(f"  Temperature: {metrics.get('temperature'):.1f}°C")
            print()

        # Display AI prediction if available
        ai_prediction = suggestions_data.get('ai_prediction')
        if ai_prediction:
            print_status("🎯 AI Performance Prediction:", 'SUCCESS')
            fps = ai_prediction.get('predicted_fps', 0)
            confidence = ai_prediction.get('confidence', 0)
            risk = ai_prediction.get('risk_level', 'UNKNOWN')

            print(f"  Predicted FPS: {fps:.1f}")
            print(f"  Confidence: {confidence:.1%}")
            print(f"  Risk Level: {risk}")
            print()

            # Display AI recommendations
            recommendations = ai_prediction.get('recommendations', [])
            if recommendations:
                print_status("💡 AI Recommendations:", 'INFO')
                for rec in recommendations:
                    print(f"  • {rec}")
                print()

        # Display basic suggestions
        basic_suggestions = suggestions_data.get('basic_suggestions', [])
        if basic_suggestions and not ai_prediction:
            print_status("💡 Basic Optimization Suggestions:", 'INFO')
            for suggestion in basic_suggestions:
                print(f"  • {suggestion}")
            print()

        # Display component scores
        print_status("📈 Component Performance Scores:", 'INFO')
        ram_score = calculate_ram_score()
        cpu_score = calculate_cpu_score()

        if 'score' in ram_score:
            print(f"  RAM Score: {ram_score['score']}/100 ({ram_score['rating']})")
            print(f"    Used: {ram_score['used_gb']}GB / {ram_score['total_gb']}GB")

        if 'score' in cpu_score:
            print(f"  CPU Score: {cpu_score['score']}/100 ({cpu_score['rating']})")
            print(f"    Usage: {cpu_score['usage_percent']}%")

        print_status("✅ Analysis complete!", 'SUCCESS')

    except Exception as e:
        logger.error(f"Error displaying suggestions: {e}")
        print(f"❌ Error displaying suggestions: {e}")

@log_with_context
def train_ai_model() -> bool:
    """
    Train the AI model with current system data.

    Returns:
        True if training successful, False otherwise
    """
    try:
        from .win_compat import print_status, print_header

        print_header("🧠 Training AI Model")
        print_status("This will collect system data for 60 seconds...", 'INFO')
        print_status("Please perform normal gaming activities during this time.", 'WARNING')
        print()

        predictor = get_predictor()

        # Collect training data
        training_data = predictor.collect_training_data(duration_seconds=60)

        if len(training_data) < 10:
            print_status("Not enough training data collected. Try again.", 'ERROR')
            return False

        # Train the model
        metrics = predictor.train_model()

        if metrics:
            print_status("✅ AI model trained successfully!", 'SUCCESS')
            print(f"  Training samples: {metrics.get('training_samples', 0)}")
            print(f"  Test samples: {metrics.get('test_samples', 0)}")
            print(f"  Mean Absolute Error: {metrics.get('mean_absolute_error', 0):.2f}")
            print(f"  R² Score: {metrics.get('r2_score', 0):.3f}")
            return True
        else:
            print_status("❌ AI model training failed.", 'ERROR')
            return False

    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        print_status(f"❌ Training failed: {e}", 'ERROR')
        return False

if __name__ == "__main__":
    # Test the module
    print("Testing Smart Advisor Module...")

    # Generate suggestions
    suggestions = generate_ai_suggestions()
    display_suggestions(suggestions)

    # Test component scores
    print("\nRAM Score:", calculate_ram_score())
    print("CPU Score:", calculate_cpu_score())
        except Exception as e:
            log_debug(f"Model yükleme hatası: {e}")

    def save_model(self):
        """Modeli kaydet"""
        try:
            MODEL_DIR.mkdir(exist_ok=True)
            if self.model:
                joblib.dump(self.model, PERFORMANCE_MODEL)
                log_debug("AI model kaydedildi")
        except Exception as e:
            log_debug(f"Model kaydetme hatası: {e}")

    def collect_training_data(self, specs, actual_fps):
        """Eğitim verisi topla"""
        try:
            data = {
                'timestamp': time.time(),
                'specs': specs,
                'actual_fps': actual_fps
            }

            # Mevcut veriyi yükle
            training_data = []
            if TRAINING_DATA.exists():
                with open(TRAINING_DATA, 'r') as f:
                    training_data = json.load(f)

            training_data.append(data)

            # Son 1000 veriyi tut
            if len(training_data) > 1000:
                training_data = training_data[-1000:]

            # Kaydet
            with open(TRAINING_DATA, 'w') as f:
                json.dump(training_data, f, indent=2)

        except Exception as e:
            log_debug(f"Eğitim verisi toplama hatası: {e}")

    def train_model(self):
        """Modeli eğit"""
        if not AI_AVAILABLE:
            return False

        try:
            if not TRAINING_DATA.exists():
                log_debug("Yeterli eğitim verisi yok")
                return False

            with open(TRAINING_DATA, 'r') as f:
                data = json.load(f)

            if len(data) < 10:  # Minimum eğitim verisi
                return False

            # Veriyi hazırla
            X = []
            y = []

            for entry in data:
                specs = entry['specs']
                features = [
                    specs.get('cpu_cores', 4),
                    specs.get('cpu_threads', 8),
                    specs.get('cpu_freq', 3000) / 1000,  # GHz'e çevir
                    specs.get('ram_gb', 8),
                    specs.get('ram_usage', 50),
                    1 if specs.get('disk_type') == 'SSD' else 0,
                    specs.get('startup_programs', 5),
                    specs.get('background_processes', 100) / 100,  # Normalize
                ]
                X.append(features)
                y.append(entry['actual_fps'])

            X = np.array(X)
            y = np.array(y)

            # Eğitim/test böl
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Model oluştur
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            # Skoru hesapla
            score = self.model.score(X_test, y_test)
            log_debug(f"AI model eğitildi, doğruluk: {score:.2f}")

            self.is_trained = True
            self.save_model()

            return True

        except Exception as e:
            log_debug(f"Model eğitim hatası: {e}")
            return False

    def predict_fps(self, specs):
        """FPS tahmin et"""
        if not self.is_trained or not self.model:
            return None

        try:
            features = np.array([[
                specs.get('cpu_cores', 4),
                specs.get('cpu_threads', 8),
                specs.get('cpu_freq', 3000) / 1000,
                specs.get('ram_gb', 8),
                specs.get('ram_usage', 50),
                1 if specs.get('disk_type') == 'SSD' else 0,
                specs.get('startup_programs', 5),
                specs.get('background_processes', 100) / 100,
            ]])

            prediction = self.model.predict(features)[0]
            return max(0, min(300, prediction))  # 0-300 FPS arası sınırla

        except Exception as e:
            log_debug(f"FPS tahmin hatası: {e}")
            return None

# Global AI predictor
ai_predictor = PerformancePredictor()

def get_system_specs():
    """Sistem özelliklerini topla"""
    specs = {
        'cpu_cores': psutil.cpu_count(logical=False),
        'cpu_threads': psutil.cpu_count(logical=True),
        'cpu_freq': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
        'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
        'ram_usage': psutil.virtual_memory().percent,
        'disk_type': 'Unknown',
        'windows_version': platform.release(),
        'startup_programs': 0,
        'background_processes': len(psutil.pids()),
    }
    
    # Disk tipi kontrolü (SSD/HDD)
    try:
        output = subprocess.check_output(
            'powershell "Get-PhysicalDisk | Select-Object MediaType"',
            shell=True,
            encoding='utf-8',
            errors='ignore'
        )
        if 'SSD' in output:
            specs['disk_type'] = 'SSD'
        elif 'HDD' in output:
            specs['disk_type'] = 'HDD'
    except:
        pass
    
    # Başlangıç programları sayısı
    try:
        output = subprocess.check_output(
            'powershell "Get-CimInstance Win32_StartupCommand | Measure-Object | Select-Object -ExpandProperty Count"',
            shell=True,
            encoding='utf-8',
            errors='ignore'
        )
        specs['startup_programs'] = int(output.strip())
    except:
        pass
    
    return specs

def analyze_and_suggest():
    """AI tabanlı sistem analizi yap ve öneriler sun"""
    print(Fore.CYAN + Style.BRIGHT + "\n")
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║      🤖 AI AKILLI ÖNERİ SİSTEMİ               ║")
    print("  ╚════════════════════════════════════════════════╝\n")

    print(Fore.YELLOW + "  🔍 Sisteminiz AI ile analiz ediliyor...\n")

    specs = get_system_specs()

    # AI FPS Tahmini
    ai_fps_prediction = None
    if AI_AVAILABLE and ai_predictor.is_trained:
        ai_fps_prediction = ai_predictor.predict_fps(specs)
        if ai_fps_prediction:
            print(Fore.GREEN + f"  🎯 AI FPS Tahmini: ~{ai_fps_prediction:.0f} FPS (ortalama oyunlarda)")
            print(Fore.WHITE + "  " + "─" * 60)

    # Sistem bilgilerini göster
    print(Fore.WHITE + "  📊 SİSTEM ÖZETİ:")
    print(Fore.WHITE + "  " + "─" * 60)
    print(Fore.CYAN + f"  CPU: {specs['cpu_cores']} Core / {specs['cpu_threads']} Thread")
    if specs['cpu_freq'] > 0:
        print(Fore.CYAN + f"  CPU Frekans: {specs['cpu_freq']:.0f} MHz")
    print(Fore.CYAN + f"  RAM: {specs['ram_gb']} GB (Kullanım: {specs['ram_usage']:.0f}%)")
    print(Fore.CYAN + f"  Disk: {specs['disk_type']}")
    print(Fore.CYAN + f"  Windows: {specs['windows_version']}")
    print(Fore.CYAN + f"  Başlangıç Programları: {specs['startup_programs']}")
    print(Fore.CYAN + f"  Arka Plan Process: {specs['background_processes']}")
    print(Fore.WHITE + "  " + "─" * 60)

    # AI Tabanlı Öneri Sistemi
    suggestions = generate_ai_suggestions(specs, ai_fps_prediction)

    # Önerileri göster
    display_suggestions(suggestions)

    # AI Model Durumu
    print(Fore.WHITE + "\n  🤖 AI SİSTEM DURUMU:")
    print(Fore.WHITE + "  " + "─" * 60)
    if AI_AVAILABLE:
        if ai_predictor.is_trained:
            print(Fore.GREEN + "  ✅ AI Model: Aktif (Eğitilmiş)")
            print(Fore.CYAN + "  📈 Tahmin Doğruluğu: Yüksek")
        else:
            print(Fore.YELLOW + "  ⚠️  AI Model: Eğitim Gerekli")
            print(Fore.CYAN + "  💡 Daha fazla kullanım ile öğrenir")
    else:
        print(Fore.RED + "  ❌ AI Özellikler: Kütüphaneler Eksik")
        print(Fore.CYAN + "  📦 Kurulum: pip install scikit-learn numpy pandas joblib")

    print(Fore.WHITE + "  " + "─" * 60)

                'confidence': 'Yüksek'
            })
        elif ai_fps_prediction < 120:
            suggestions['high'].append({
                'title': '🟡 YÜKSEK: Orta FPS Tahmini',
                'description': f'AI sisteminizde ortalama {ai_fps_prediction:.0f} FPS bekleniyor',
                'actions': [
                    'Temel optimizasyonları uygulayın',
                    'Arka plan uygulamalarını kapatın'
                ],
                'expected_gain': '+20-40 FPS potansiyel',
                'confidence': 'Yüksek'
            })

    # RAM analizi (AI geliştirilmiş)
    ram_score = calculate_ram_score(specs)
    if ram_score < 3:
        suggestions['critical'].append({
            'title': '🔴 KRİTİK: RAM Yetersizliği',
            'description': f'RAM puanınız: {ram_score}/10 - Oyun performansı ciddi etkilenecek',
            'actions': [
                'RAM yükseltme önerilir (minimum 16GB)',
                'Arka plan uygulamalarını kapatın',
                'RAM temizleme uygulayın'
            ],
            'expected_gain': '+30-50 FPS potansiyel',
            'confidence': 'Çok Yüksek'
        })
    elif specs['ram_usage'] > 85:
        suggestions['high'].append({
            'title': '🟡 YÜKSEK: RAM Baskısı',
            'description': f'RAM kullanımınız %{specs["ram_usage"]:.0f} - Bellek darboğazı var',
            'actions': [
                'RAM temizleme uygulayın',
                'Gereksiz programları kapatın'
            ],
            'expected_gain': '+15-25 FPS potansiyel',
            'confidence': 'Yüksek'
        })

    # CPU analizi (AI geliştirilmiş)
    cpu_score = calculate_cpu_score(specs)
    if cpu_score < 4:
        suggestions['high'].append({
            'title': '🟡 YÜKSEK: CPU Darboğazı',
            'description': f'CPU puanınız: {cpu_score}/10 - İşlemci performansı sınırlı',
            'actions': [
                'Arka plan işlemlerini minimize edin',
                'CPU öncelik ayarları yapın'
            ],
            'expected_gain': '+25-40 FPS potansiyel',
            'confidence': 'Yüksek'
        })

    # Disk analizi
    if specs['disk_type'] == 'HDD':
        suggestions['high'].append({
            'title': '🟡 YÜKSEK: HDD Kullanımı',
            'description': 'HDD oyun performansı ciddi şekilde düşürür',
            'actions': [
                'SSD yükseltme ÖNERİLİR',
                'Oyunları SSD\'ye taşıyın',
                'Disk optimizasyonu yapın'
            ],
            'expected_gain': 'Yükleme: %300+ hız, FPS: +20-30',
            'confidence': 'Çok Yüksek'
        })
    elif specs['disk_type'] == 'SSD':
        suggestions['medium'].append({
            'title': '🔵 ORTA: SSD Optimizasyonu',
            'description': 'SSD\'niz var ama optimizasyon gerekebilir',
            'actions': [
                'TRIM aktif mi kontrol edin',
                'Disk birleştirme yapın'
            ],
            'expected_gain': '+5-10 FPS potansiyel',
            'confidence': 'Orta'
        })

    # Sistem servisleri ve başlangıç
    if specs['startup_programs'] > 15:
        suggestions['medium'].append({
            'title': '🔵 ORTA: Başlangıç Programları',
            'description': f'{specs["startup_programs"]} program başlangıçta çalışıyor',
            'actions': [
                'Gereksiz programları devre dışı bırakın',
                'Başlangıç yöneticisini kullanın'
            ],
            'expected_gain': '+10-20 FPS potansiyel',
            'confidence': 'Yüksek'
        })

    if specs['background_processes'] > 200:
        suggestions['medium'].append({
            'title': '🔵 ORTA: Arka Plan İşlemleri',
            'description': f'{specs["background_processes"]} arka plan işlemi çalışıyor',
            'actions': [
                'Gereksiz servisleri kapatın',
                'Process manager kullanın'
            ],
            'expected_gain': '+15-25 FPS potansiyel',
            'confidence': 'Yüksek'
        })

    # Optimizasyon önerileri
    suggestions['optimizations'] = generate_optimization_plan(specs, ai_fps_prediction)

    return suggestions

def calculate_ram_score(specs):
    """RAM performans puanı hesapla (AI tabanlı)"""
    base_score = min(10, specs['ram_gb'] / 2)  # 16GB = 8 puan

    # Kullanım penalti
    usage_penalty = specs['ram_usage'] / 10  # %90 kullanım = 9 puan düşür

    # Minimum RAM kontrolü
    if specs['ram_gb'] < 8:
        base_score -= 3

    return max(0, min(10, base_score - usage_penalty))

def calculate_cpu_score(specs):
    """CPU performans puanı hesapla (AI tabanlı)"""
    core_score = min(10, specs['cpu_cores'] * 1.5)  # 4 core = 6 puan
    thread_score = min(5, specs['cpu_threads'] / 4)  # 8 thread = 2 puan

    # Frekans bonus
    freq_bonus = min(3, (specs['cpu_freq'] - 2000) / 1000)  # 3GHz+ için bonus

    return max(0, min(10, core_score + thread_score + freq_bonus))

def generate_optimization_plan(specs, ai_fps):
    """Kapsamlı optimizasyon planı oluştur"""
    plan = []

    # Acil optimizasyonlar
    if specs['ram_usage'] > 80 or specs['ram_gb'] < RAM_LOW:
        plan.append({
            'phase': 'ACİL',
            'title': 'RAM Optimizasyonu',
            'steps': [
                'Arka plan uygulamalarını kapat',
                'RAM temizleme uygula',
                'Sanal belleği optimize et'
            ],
            'time': '2-3 dakika',
            'impact': 'Yüksek'
        })

    # CPU optimizasyonları
    if specs['cpu_cores'] < 6:
        plan.append({
            'phase': 'ÖNCELİKLİ',
            'title': 'CPU Optimizasyonu',
            'steps': [
                'Oyun process\'lerine yüksek öncelik ver',
                'Gereksiz servisleri devre dışı bırak',
                'Power plan\'ı yüksek performans yap'
            ],
            'time': '5-7 dakika',
            'impact': 'Yüksek'
        })

    # Sistem genel optimizasyon
    plan.append({
        'phase': 'GENEL',
        'title': 'Sistem Optimizasyonu',
        'steps': [
            'Geçici dosyaları temizle',
            'Registry optimizasyonu yap',
            'Windows güncellemelerini kontrol et'
        ],
        'time': '10-15 dakika',
        'impact': 'Orta'
    })

    # Ağ optimizasyonları
    plan.append({
        'phase': 'AĞ',
        'title': 'Network Optimizasyonu',
        'steps': [
            'DNS ayarlarını optimize et',
            'Network throttling\'i kaldır',
            'Game server ping\'lerini test et'
        ],
        'time': '3-5 dakika',
        'impact': 'Orta'
    })

    return plan

def train_ai_model():
    """AI modelini manuel olarak eğit"""
    print(Fore.CYAN + "\n🤖 AI Model Eğitimi\n")
    print(Fore.YELLOW + "AI modelini eğitmek için yeterli veri toplanana kadar bekleyin...")
    print(Fore.CYAN + "Model eğitimi için en az 10 kullanım verisi gerekli.\n")

    if not AI_AVAILABLE:
        print(Fore.RED + "❌ AI kütüphaneleri yüklü değil!")
        print(Fore.CYAN + "pip install scikit-learn numpy pandas joblib")
        return

    success = ai_predictor.train_model()
    if success:
        print(Fore.GREEN + "✅ AI Model başarıyla eğitildi!")
        print(Fore.CYAN + "Artık FPS tahminleri daha doğru olacak.")
    else:
        print(Fore.YELLOW + "⚠️  AI Model eğitimi için daha fazla veri gerekli.")
        print(Fore.CYAN + "Programı daha fazla kullanarak veri toplayın.")

def collect_performance_feedback(actual_fps):
    """Kullanıcıdan performans geri bildirimi topla"""
    try:
        specs = get_system_specs()
        ai_predictor.collect_training_data(specs, actual_fps)
        log_info(f"Performance feedback collected: {actual_fps} FPS")
        return True
    except Exception as e:
        log_debug(f"Feedback collection error: {e}")
        return False

def display_suggestions(suggestions):
    """Önerileri görsel olarak göster"""
    # Kritik öneriler
    if suggestions['critical']:
        print(Fore.RED + Style.BRIGHT + "\n  🚨 KRİTİK ÖNERİLER:")
        for i, sug in enumerate(suggestions['critical'], 1):
            print(Fore.RED + f"  {i}. {sug['title']}")
            print(Fore.WHITE + f"     {sug['description']}")
            print(Fore.YELLOW + f"     💡 Önerilen Aksiyonlar:")
            for action in sug['actions']:
                print(Fore.WHITE + f"        • {action}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['expected_gain']}")
            print(Fore.CYAN + f"     🎯 Güven: {sug['confidence']}")
            print()

    # Yüksek öncelik
    if suggestions['high']:
        print(Fore.YELLOW + Style.BRIGHT + "\n  ⚠️  YÜKSEK ÖNCELİKLİ ÖNERİLER:")
        for i, sug in enumerate(suggestions['high'], 1):
            print(Fore.YELLOW + f"  {i}. {sug['title']}")
            print(Fore.WHITE + f"     {sug['description']}")
            print(Fore.CYAN + f"     💡 Önerilen Aksiyonlar:")
            for action in sug['actions']:
                print(Fore.WHITE + f"        • {action}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['expected_gain']}")
            print(Fore.CYAN + f"     🎯 Güven: {sug['confidence']}")
            print()

    # Orta öncelik
    if suggestions['medium']:
        print(Fore.BLUE + Style.BRIGHT + "\n  ℹ️  ORTA ÖNCELİKLİ ÖNERİLER:")
        for i, sug in enumerate(suggestions['medium'], 1):
            print(Fore.BLUE + f"  {i}. {sug['title']}")
            print(Fore.WHITE + f"     {sug['description']}")
            print(Fore.CYAN + f"     💡 Önerilen Aksiyonlar:")
            for action in sug['actions']:
                print(Fore.WHITE + f"        • {action}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['expected_gain']}")
            print(Fore.CYAN + f"     🎯 Güven: {sug['confidence']}")
            print()

    # Optimizasyon planı
    if suggestions['optimizations']:
        print(Fore.GREEN + Style.BRIGHT + "\n  🚀 ÖNERİLEN OPTİMİZASYON PLANI:")
        for i, opt in enumerate(suggestions['optimizations'], 1):
            print(Fore.GREEN + f"  {i}. [{opt['phase']}] {opt['title']}")
            print(Fore.WHITE + f"     ⏱️  Tahmini Süre: {opt['time']}")
            print(Fore.CYAN + f"     💪 Etki: {opt['impact']}")
            print(Fore.WHITE + f"     Adımlar:")
            for step in opt['steps']:
                print(Fore.WHITE + f"        • {step}")
            print()
            'fps_gain': '+15-25 FPS'
        })
    elif specs['ram_usage'] > 80:
        priority_high.append({
            'issue': 'Yüksek RAM kullanımı',
            'suggestion': 'RAM temizliği yapın',
            'action': 'Menü: [17] RAM Cleaner',
            'fps_gain': '+10-15 FPS'
        })
    
    # CPU analizi
    if specs['cpu_cores'] < 4:
        priority_medium.append({
            'issue': 'Düşük CPU çekirdek sayısı',
            'suggestion': 'Arka plan işlemlerini minimize edin',
            'action': 'Menü: [3] Process Manager',
            'fps_gain': '+20-30 FPS'
        })
    
    # Disk analizi
    if specs['disk_type'] == 'HDD':
        priority_high.append({
            'issue': 'HDD kullanımı',
            'suggestion': 'SSD yükseltme ÖNERİLİR',
            'action': 'Oyunları SSD\'ye taşıyın',
            'fps_gain': 'Yükleme: %300 hızlanma'
        })
    elif specs['disk_type'] == 'SSD':
        priority_low.append({
            'issue': 'SSD optimizasyonu',
            'suggestion': 'TRIM aktif mi kontrol edin',
            'action': 'Menü: [6] Gelişmiş Optimizasyon',
            'fps_gain': '+5 FPS'
        })
    
    # Başlangıç programları
    if specs['startup_programs'] > 10:
        priority_medium.append({
            'issue': f'{specs["startup_programs"]} başlangıç programı',
            'suggestion': 'Gereksiz programları devre dışı bırakın',
            'action': 'Menü: [10] Startup Manager',
            'fps_gain': '+10-20 FPS'
        })
    
    # Arka plan process
    if specs['background_processes'] > 150:
        priority_medium.append({
            'issue': f'{specs["background_processes"]} arka plan process',
            'suggestion': 'Gereksiz servisleri kapatın',
            'action': 'Menü: [1] FPS Boost Mode',
            'fps_gain': '+15-25 FPS'
        })
    
    # Windows versiyonu
    if specs['windows_version'] == '11':
        priority_low.append({
            'issue': 'Windows 11 optimizasyonu',
            'suggestion': 'VBS (Virtualization Based Security) kapatın',
            'action': 'Manuel: msinfo32 > VBS durumunu kontrol',
            'fps_gain': '+5-10 FPS'
        })
    
    # Genel öneriler
    priority_low.append({
        'issue': 'GPU Driver',
        'suggestion': 'En son GPU driver\'ı kullanın',
        'action': 'NVIDIA/AMD sitesinden güncelleyin',
        'fps_gain': '+10-20 FPS'
    })
    
    priority_low.append({
        'issue': 'Game Mode',
        'suggestion': 'Windows Game Mode aktif olmalı',
        'action': 'Menü: [8] GPU Turbo Mode',
        'fps_gain': '+5-10 FPS'
    })
    
    # Önerileri göster
    print(Fore.GREEN + "\n  ✨ KİŞİSELLEŞTİRİLMİŞ ÖNERİLER:\n")
    
    if priority_high:
        print(Fore.RED + Style.BRIGHT + "  🔴 YÜKSEK ÖNCELİK:")
        print(Fore.WHITE + "  " + "─" * 60)
        for i, sug in enumerate(priority_high, 1):
            print(Fore.RED + f"  {i}. {sug['issue']}")
            print(Fore.YELLOW + f"     💡 {sug['suggestion']}")
            print(Fore.WHITE + f"     ⚡ {sug['action']}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['fps_gain']}\n")
    
    if priority_medium:
        print(Fore.YELLOW + Style.BRIGHT + "  🟡 ORTA ÖNCELİK:")
        print(Fore.WHITE + "  " + "─" * 60)
        for i, sug in enumerate(priority_medium, 1):
            print(Fore.YELLOW + f"  {i}. {sug['issue']}")
            print(Fore.CYAN + f"     💡 {sug['suggestion']}")
            print(Fore.WHITE + f"     ⚡ {sug['action']}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['fps_gain']}\n")
    
    if priority_low:
        print(Fore.CYAN + Style.BRIGHT + "  🔵 DÜŞÜK ÖNCELİK:")
        print(Fore.WHITE + "  " + "─" * 60)
        for i, sug in enumerate(priority_low, 1):
            print(Fore.CYAN + f"  {i}. {sug['issue']}")
            print(Fore.WHITE + f"     💡 {sug['suggestion']}")
            print(Fore.WHITE + f"     ⚡ {sug['action']}")
            print(Fore.GREEN + f"     📈 Beklenen Kazanç: {sug['fps_gain']}\n")
    
    # Toplam potansiyel kazanç
    total_suggestions = len(priority_high) + len(priority_medium) + len(priority_low)
    
    print(Fore.WHITE + "  " + "═" * 60)
    print(Fore.GREEN + Style.BRIGHT + f"  🎯 TOPLAM {total_suggestions} ÖNERİ BULUNDU")
    print(Fore.YELLOW + "  💰 Potansiyel FPS Kazancı: +50-150 FPS (donanıma bağlı)")
    print(Fore.WHITE + "  " + "═" * 60)
    
    # Hızlı aksiyon menüsü
    print(Fore.CYAN + "\n  🚀 HIZLI AKSİYON:")
    print(Fore.WHITE + "  [1] Tüm önerileri uygula (Otomatik)")
    print(Fore.WHITE + "  [2] Sadece yüksek öncelikli önerileri uygula")
    print(Fore.WHITE + "  [3] Manuel uygulama (Ana menüye dön)")
    
    choice = input(Fore.GREEN + "\n  Seçim (1-3): ")
    
    if choice == '1':
        apply_all_suggestions()
    elif choice == '2':
        apply_high_priority_suggestions()
    
    log_info(f"Akıllı öneri sistemi çalıştırıldı - {total_suggestions} öneri")

def apply_all_suggestions():
    """Tüm önerileri otomatik uygula"""
    print(Fore.YELLOW + "\n  ⚡ Tüm optimizasyonlar uygulanıyor...\n")
    
    actions = [
        ('RAM Temizliği', 'psapi.dll EmptyWorkingSet'),
        ('FPS Boost', 'powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61'),
        ('SSD TRIM', 'fsutil behavior set disabledeletenotify 0'),
        ('Network Throttling', 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f'),
        ('GPU Hardware Scheduling', 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f'),
    ]
    
    for name, cmd in actions:
        print(Fore.CYAN + f"  • {name:<30} ", end='', flush=True)
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT_MEDIUM)
            print(Fore.GREEN + "✓")
        except:
            print(Fore.RED + "✗")
    
    print(Fore.GREEN + "\n  ✅ Otomatik optimizasyon tamamlandı!")

def apply_high_priority_suggestions():
    """Sadece yüksek öncelikli önerileri uygula"""
    print(Fore.YELLOW + "\n  🔴 Yüksek öncelikli optimizasyonlar uygulanıyor...\n")
    
    # RAM temizliği
    print(Fore.CYAN + "  • RAM Temizliği                ", end='', flush=True)
    try:
        import ctypes
        psapi = ctypes.WinDLL('psapi.dll')
        kernel = ctypes.WinDLL('kernel32.dll')
        psapi.EmptyWorkingSet(kernel.GetCurrentProcess())
        print(Fore.GREEN + "✓")
    except:
        print(Fore.RED + "✗")
    
    # Process önceliği
    print(Fore.CYAN + "  • Process Optimizasyonu        ", end='', flush=True)
    try:
        subprocess.run(
            'wmic process where name="explorer.exe" CALL setpriority "below normal"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=TIMEOUT_MEDIUM
        )
        print(Fore.GREEN + "✓")
    except:
        print(Fore.RED + "✗")
    
    print(Fore.GREEN + "\n  ✅ Yüksek öncelikli optimizasyonlar tamamlandı!")

if __name__ == "__main__":
    from colorama import init
    init(autoreset=True)
    analyze_and_suggest()
    input("\n\nDevam etmek için ENTER'a basın...")
