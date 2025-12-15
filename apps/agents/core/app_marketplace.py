"""
App Marketplace - Community Agents, Agent Sharing, Rating System

Features:
- Agent Discovery
- Agent Sharing
- Rating System
- Version Management
- Installation/Uninstallation
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import logging

logger = logging.getLogger(__name__)


class AgentCategory(str, Enum):
    """Agent Kategorien"""
    GASTRONOMY = "gastronomy"
    PRACTICE = "practice"
    GENERAL = "general"
    PRODUCTIVITY = "productivity"
    MARKETING = "marketing"
    SUPPORT = "support"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent Status"""
    PUBLISHED = "published"
    DRAFT = "draft"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class AgentRating:
    """Agent Rating"""
    agent_id: str
    user_id: str
    rating: int  # 1-5
    comment: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketplaceAgent:
    """Marketplace Agent"""
    id: str
    name: str
    description: str
    author: str
    version: str
    category: AgentCategory
    status: AgentStatus
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    installation_count: int = 0
    average_rating: float = 0.0
    rating_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    code_url: Optional[str] = None
    documentation_url: Optional[str] = None
    license: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentMarketplace:
    """
    Agent Marketplace
    
    Verwaltet Community Agents, Ratings, Installationen.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialisiert Marketplace
        
        Args:
            storage_path: Pfad für Storage (JSON-Datei)
        """
        self.storage_path = storage_path or os.getenv(
            "MARKETPLACE_STORAGE_PATH",
            "data/marketplace.json"
        )
        self.agents: Dict[str, MarketplaceAgent] = {}
        self.ratings: Dict[str, List[AgentRating]] = {}  # agent_id -> ratings
        self.installations: Dict[str, List[str]] = {}  # account_id -> [agent_ids]
        self._load_data()
    
    def _load_data(self):
        """Lädt Daten aus Storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Lade Agents
                    for agent_data in data.get("agents", []):
                        agent = MarketplaceAgent(**agent_data)
                        self.agents[agent.id] = agent
                    # Lade Ratings
                    for agent_id, ratings_data in data.get("ratings", {}).items():
                        self.ratings[agent_id] = [
                            AgentRating(**r) for r in ratings_data
                        ]
                    # Lade Installationen
                    self.installations = data.get("installations", {})
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Marketplace-Daten: {e}")
    
    def _save_data(self):
        """Speichert Daten in Storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description,
                        "author": agent.author,
                        "version": agent.version,
                        "category": agent.category.value,
                        "status": agent.status.value,
                        "tags": agent.tags,
                        "dependencies": agent.dependencies,
                        "installation_count": agent.installation_count,
                        "average_rating": agent.average_rating,
                        "rating_count": agent.rating_count,
                        "created_at": agent.created_at.isoformat(),
                        "updated_at": agent.updated_at.isoformat(),
                        "code_url": agent.code_url,
                        "documentation_url": agent.documentation_url,
                        "license": agent.license,
                        "metadata": agent.metadata
                    }
                    for agent in self.agents.values()
                ],
                "ratings": {
                    agent_id: [
                        {
                            "agent_id": r.agent_id,
                            "user_id": r.user_id,
                            "rating": r.rating,
                            "comment": r.comment,
                            "created_at": r.created_at.isoformat()
                        }
                        for r in ratings
                    ]
                    for agent_id, ratings in self.ratings.items()
                },
                "installations": self.installations
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Marketplace-Daten: {e}")
    
    def publish_agent(self, agent: MarketplaceAgent) -> bool:
        """
        Veröffentlicht Agent im Marketplace
        
        Args:
            agent: Marketplace Agent
        
        Returns:
            True wenn erfolgreich
        """
        try:
            agent.status = AgentStatus.PUBLISHED
            agent.created_at = datetime.now()
            agent.updated_at = datetime.now()
            self.agents[agent.id] = agent
            self._save_data()
            logger.info(f"Agent {agent.id} veröffentlicht")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Veröffentlichen: {e}")
            return False
    
    def search_agents(
        self,
        query: Optional[str] = None,
        category: Optional[AgentCategory] = None,
        tags: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        limit: int = 20
    ) -> List[MarketplaceAgent]:
        """
        Sucht Agents im Marketplace
        
        Args:
            query: Suchanfrage
            category: Kategorie-Filter
            tags: Tag-Filter
            min_rating: Mindest-Rating
            limit: Maximale Anzahl Ergebnisse
        
        Returns:
            Liste von Agents
        """
        results = []
        
        for agent in self.agents.values():
            if agent.status != AgentStatus.PUBLISHED:
                continue
            
            # Filter: Kategorie
            if category and agent.category != category:
                continue
            
            # Filter: Rating
            if min_rating and agent.average_rating < min_rating:
                continue
            
            # Filter: Tags
            if tags and not any(tag in agent.tags for tag in tags):
                continue
            
            # Filter: Query
            if query:
                query_lower = query.lower()
                if query_lower not in agent.name.lower() and \
                   query_lower not in agent.description.lower() and \
                   not any(query_lower in tag.lower() for tag in agent.tags):
                    continue
            
            results.append(agent)
        
        # Sortiere nach Rating und Installation Count
        results.sort(key=lambda a: (a.average_rating, a.installation_count), reverse=True)
        
        return results[:limit]
    
    def rate_agent(
        self,
        agent_id: str,
        user_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> bool:
        """
        Bewertet Agent
        
        Args:
            agent_id: Agent ID
            user_id: User ID
            rating: Rating (1-5)
            comment: Kommentar (optional)
        
        Returns:
            True wenn erfolgreich
        """
        if agent_id not in self.agents:
            return False
        
        if rating < 1 or rating > 5:
            return False
        
        # Erstelle Rating
        agent_rating = AgentRating(
            agent_id=agent_id,
            user_id=user_id,
            rating=rating,
            comment=comment
        )
        
        # Füge Rating hinzu
        if agent_id not in self.ratings:
            self.ratings[agent_id] = []
        self.ratings[agent_id].append(agent_rating)
        
        # Aktualisiere Agent-Rating
        agent = self.agents[agent_id]
        all_ratings = self.ratings[agent_id]
        agent.average_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
        agent.rating_count = len(all_ratings)
        agent.updated_at = datetime.now()
        
        self._save_data()
        return True
    
    def install_agent(self, agent_id: str, account_id: str) -> bool:
        """
        Installiert Agent für Account
        
        Args:
            agent_id: Agent ID
            account_id: Account ID
        
        Returns:
            True wenn erfolgreich
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.status != AgentStatus.PUBLISHED:
            return False
        
        # Füge Installation hinzu
        if account_id not in self.installations:
            self.installations[account_id] = []
        
        if agent_id not in self.installations[account_id]:
            self.installations[account_id].append(agent_id)
            agent.installation_count += 1
            agent.updated_at = datetime.now()
            self._save_data()
        
        return True
    
    def uninstall_agent(self, agent_id: str, account_id: str) -> bool:
        """
        Deinstalliert Agent für Account
        
        Args:
            agent_id: Agent ID
            account_id: Account ID
        
        Returns:
            True wenn erfolgreich
        """
        if account_id in self.installations and agent_id in self.installations[account_id]:
            self.installations[account_id].remove(agent_id)
            if agent_id in self.agents:
                self.agents[agent_id].installation_count = max(0, self.agents[agent_id].installation_count - 1)
                self.agents[agent_id].updated_at = datetime.now()
            self._save_data()
            return True
        return False
    
    def get_installed_agents(self, account_id: str) -> List[MarketplaceAgent]:
        """Holt installierte Agents für Account"""
        agent_ids = self.installations.get(account_id, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]


# Globale Marketplace-Instanz
_global_marketplace: Optional[AgentMarketplace] = None


def get_marketplace() -> AgentMarketplace:
    """Holt globale Marketplace-Instanz"""
    global _global_marketplace
    if _global_marketplace is None:
        _global_marketplace = AgentMarketplace()
    return _global_marketplace
