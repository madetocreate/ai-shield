"""
Agent Learning System - Feedback-Loop, Continuous Improvement, Auto-Optimization

Features:
- Feedback Collection
- Learning Algorithm
- Performance Tracking
- Auto-Optimization
- Continuous Improvement
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import logging
import statistics

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Feedback Type"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"  # User korrigiert Agent-Antwort


class FeedbackSource(str, Enum):
    """Feedback Source"""
    USER = "user"
    SYSTEM = "system"
    HUMAN_REVIEWER = "human_reviewer"
    AUTOMATED = "automated"


@dataclass
class AgentFeedback:
    """Agent Feedback"""
    agent_name: str
    feedback_type: FeedbackType
    source: FeedbackSource
    rating: Optional[float] = None  # 1.0 - 5.0
    comment: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)  # Request, Response, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    account_id: Optional[str] = None


@dataclass
class LearningInsight:
    """Learning Insight"""
    agent_name: str
    insight_type: str  # pattern, improvement, error_pattern
    description: str
    confidence: float
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance Metrics für Learning"""
    agent_name: str
    avg_rating: float
    total_feedback: int
    positive_rate: float
    negative_rate: float
    improvement_trend: str  # improving, stable, declining
    common_errors: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)


class AgentLearningSystem:
    """
    Agent Learning System
    
    Sammelt Feedback, analysiert Performance und optimiert Agents.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialisiert Learning System
        
        Args:
            storage_path: Pfad für Storage
        """
        self.storage_path = storage_path or os.getenv(
            "LEARNING_STORAGE_PATH",
            "data/agent_learning.json"
        )
        self.feedback_history: List[AgentFeedback] = []
        self.insights: Dict[str, List[LearningInsight]] = {}  # agent_name -> insights
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self._load_data()
    
    def _load_data(self):
        """Lädt Daten aus Storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.feedback_history = [
                        AgentFeedback(
                            agent_name=f["agent_name"],
                            feedback_type=FeedbackType(f["feedback_type"]),
                            source=FeedbackSource(f["source"]),
                            rating=f.get("rating"),
                            comment=f.get("comment"),
                            context=f.get("context", {}),
                            timestamp=datetime.fromisoformat(f.get("timestamp", datetime.now().isoformat())),
                            user_id=f.get("user_id"),
                            account_id=f.get("account_id")
                        )
                        for f in data.get("feedback_history", [])
                    ]
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Learning-Daten: {e}")
    
    def _save_data(self):
        """Speichert Daten in Storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "feedback_history": [
                    {
                        "agent_name": f.agent_name,
                        "feedback_type": f.feedback_type.value,
                        "source": f.source.value,
                        "rating": f.rating,
                        "comment": f.comment,
                        "context": f.context,
                        "timestamp": f.timestamp.isoformat(),
                        "user_id": f.user_id,
                        "account_id": f.account_id
                    }
                    for f in self.feedback_history
                ]
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Learning-Daten: {e}")
    
    def collect_feedback(
        self,
        agent_name: str,
        feedback_type: FeedbackType,
        source: FeedbackSource,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> AgentFeedback:
        """
        Sammelt Feedback
        
        Args:
            agent_name: Agent Name
            feedback_type: Feedback Type
            source: Feedback Source
            rating: Rating (1.0 - 5.0)
            comment: Kommentar
            context: Kontext (Request, Response, etc.)
            user_id: User ID
            account_id: Account ID
        
        Returns:
            AgentFeedback
        """
        feedback = AgentFeedback(
            agent_name=agent_name,
            feedback_type=feedback_type,
            source=source,
            rating=rating,
            comment=comment,
            context=context or {},
            user_id=user_id,
            account_id=account_id
        )
        
        self.feedback_history.append(feedback)
        
        # Analysiere Feedback
        self._analyze_feedback(feedback)
        
        # Speichere (alle 10 Feedbacks)
        if len(self.feedback_history) % 10 == 0:
            self._save_data()
        
        logger.info(f"Feedback gesammelt für {agent_name}: {feedback_type.value}")
        return feedback
    
    def _analyze_feedback(self, feedback: AgentFeedback):
        """Analysiert Feedback und generiert Insights"""
        agent_name = feedback.agent_name
        
        # Berechne Performance Metrics
        agent_feedbacks = [f for f in self.feedback_history if f.agent_name == agent_name]
        
        if not agent_feedbacks:
            return
        
        ratings = [f.rating for f in agent_feedbacks if f.rating is not None]
        positive = sum(1 for f in agent_feedbacks if f.feedback_type == FeedbackType.POSITIVE)
        negative = sum(1 for f in agent_feedbacks if f.feedback_type == FeedbackType.NEGATIVE)
        
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        positive_rate = positive / len(agent_feedbacks) if agent_feedbacks else 0.0
        negative_rate = negative / len(agent_feedbacks) if agent_feedbacks else 0.0
        
        # Trend-Analyse
        recent_feedbacks = agent_feedbacks[-20:] if len(agent_feedbacks) >= 20 else agent_feedbacks
        older_feedbacks = agent_feedbacks[:-20] if len(agent_feedbacks) >= 20 else []
        
        if older_feedbacks:
            recent_avg = statistics.mean([f.rating for f in recent_feedbacks if f.rating]) if any(f.rating for f in recent_feedbacks) else 0.0
            older_avg = statistics.mean([f.rating for f in older_feedbacks if f.rating]) if any(f.rating for f in older_feedbacks) else 0.0
            
            if recent_avg > older_avg * 1.1:
                trend = "improving"
            elif recent_avg < older_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Common Errors (aus negativen Feedbacks)
        common_errors = []
        negative_comments = [f.comment for f in agent_feedbacks if f.feedback_type == FeedbackType.NEGATIVE and f.comment]
        if negative_comments:
            # Einfache Pattern-Erkennung (könnte erweitert werden)
            common_errors = list(set(negative_comments[:5]))  # Top 5
        
        # Update Performance Metrics
        self.performance_metrics[agent_name] = PerformanceMetrics(
            agent_name=agent_name,
            avg_rating=avg_rating,
            total_feedback=len(agent_feedbacks),
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            improvement_trend=trend,
            common_errors=common_errors
        )
        
        # Generiere Insights
        self._generate_insights(agent_name, feedback)
    
    def _generate_insights(self, agent_name: str, feedback: AgentFeedback):
        """Generiert Learning Insights"""
        if agent_name not in self.insights:
            self.insights[agent_name] = []
        
        # Insight: Negative Feedback Pattern
        if feedback.feedback_type == FeedbackType.NEGATIVE:
            insight = LearningInsight(
                agent_name=agent_name,
                insight_type="error_pattern",
                description=f"Negatives Feedback erhalten: {feedback.comment or 'Kein Kommentar'}",
                confidence=0.7,
                recommendations=[
                    "Prüfe Agent-Logik für ähnliche Fälle",
                    "Verbessere Error Handling",
                    "Erweitere Prompt-Templates"
                ]
            )
            self.insights[agent_name].append(insight)
        
        # Insight: Rating Drop
        metrics = self.performance_metrics.get(agent_name)
        if metrics and metrics.improvement_trend == "declining":
            insight = LearningInsight(
                agent_name=agent_name,
                insight_type="performance_decline",
                description="Performance-Trend zeigt Verschlechterung",
                confidence=0.8,
                recommendations=[
                    "Review letzte Änderungen",
                    "Prüfe Dependencies",
                    "Analysiere Common Errors"
                ]
            )
            self.insights[agent_name].append(insight)
    
    def get_performance_metrics(self, agent_name: str) -> Optional[PerformanceMetrics]:
        """Holt Performance Metrics"""
        return self.performance_metrics.get(agent_name)
    
    def get_insights(self, agent_name: str, limit: int = 10) -> List[LearningInsight]:
        """Holt Insights für Agent"""
        return self.insights.get(agent_name, [])[-limit:]
    
    def get_improvement_recommendations(self, agent_name: str) -> List[str]:
        """Gibt Verbesserungs-Empfehlungen"""
        recommendations = []
        
        metrics = self.performance_metrics.get(agent_name)
        if not metrics:
            return ["Keine Daten verfügbar"]
        
        # Basierend auf Metrics
        if metrics.negative_rate > 0.3:
            recommendations.append("Hohe Negative-Rate - Prüfe Agent-Logik")
        
        if metrics.avg_rating < 3.0:
            recommendations.append("Niedrige Ratings - Verbessere Agent-Performance")
        
        if metrics.improvement_trend == "declining":
            recommendations.append("Performance-Trend zeigt Verschlechterung - Review nötig")
        
        # Basierend auf Insights
        insights = self.get_insights(agent_name, limit=5)
        for insight in insights:
            recommendations.extend(insight.recommendations)
        
        return list(set(recommendations))  # Unique


# Globale Learning System-Instanz
_global_learning_system: Optional[AgentLearningSystem] = None


def get_learning_system() -> AgentLearningSystem:
    """Holt globale Learning System-Instanz"""
    global _global_learning_system
    if _global_learning_system is None:
        _global_learning_system = AgentLearningSystem()
    return _global_learning_system
