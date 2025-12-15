"""
Agent Learning System Beispiel

Zeigt wie Agents aus Feedback lernen.
"""

from apps.agents.core.agent_learning import (
    get_learning_system,
    FeedbackType,
    FeedbackSource
)


def example_feedback_collection():
    """Beispiel: Feedback sammeln"""
    learning = get_learning_system()
    
    # Positive Feedbacks
    learning.collect_feedback(
        agent_name="restaurant_voice_host_agent",
        feedback_type=FeedbackType.POSITIVE,
        source=FeedbackSource.USER,
        rating=5.0,
        comment="Sehr hilfreich und freundlich!",
        account_id="account_123"
    )
    
    learning.collect_feedback(
        agent_name="restaurant_voice_host_agent",
        feedback_type=FeedbackType.POSITIVE,
        source=FeedbackSource.USER,
        rating=4.5,
        comment="Gut, aber etwas langsam",
        account_id="account_123"
    )
    
    # Negative Feedback
    learning.collect_feedback(
        agent_name="restaurant_voice_host_agent",
        feedback_type=FeedbackType.NEGATIVE,
        source=FeedbackSource.USER,
        rating=2.0,
        comment="Konnte meine Anfrage nicht verstehen",
        context={
            "user_message": "Ich will heute Abend essen",
            "agent_response": "Entschuldigung, ich verstehe nicht"
        },
        account_id="account_123"
    )
    
    # Correction
    learning.collect_feedback(
        agent_name="restaurant_voice_host_agent",
        feedback_type=FeedbackType.CORRECTION,
        source=FeedbackSource.USER,
        comment="Korrektur: Ich wollte eine Reservierung, nicht Takeout",
        context={
            "original_response": "Takeout bestellen?",
            "corrected_intent": "reservation"
        },
        account_id="account_123"
    )
    
    print("Feedback gesammelt")


def example_insights_and_recommendations():
    """Beispiel: Insights und Empfehlungen holen"""
    learning = get_learning_system()
    
    # Performance Metrics
    metrics = learning.get_performance_metrics("restaurant_voice_host_agent")
    if metrics:
        print(f"Average Rating: {metrics.avg_rating:.2f}")
        print(f"Total Feedback: {metrics.total_feedback}")
        print(f"Positive Rate: {metrics.positive_rate:.2%}")
        print(f"Negative Rate: {metrics.negative_rate:.2%}")
        print(f"Trend: {metrics.improvement_trend}")
        print(f"Common Errors: {metrics.common_errors}")
    
    # Insights
    insights = learning.get_insights("restaurant_voice_host_agent", limit=5)
    print(f"\nInsights ({len(insights)}):")
    for insight in insights:
        print(f"  - {insight.insight_type}: {insight.description}")
        print(f"    Recommendations: {insight.recommendations}")
    
    # Recommendations
    recommendations = learning.get_improvement_recommendations("restaurant_voice_host_agent")
    print(f"\nRecommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    print("=" * 80)
    print("AGENT LEARNING SYSTEM BEISPIEL")
    print("=" * 80)
    print()
    
    # Feedback sammeln
    print("1. Feedback sammeln:")
    example_feedback_collection()
    print()
    
    # Insights & Recommendations
    print("2. Insights & Recommendations:")
    example_insights_and_recommendations()
    print()
