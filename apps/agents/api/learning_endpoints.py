"""
Learning API Endpoints - FastAPI Endpoints für Agent Learning

Endpoints:
- POST /api/v1/learning/feedback - Feedback sammeln
- GET /api/v1/learning/agents/{agent_name}/metrics - Performance Metrics
- GET /api/v1/learning/agents/{agent_name}/insights - Learning Insights
- GET /api/v1/learning/agents/{agent_name}/recommendations - Verbesserungs-Empfehlungen
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.agent_learning import (
    get_learning_system,
    FeedbackType,
    FeedbackSource
)

router = APIRouter(prefix="/api/v1/learning", tags=["learning"])


# Request Models
class CollectFeedbackRequest(BaseModel):
    agent_name: str
    feedback_type: str  # positive, negative, neutral, correction
    source: str  # user, system, human_reviewer, automated
    rating: Optional[float] = None  # 1.0 - 5.0
    comment: Optional[str] = None
    context: Dict[str, Any] = {}
    user_id: Optional[str] = None
    account_id: Optional[str] = None


# Response Models
class PerformanceMetricsResponse(BaseModel):
    agent_name: str
    avg_rating: float
    total_feedback: int
    positive_rate: float
    negative_rate: float
    improvement_trend: str
    common_errors: List[str]
    best_practices: List[str]


class LearningInsightResponse(BaseModel):
    agent_name: str
    insight_type: str
    description: str
    confidence: float
    recommendations: List[str]


@router.post("/feedback")
def collect_feedback(request: CollectFeedbackRequest):
    """Sammelt Feedback"""
    learning = get_learning_system()
    
    try:
        feedback_type = FeedbackType(request.feedback_type)
        source = FeedbackSource(request.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültiger Wert: {e}")
    
    feedback = learning.collect_feedback(
        agent_name=request.agent_name,
        feedback_type=feedback_type,
        source=source,
        rating=request.rating,
        comment=request.comment,
        context=request.context,
        user_id=request.user_id,
        account_id=request.account_id
    )
    
    return {
        "success": True,
        "feedback_id": feedback.agent_name,
        "message": "Feedback gesammelt"
    }


@router.get("/agents/{agent_name}/metrics", response_model=PerformanceMetricsResponse)
def get_performance_metrics(agent_name: str):
    """Holt Performance Metrics"""
    learning = get_learning_system()
    metrics = learning.get_performance_metrics(agent_name)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Keine Metrics verfügbar")
    
    return PerformanceMetricsResponse(
        agent_name=metrics.agent_name,
        avg_rating=metrics.avg_rating,
        total_feedback=metrics.total_feedback,
        positive_rate=metrics.positive_rate,
        negative_rate=metrics.negative_rate,
        improvement_trend=metrics.improvement_trend,
        common_errors=metrics.common_errors,
        best_practices=metrics.best_practices
    )


@router.get("/agents/{agent_name}/insights", response_model=List[LearningInsightResponse])
def get_insights(agent_name: str, limit: int = 10):
    """Holt Learning Insights"""
    learning = get_learning_system()
    insights = learning.get_insights(agent_name, limit=limit)
    
    return [
        LearningInsightResponse(
            agent_name=i.agent_name,
            insight_type=i.insight_type,
            description=i.description,
            confidence=i.confidence,
            recommendations=i.recommendations
        )
        for i in insights
    ]


@router.get("/agents/{agent_name}/recommendations")
def get_recommendations(agent_name: str):
    """Gibt Verbesserungs-Empfehlungen"""
    learning = get_learning_system()
    recommendations = learning.get_improvement_recommendations(agent_name)
    
    return {
        "agent_name": agent_name,
        "recommendations": recommendations,
        "count": len(recommendations)
    }
