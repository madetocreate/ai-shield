"""
AI Shield SDK Client - Python Client für AI Shield Agents API
"""

from typing import Dict, Optional, Any, List
import httpx
import asyncio
from .exceptions import AIShieldError, APIError, AuthenticationError


class AIShieldClient:
    """
    AI Shield SDK Client
    
    Python Client für die AI Shield Agents API.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None
    ):
        """
        Initialisiert Client
        
        Args:
            base_url: Base URL der API
            api_key: API Key für Authentifizierung
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def close(self):
        """Schließt Client"""
        await self.client.aclose()
    
    def _handle_response(self, response: httpx.Response):
        """Behandelt Response"""
        if response.status_code == 401:
            raise AuthenticationError("Unauthorized")
        elif response.status_code >= 400:
            raise APIError(f"API Error: {response.status_code} - {response.text}")
        return response.json()
    
    # Marketplace
    async def search_agents(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Sucht Agents im Marketplace"""
        params = {}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        if min_rating:
            params["min_rating"] = min_rating
        
        response = await self.client.get(
            f"{self.base_url}/api/v1/marketplace/agents",
            params=params
        )
        return self._handle_response(response)
    
    async def install_agent(self, agent_id: str, account_id: str) -> Dict[str, Any]:
        """Installiert Agent"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/marketplace/agents/{agent_id}/install",
            json={"account_id": account_id}
        )
        return self._handle_response(response)
    
    # Analytics
    async def track_metric(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Trackt Metrik"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/analytics/track",
            json={
                "metric_name": metric_name,
                "value": value,
                "metadata": metadata or {}
            }
        )
        return self._handle_response(response)
    
    async def get_insights(self, metric_name: str) -> Dict[str, Any]:
        """Holt Insights für Metrik"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/analytics/insights/{metric_name}"
        )
        return self._handle_response(response)
    
    # Configuration
    async def is_feature_enabled(
        self,
        feature_name: str,
        account_id: Optional[str] = None
    ) -> bool:
        """Prüft ob Feature aktiviert ist"""
        params = {}
        if account_id:
            params["account_id"] = account_id
        
        response = await self.client.get(
            f"{self.base_url}/api/v1/config/features/{feature_name}/check",
            params=params
        )
        result = self._handle_response(response)
        return result.get("enabled", False)
    
    # Webhooks
    async def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Erstellt Webhook"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/webhooks",
            json={
                "url": url,
                "events": events,
                "secret": secret
            }
        )
        return self._handle_response(response)
    
    # Costs
    async def track_cost(
        self,
        account_id: str,
        cost_type: str,
        amount: float,
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Trackt Kosten"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/costs/track",
            json={
                "account_id": account_id,
                "cost_type": cost_type,
                "amount": amount,
                "agent_name": agent_name
            }
        )
        return self._handle_response(response)
    
    async def get_costs(
        self,
        account_id: str,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """Holt Kosten für Account"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/costs/{account_id}",
            params={"period": period}
        )
        return self._handle_response(response)
    
    # Export
    async def export_agents(self, format: str = "json") -> str:
        """Exportiert Agents"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/export/agents",
            params={"format": format}
        )
        return response.text


# Sync Wrapper
class AIShieldClientSync:
    """Synchroner Wrapper für AIShieldClient"""
    
    def __init__(self, *args, **kwargs):
        self.client = AIShieldClient(*args, **kwargs)
        self._loop = None
    
    def _get_loop(self):
        """Holt oder erstellt Event Loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def search_agents(self, *args, **kwargs):
        """Sucht Agents (sync)"""
        return self._get_loop().run_until_complete(
            self.client.search_agents(*args, **kwargs)
        )
    
    def install_agent(self, *args, **kwargs):
        """Installiert Agent (sync)"""
        return self._get_loop().run_until_complete(
            self.client.install_agent(*args, **kwargs)
        )
    
    def is_feature_enabled(self, *args, **kwargs):
        """Prüft Feature (sync)"""
        return self._get_loop().run_until_complete(
            self.client.is_feature_enabled(*args, **kwargs)
        )
