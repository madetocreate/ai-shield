"""
Web Search Tool - Vollständige Web Search Integration

Ermöglicht Orchestrator direkten Zugriff auf Web-Suche für:
- Aktuelle Informationen
- Öffnungszeiten-Verifikation
- Event-Informationen
- Externe Daten

Unterstützt:
- Google Custom Search API
- Bing Search API
- SerpAPI
- OpenAI Web Search (wenn verfügbar)
"""

from typing import Dict, Optional, Any, List
import os
import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Web Search Tool für Orchestrator
    
    Nutzt verschiedene Search Providers mit Fallback.
    """
    
    def __init__(self, search_provider: str = "google"):
        """
        Initialisiert Web Search Tool
        
        Args:
            search_provider: "google", "bing", "serpapi", "openai"
        """
        self.search_provider = search_provider or os.getenv("WEB_SEARCH_PROVIDER", "google")
        self._setup_search()
        self.cache: Dict[str, Dict[str, Any]] = {}  # Simple cache
    
    def _setup_search(self):
        """Setzt Search Provider auf"""
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cx = os.getenv("GOOGLE_SEARCH_CX")
        self.bing_api_key = os.getenv("BING_SEARCH_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        
        # Client
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def search(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Führt Web-Suche aus
        
        Args:
            query: Suchanfrage
            max_results: Maximale Anzahl Ergebnisse
        
        Returns:
            Dict mit Suchergebnissen
        """
        # Prüfe Cache
        cache_key = f"{query}:{max_results}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Versuche verschiedene Provider
        providers = [self.search_provider, "google", "bing", "serpapi"]
        
        for provider in providers:
            try:
                if provider == "google":
                    result = await self._google_search(query, max_results)
                elif provider == "bing":
                    result = await self._bing_search(query, max_results)
                elif provider == "serpapi":
                    result = await self._serpapi_search(query, max_results)
                else:
                    continue
                
                if result.get("results"):
                    # Cache Ergebnis
                    self.cache[cache_key] = result
                    return result
            except Exception as e:
                logger.warning(f"Search Provider {provider} fehlgeschlagen: {e}")
                continue
        
        # Fallback: Placeholder
        return {
            "query": query,
            "provider": "none",
            "results": [],
            "status": "no_provider_available",
            "message": "Kein Search Provider verfügbar"
        }
    
    async def _google_search(
        self,
        query: str,
        max_results: int
    ) -> Dict[str, Any]:
        """Google Custom Search API"""
        if not self.google_api_key or not self.google_cx:
            raise ValueError("Google Search API Key oder CX nicht konfiguriert")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cx,
            "q": query,
            "num": min(max_results, 10)
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("items", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
                "displayLink": item.get("displayLink", "")
            })
        
        return {
            "query": query,
            "provider": "google",
            "results": results,
            "status": "success"
        }
    
    async def _bing_search(
        self,
        query: str,
        max_results: int
    ) -> Dict[str, Any]:
        """Bing Search API"""
        if not self.bing_api_key:
            raise ValueError("Bing Search API Key nicht konfiguriert")
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            "Ocp-Apim-Subscription-Key": self.bing_api_key
        }
        params = {
            "q": query,
            "count": min(max_results, 50)
        }
        
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("webPages", {}).get("value", [])[:max_results]:
            results.append({
                "title": item.get("name", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("url", ""),
                "displayLink": item.get("displayUrl", "")
            })
        
        return {
            "query": query,
            "provider": "bing",
            "results": results,
            "status": "success"
        }
    
    async def _serpapi_search(
        self,
        query: str,
        max_results: int
    ) -> Dict[str, Any]:
        """SerpAPI"""
        if not self.serpapi_key:
            raise ValueError("SerpAPI Key nicht konfiguriert")
        
        url = "https://serpapi.com/search"
        params = {
            "api_key": self.serpapi_key,
            "q": query,
            "engine": "google",
            "num": max_results
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic_results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
                "displayLink": item.get("displayLink", "")
            })
        
        return {
            "query": query,
            "provider": "serpapi",
            "results": results,
            "status": "success"
        }
    
    def clear_cache(self):
        """Löscht Cache"""
        self.cache.clear()


# Globale Web Search Tool-Instanz
_global_web_search: Optional[WebSearchTool] = None


def get_web_search_tool() -> WebSearchTool:
    """Holt globale Web Search Tool-Instanz"""
    global _global_web_search
    if _global_web_search is None:
        provider = os.getenv("WEB_SEARCH_PROVIDER", "google")
        _global_web_search = WebSearchTool(search_provider=provider)
    return _global_web_search
