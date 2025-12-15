"""
Advanced Analytics - Predictive Analytics, Anomaly Detection, Business Intelligence

Features:
- Predictive Analytics
- Anomaly Detection
- Business Intelligence
- Trend Analysis
- Forecasting
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesDataPoint:
    """Time Series Data Point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetectionResult:
    """Anomaly Detection Ergebnis"""
    is_anomaly: bool
    score: float  # 0.0 - 1.0 (höher = anomaler)
    expected_value: Optional[float] = None
    actual_value: float = 0.0
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ForecastResult:
    """Forecast Ergebnis"""
    predictions: List[float]  # Vorhersagen für nächste N Perioden
    confidence_intervals: List[tuple] = field(default_factory=list)  # (lower, upper)
    method: str = "moving_average"
    timestamp: datetime = field(default_factory=datetime.now)


class AnomalyDetector:
    """
    Anomaly Detector
    
    Erkennt Anomalien in Zeitreihen-Daten.
    """
    
    def __init__(self, window_size: int = 10, threshold: float = 2.0):
        """
        Initialisiert Anomaly Detector
        
        Args:
            window_size: Größe des Sliding Windows
            threshold: Standardabweichungs-Threshold (z.B. 2.0 = 2 Sigma)
        """
        self.window_size = window_size
        self.threshold = threshold
    
    def detect(
        self,
        data_points: List[TimeSeriesDataPoint],
        current_value: float
    ) -> AnomalyDetectionResult:
        """
        Erkennt Anomalie
        
        Args:
            data_points: Historische Datenpunkte
            current_value: Aktueller Wert
        
        Returns:
            AnomalyDetectionResult
        """
        if len(data_points) < self.window_size:
            # Nicht genug Daten
            return AnomalyDetectionResult(
                is_anomaly=False,
                score=0.0,
                actual_value=current_value,
                reason="Not enough historical data"
            )
        
        # Nutze letzte N Datenpunkte
        recent_values = [dp.value for dp in data_points[-self.window_size:]]
        
        # Berechne Statistik
        mean = statistics.mean(recent_values)
        stdev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0
        
        if stdev == 0.0:
            # Keine Variation
            is_anomaly = current_value != mean
            score = 1.0 if is_anomaly else 0.0
        else:
            # Z-Score berechnen
            z_score = abs((current_value - mean) / stdev)
            is_anomaly = z_score > self.threshold
            score = min(1.0, z_score / self.threshold)
        
        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            expected_value=mean,
            actual_value=current_value,
            reason=f"Z-score: {z_score:.2f}, Threshold: {self.threshold}" if stdev > 0 else "No variation",
            timestamp=datetime.now()
        )


class ForecastingEngine:
    """
    Forecasting Engine
    
    Erstellt Vorhersagen basierend auf historischen Daten.
    """
    
    def __init__(self):
        """Initialisiert Forecasting Engine"""
        pass
    
    def forecast(
        self,
        data_points: List[TimeSeriesDataPoint],
        periods: int = 7,
        method: str = "moving_average"
    ) -> ForecastResult:
        """
        Erstellt Vorhersage
        
        Args:
            data_points: Historische Datenpunkte
            periods: Anzahl Perioden für Vorhersage
            method: Methode (moving_average, linear_trend, exponential_smoothing)
        
        Returns:
            ForecastResult
        """
        if len(data_points) < 2:
            # Nicht genug Daten
            return ForecastResult(
                predictions=[data_points[0].value] * periods if data_points else [0.0] * periods,
                method=method
            )
        
        values = [dp.value for dp in data_points]
        
        if method == "moving_average":
            predictions = self._moving_average_forecast(values, periods)
        elif method == "linear_trend":
            predictions = self._linear_trend_forecast(values, periods)
        elif method == "exponential_smoothing":
            predictions = self._exponential_smoothing_forecast(values, periods)
        else:
            predictions = self._moving_average_forecast(values, periods)
        
        # Berechne Confidence Intervals (vereinfacht)
        confidence_intervals = [
            (pred * 0.9, pred * 1.1) for pred in predictions
        ]
        
        return ForecastResult(
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            method=method
        )
    
    def _moving_average_forecast(self, values: List[float], periods: int) -> List[float]:
        """Moving Average Forecast"""
        window = min(7, len(values))
        avg = statistics.mean(values[-window:])
        return [avg] * periods
    
    def _linear_trend_forecast(self, values: List[float], periods: int) -> List[float]:
        """Linear Trend Forecast"""
        if len(values) < 2:
            return [values[0]] * periods
        
        # Berechne Trend
        n = len(values)
        x = list(range(n))
        y = values
        
        # Einfache lineare Regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Vorhersagen
        predictions = []
        for i in range(periods):
            pred = intercept + slope * (n + i)
            predictions.append(pred)
        
        return predictions
    
    def _exponential_smoothing_forecast(self, values: List[float], periods: int, alpha: float = 0.3) -> List[float]:
        """Exponential Smoothing Forecast"""
        if not values:
            return [0.0] * periods
        
        # Exponential Smoothing
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])
        
        # Vorhersage: Nutze letzter geglätteter Wert
        last_smoothed = smoothed[-1]
        return [last_smoothed] * periods


