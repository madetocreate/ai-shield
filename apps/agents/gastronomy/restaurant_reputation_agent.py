"""
Restaurant Reputation Agent - Reviews & Responses

Kann:
- Neue Reviews erkennen (Google/Yelp/etc.)
- Antwortvorschläge (Ton: freundlich, deeskalierend)
- Interne Eskalation bei kritischen Fällen

Inspiration: Yelp AI Host/Rezeptionist
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ReviewSentiment(str, Enum):
    """Review-Sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CRITICAL = "critical"  # Sehr negativ, erfordert sofortige Aufmerksamkeit


@dataclass
class Review:
    """Review-Eintrag"""
    review_id: str
    platform: str  # google, yelp, tripadvisor, etc.
    rating: int  # 1-5
    text: str
    author: str
    date: datetime
    sentiment: ReviewSentiment
    requires_response: bool = True
    response_sent: bool = False


class RestaurantReputationAgent:
    """
    Reputation Agent für Review-Management
    
    Überwacht Reviews, generiert Antworten, eskaliert kritische Fälle.
    """
    
    def __init__(self, account_id: str, integration_agent=None, marketing_execution_agent=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.marketing_execution_agent = marketing_execution_agent
        self.reviews: List[Review] = []
    
    def analyze_review(self, review_text: str, rating: int) -> ReviewSentiment:
        """
        Analysiert Review und bestimmt Sentiment
        
        Returns:
            ReviewSentiment
        """
        # TODO: NLP-basierte Sentiment-Analyse
        
        if rating <= 2:
            # Kritische Keywords prüfen
            critical_keywords = ["schlecht", "schrecklich", "nie wieder", "enttäuscht", "beschwerde"]
            if any(kw in review_text.lower() for kw in critical_keywords):
                return ReviewSentiment.CRITICAL
            return ReviewSentiment.NEGATIVE
        
        if rating == 3:
            return ReviewSentiment.NEUTRAL
        
        return ReviewSentiment.POSITIVE
    
    def generate_response(
        self,
        review: Review
    ) -> str:
        """
        Generiert Antwortvorschlag für Review
        
        Returns:
            Antwort-Text
        """
        if review.sentiment == ReviewSentiment.POSITIVE:
            return self._generate_positive_response(review)
        elif review.sentiment == ReviewSentiment.NEGATIVE or review.sentiment == ReviewSentiment.CRITICAL:
            return self._generate_negative_response(review)
        else:
            return self._generate_neutral_response(review)
    
    def _generate_positive_response(self, review: Review) -> str:
        """Generiert Antwort für positive Reviews"""
        templates = [
            f"Vielen Dank, {review.author}, für Ihre positive Bewertung! Wir freuen uns sehr, dass Sie zufrieden waren.",
            f"Liebe/r {review.author}, vielen Dank für Ihr Feedback! Es freut uns, dass Sie einen schönen Abend bei uns hatten.",
        ]
        # TODO: Personalisierung basierend auf Review-Inhalt
        return templates[0]
    
    def _generate_negative_response(self, review: Review) -> str:
        """Generiert deeskalierende Antwort für negative Reviews"""
        return f"""Liebe/r {review.author},

vielen Dank für Ihr Feedback. Es tut uns leid, dass Ihr Besuch nicht Ihren Erwartungen entsprochen hat.

Wir nehmen Ihre Anmerkungen sehr ernst und würden gerne mit Ihnen persönlich sprechen, um die Situation zu klären. Bitte kontaktieren Sie uns unter [Kontakt].

Wir hoffen, Sie bei einem nächsten Besuch von uns überzeugen zu können.

Mit freundlichen Grüßen
[Restaurant Name]"""
    
    def _generate_neutral_response(self, review: Review) -> str:
        """Generiert Antwort für neutrale Reviews"""
        return f"Vielen Dank, {review.author}, für Ihr Feedback. Wir nehmen Ihre Anmerkungen zur Kenntnis und arbeiten kontinuierlich an Verbesserungen."
    
    def should_escalate(self, review: Review) -> bool:
        """Prüft ob Review eskaliert werden sollte"""
        return (
            review.sentiment == ReviewSentiment.CRITICAL or
            (review.sentiment == ReviewSentiment.NEGATIVE and review.rating == 1)
        )
    
    def process_new_review(
        self,
        review_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verarbeitet neue Review
        
        Returns:
            Dict mit Review, Response-Vorschlag, Escalation-Status
        """
        review = Review(
            review_id=review_data.get("review_id", ""),
            platform=review_data.get("platform", "unknown"),
            rating=review_data.get("rating", 0),
            text=review_data.get("text", ""),
            author=review_data.get("author", "Anonym"),
            date=datetime.fromisoformat(review_data.get("date", datetime.now().isoformat())),
            sentiment=self.analyze_review(
                review_data.get("text", ""),
                review_data.get("rating", 0)
            )
        )
        
        self.reviews.append(review)
        
        response = self.generate_response(review)
        escalate = self.should_escalate(review)
        
        return {
            "review": review,
            "response_suggestion": response,
            "requires_escalation": escalate,
            "priority": "high" if escalate else "normal"
        }
