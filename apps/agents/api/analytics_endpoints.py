"""
Analytics API Endpoints - FastAPI Endpoints für Advanced Analytics

Endpoints:
- POST /api/v1/analytics/track - Metrik tracken
- GET /api/v1/analytics/insights/{metric_name} - Insights holen
- GET /api/v1/analytics/compare - Metriken vergleichen
- GET /api/v1/analytics/anomaly/{metric_name} - Anomaly Detection
- GET /api/v1/analytics/forecast/{metric_name} - Forecasting
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.advanced_analytics import (
    get_business_intelligence,
    get_anomaly_detector,
    get_forecasting_engine,
    TimeSeriesDataPoint
)
from datetime import datetime

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


# Request Models
class TrackMetricRequest(BaseModel):
    metric_name: str
    value: float
    metadata: Optional[Dict[str, Any]] = None


# Response Models
class InsightsResponse(BaseModel):
    metric_name: str
    current_value: float
    mean: float
    median: float
    stdev: float
    trend: str
    trend_percentage: float
    anomaly: Dict[str, Any]
    forecast: Dict[str, Any]
    data_points_count: int


class ComparisonResponse(BaseModel):
    metric1: Dict[str, Any]
    metric2: Dict[str, Any]
    correlation: float
    ratio: float


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    score: float
    expected_value: Optional[float]
    actual_value: float
    reason: Optional[str]


class ForecastResponse(BaseModel):
    predictions: List[float]
    confidence_intervals: List[List[float]]
    method: str


@router.post("/track")
def track_metric(request: TrackMetricRequest):
    """
    Trackt Metrik
    """
    bi = get_business_intelligence()
    bi.track_metric(
        metric_name=request.metric_name,
        value=request.value,
        metadata=request.metadata
    )
    return {"success": True, "message": "Metric tracked"}


@router.get("/insights/{metric_name}", response_model=InsightsResponse)
def get_insights(metric_name: str):
    """
    Holt Business Insights für Metrik
    """
    bi = get_business_intelligence()
    insights = bi.get_insights(metric_name)
    
    if "error" in insights:
        raise HTTPException(status_code=404, detail=insights["error"])
    
    return InsightsResponse(
        metric_name=insights["metric_name"],
        current_value=insights["current_value"],
        mean=insights["mean"],
        median=insights["median"],
        stdev=insights["stdev"],
        trend=insights["trend"],
        trend_percentage=insights["trend_percentage"],
        anomaly=insights["anomaly"],
        forecast=insights["forecast"],
        data_points_count=insights["data_points_count"]
    )


@router.get("/compare", response_model=ComparisonResponse)
def compare_metrics(
    metric1: str = Query(..., description="Erste Metrik"),
    metric2: str = Query(..., description="Zweite Metrik")
):
    """
    Vergleicht zwei Metriken
    """
    bi = get_business_intelligence()
    comparison = bi.get_comparison(metric1, metric2)
    
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    
    return ComparisonResponse(
        metric1=comparison["metric1"],
        metric2=comparison["metric2"],
        correlation=comparison["correlation"],
        ratio=comparison["ratio"]
    )


@router.get("/anomaly/{metric_name}", response_model=AnomalyResponse)
def detect_anomaly(
    metric_name: str,
    current_value: float = Query(..., description="Aktueller Wert"),
    window_size: int = Query(10, description="Window Size")
):
    """
    Erkennt Anomalie für Metrik
    """
    bi = get_business_intelligence()
    
    if metric_name not in bi.metrics_history or not bi.metrics_history[metric_name]:
        raise HTTPException(status_code=404, detail="Keine Daten verfügbar")
    
    data_points = bi.metrics_history[metric_name]
    detector = get_anomaly_detector(window_size=window_size)
    anomaly = detector.detect(data_points, current_value)
    
    return AnomalyResponse(
        is_anomaly=anomaly.is_anomaly,
        score=anomaly.score,
        expected_value=anomaly.expected_value,
        actual_value=anomaly.actual_value,
        reason=anomaly.reason
    )


@router.get("/forecast/{metric_name}", response_model=ForecastResponse)
def get_forecast(
    metric_name: str,
    periods: int = Query(7, description="Anzahl Perioden"),
    method: str = Query("moving_average", description="Methode (moving_average, linear_trend, exponential_smoothing)")
):
    """
    Erstellt Vorhersage für Metrik
    """
    bi = get_business_intelligence()
    
    if metric_name not in bi.metrics_history or not bi.metrics_history[metric_name]:
        raise HTTPException(status_code=404, detail="Keine Daten verfügbar")
    
    data_points = bi.metrics_history[metric_name]
    forecaster = get_forecasting_engine()
    forecast = forecaster.forecast(data_points, periods=periods, method=method)
    
    return ForecastResponse(
        predictions=forecast.predictions,
        confidence_intervals=[[ci[0], ci[1]] for ci in forecast.confidence_intervals],
        method=forecast.method
    )


@router.get("/metrics")
def list_metrics():
    """
    Listet alle verfügbaren Metriken
    """
    bi = get_business_intelligence()
    return {
        "metrics": list(bi.metrics_history.keys()),
        "count": len(bi.metrics_history)
    }