class BusinessIntelligence:
    """
    Business Intelligence
    
    Analysiert Business-Metriken und erstellt Insights.
    """
    
    def __init__(self):
        """Initialisiert Business Intelligence"""
        self.metrics_history: Dict[str, List[TimeSeriesDataPoint]] = {}
    
    def track_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Trackt Metrik
        
        Args:
            metric_name: Metrik-Name
            value: Wert
            metadata: Zusätzliche Metadaten
        """
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
        
        self.metrics_history[metric_name].append(
            TimeSeriesDataPoint(
                timestamp=datetime.now(),
                value=value,
                metadata=metadata or {}
            )
        )
        
        # Behalte nur letzte 1000 Datenpunkte
        if len(self.metrics_history[metric_name]) > 1000:
            self.metrics_history[metric_name] = self.metrics_history[metric_name][-1000:]
    
    def get_insights(self, metric_name: str) -> Dict[str, Any]:
        """
        Gibt Business Insights
        
        Args:
            metric_name: Metrik-Name
        
        Returns:
            Dict mit Insights
        """
        if metric_name not in self.metrics_history or not self.metrics_history[metric_name]:
            return {"error": "No data available"}
        
        data_points = self.metrics_history[metric_name]
        values = [dp.value for dp in data_points]
        
        # Basis-Statistik
        mean = statistics.mean(values)
        median = statistics.median(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        
        # Trends
        recent_avg = statistics.mean([dp.value for dp in data_points[-7:]]) if len(data_points) >= 7 else mean
        older_avg = statistics.mean([dp.value for dp in data_points[:-7]]) if len(data_points) >= 14 else recent_avg
        trend = "increasing" if recent_avg > older_avg * 1.1 else "decreasing" if recent_avg < older_avg * 0.9 else "stable"
        
        # Anomaly Detection
        detector = AnomalyDetector()
        latest_value = values[-1]
        anomaly = detector.detect(data_points, latest_value)
        
        # Forecasting
        forecaster = ForecastingEngine()
        forecast = forecaster.forecast(data_points, periods=7)
        
        return {
            "metric_name": metric_name,
            "current_value": latest_value,
            "mean": mean,
            "median": median,
            "stdev": stdev,
            "trend": trend,
            "trend_percentage": ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0.0,
            "anomaly": {
                "is_anomaly": anomaly.is_anomaly,
                "score": anomaly.score,
                "reason": anomaly.reason
            },
            "forecast": {
                "next_7_days": forecast.predictions,
                "method": forecast.method
            },
            "data_points_count": len(data_points)
        }
    
    def get_comparison(self, metric1: str, metric2: str) -> Dict[str, Any]:
        """
        Vergleicht zwei Metriken
        
        Args:
            metric1: Erste Metrik
            metric2: Zweite Metrik
        
        Returns:
            Vergleichs-Ergebnis
        """
        if metric1 not in self.metrics_history or metric2 not in self.metrics_history:
            return {"error": "Metrics not found"}
        
        values1 = [dp.value for dp in self.metrics_history[metric1]]
        values2 = [dp.value for dp in self.metrics_history[metric2]]
        
        if not values1 or not values2:
            return {"error": "No data available"}
        
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        correlation = self._calculate_correlation(values1, values2) if len(values1) == len(values2) else 0.0
        
        return {
            "metric1": {
                "name": metric1,
                "mean": mean1,
                "current": values1[-1] if values1 else 0.0
            },
            "metric2": {
                "name": metric2,
                "mean": mean2,
                "current": values2[-1] if values2 else 0.0
            },
            "correlation": correlation,
            "ratio": mean1 / mean2 if mean2 > 0 else 0.0
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Berechnet Korrelation (vereinfacht)"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = (
            sum((x[i] - mean_x) ** 2 for i in range(n)) *
            sum((y[i] - mean_y) ** 2 for i in range(n))
        ) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


# Globale Instanzen
_global_anomaly_detector: Optional[AnomalyDetector] = None
_global_forecasting_engine: Optional[ForecastingEngine] = None
_global_business_intelligence: Optional[BusinessIntelligence] = None


def get_anomaly_detector(window_size: int = 10, threshold: float = 2.0) -> AnomalyDetector:
    """Holt globale Anomaly Detector Instanz"""
    global _global_anomaly_detector
    if _global_anomaly_detector is None:
        _global_anomaly_detector = AnomalyDetector(window_size=window_size, threshold=threshold)
    return _global_anomaly_detector


def get_forecasting_engine() -> ForecastingEngine:
    """Holt globale Forecasting Engine Instanz"""
    global _global_forecasting_engine
    if _global_forecasting_engine is None:
        _global_forecasting_engine = ForecastingEngine()
    return _global_forecasting_engine


def get_business_intelligence() -> BusinessIntelligence:
    """Holt globale Business Intelligence Instanz"""
    global _global_business_intelligence
    if _global_business_intelligence is None:
        _global_business_intelligence = BusinessIntelligence()
    return _global_business_intelligence
