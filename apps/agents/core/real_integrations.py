"""
Real Integrations - Echte Integrationen statt Mocks

Implementiert:
- Communications Supervisor (HTTP/WebSocket)
- Integration Agent (REST API)
- Knowledge Base Agent (Vector DB/API)
- CRM Agent (REST API)
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import os
import logging
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MessageRequest:
    """Nachrichten-Anfrage"""
    channel: str  # phone, chat, email, sms, website
    recipient: str
    message: str
    account_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MessageResponse:
    """Nachrichten-Antwort"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CommunicationsSupervisor:
    """
    Echter Communications Supervisor
    
    Sendet Nachrichten über verschiedene Kanäle (SMS, Email, Phone, Chat).
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialisiert Communications Supervisor
        
        Args:
            base_url: Base URL für Communications API
            api_key: API Key für Authentifizierung
        """
        self.base_url = base_url or os.getenv(
            "COMMUNICATIONS_API_URL",
            "http://localhost:8000/api/v1/communications"
        )
        self.api_key = api_key or os.getenv("COMMUNICATIONS_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def send_message(
        self,
        channel: str,
        recipient: str,
        message: str,
        account_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageResponse:
        """
        Sendet Nachricht über Channel
        
        Args:
            channel: phone, chat, email, sms, website
            recipient: Empfänger (Telefonnummer, Email, etc.)
            message: Nachricht
            account_id: Account ID
            user_id: User ID (optional)
            metadata: Zusätzliche Metadaten
        
        Returns:
            MessageResponse
        """
        try:
            payload = {
                "channel": channel,
                "recipient": recipient,
                "message": message,
                "account_id": account_id,
                "user_id": user_id,
                "metadata": metadata or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/send",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return MessageResponse(
                success=True,
                message_id=data.get("message_id"),
                metadata=data.get("metadata")
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Communications API Error: {e}")
            return MessageResponse(
                success=False,
                error=str(e)
            )
    
    async def send_sms(
        self,
        phone_number: str,
        message: str,
        account_id: str
    ) -> MessageResponse:
        """Sendet SMS"""
        return await self.send_message(
            channel="sms",
            recipient=phone_number,
            message=message,
            account_id=account_id
        )
    
    async def send_email(
        self,
        email: str,
        subject: str,
        message: str,
        account_id: str
    ) -> MessageResponse:
        """Sendet Email"""
        return await self.send_message(
            channel="email",
            recipient=email,
            message=f"{subject}\n\n{message}",
            account_id=account_id,
            metadata={"subject": subject}
        )
    
    def send_message_sync(
        self,
        channel: str,
        recipient: str,
        message: str,
        account_id: str,
        user_id: Optional[str] = None
    ) -> MessageResponse:
        """Synchroner Wrapper für send_message"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.send_message(channel, recipient, message, account_id, user_id)
            )
        except RuntimeError:
            # Neuer Event Loop falls keiner existiert
            return asyncio.run(
                self.send_message(channel, recipient, message, account_id, user_id)
            )


class IntegrationAgent:
    """
    Echter Integration Agent
    
    Führt Integrationen mit externen Systemen aus (OpenTable, Toast, Doctolib, etc.).
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialisiert Integration Agent
        
        Args:
            base_url: Base URL für Integration API
            api_key: API Key für Authentifizierung
        """
        self.base_url = base_url or os.getenv(
            "INTEGRATION_API_URL",
            "http://localhost:8000/api/v1/integrations"
        )
        self.api_key = api_key or os.getenv("INTEGRATION_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def execute_integration(
        self,
        integration_type: str,
        action: str,
        account_id: str,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Führt Integration aus
        
        Args:
            integration_type: opentable, toast, doctolib, etc.
            action: create_reservation, update_appointment, etc.
            account_id: Account ID
            data: Daten für Integration
            config: Zusätzliche Konfiguration
        
        Returns:
            Ergebnis der Integration
        """
        try:
            payload = {
                "integration_type": integration_type,
                "action": action,
                "account_id": account_id,
                "data": data,
                "config": config or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/execute",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Integration API Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_reservation(
        self,
        account_id: str,
        date: str,
        time: str,
        party_size: int,
        customer_name: str,
        customer_phone: str,
        integration_type: str = "opentable"
    ) -> Dict[str, Any]:
        """Erstellt Reservierung"""
        return await self.execute_integration(
            integration_type=integration_type,
            action="create_reservation",
            account_id=account_id,
            data={
                "date": date,
                "time": time,
                "party_size": party_size,
                "customer_name": customer_name,
                "customer_phone": customer_phone
            }
        )
    
    async def create_appointment(
        self,
        account_id: str,
        date: str,
        time: str,
        patient_name: str,
        patient_phone: str,
        integration_type: str = "doctolib"
    ) -> Dict[str, Any]:
        """Erstellt Termin"""
        return await self.execute_integration(
            integration_type=integration_type,
            action="create_appointment",
            account_id=account_id,
            data={
                "date": date,
                "time": time,
                "patient_name": patient_name,
                "patient_phone": patient_phone
            }
        )
    
    def execute_integration_sync(
        self,
        integration_type: str,
        action: str,
        account_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synchroner Wrapper"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.execute_integration(integration_type, action, account_id, data)
            )
        except RuntimeError:
            return asyncio.run(
                self.execute_integration(integration_type, action, account_id, data)
            )


class KnowledgeBaseAgent:
    """
    Echter Knowledge Base Agent
    
    Sucht in Knowledge Base nach Informationen.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialisiert Knowledge Base Agent
        
        Args:
            base_url: Base URL für Knowledge Base API
            api_key: API Key für Authentifizierung
        """
        self.base_url = base_url or os.getenv(
            "KNOWLEDGE_BASE_API_URL",
            "http://localhost:8000/api/v1/knowledge"
        )
        self.api_key = api_key or os.getenv("KNOWLEDGE_BASE_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def search(
        self,
        query: str,
        account_id: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Sucht in Knowledge Base
        
        Args:
            query: Suchanfrage
            account_id: Account ID
            limit: Maximale Anzahl Ergebnisse
            filters: Zusätzliche Filter
        
        Returns:
            Liste von Suchergebnissen
        """
        try:
            payload = {
                "query": query,
                "account_id": account_id,
                "limit": limit,
                "filters": filters or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/search",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", [])
            
        except httpx.HTTPError as e:
            logger.error(f"Knowledge Base API Error: {e}")
            return []
    
    def search_sync(
        self,
        query: str,
        account_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Synchroner Wrapper"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.search(query, account_id, limit))
        except RuntimeError:
            return asyncio.run(self.search(query, account_id, limit))


class CRMAgent:
    """
    Echter CRM Agent
    
    Erstellt/aktualisiert Kontakte, Deals, Notizen im CRM.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialisiert CRM Agent
        
        Args:
            base_url: Base URL für CRM API
            api_key: API Key für Authentifizierung
        """
        self.base_url = base_url or os.getenv(
            "CRM_API_URL",
            "http://localhost:8000/api/v1/crm"
        )
        self.api_key = api_key or os.getenv("CRM_API_KEY")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def create_contact(
        self,
        account_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Erstellt Kontakt"""
        try:
            payload = {
                "account_id": account_id,
                "name": name,
                "email": email,
                "phone": phone,
                "metadata": metadata or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/contacts",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"CRM API Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_deal(
        self,
        account_id: str,
        contact_id: str,
        title: str,
        value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Erstellt Deal"""
        try:
            payload = {
                "account_id": account_id,
                "contact_id": contact_id,
                "title": title,
                "value": value,
                "metadata": metadata or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/deals",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"CRM API Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_note(
        self,
        account_id: str,
        contact_id: str,
        note: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Erstellt Notiz"""
        try:
            payload = {
                "account_id": account_id,
                "contact_id": contact_id,
                "note": note,
                "metadata": metadata or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/notes",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"CRM API Error: {e}")
            return {"success": False, "error": str(e)}


# Globale Instanzen
_global_communications: Optional[CommunicationsSupervisor] = None
_global_integration: Optional[IntegrationAgent] = None
_global_knowledge_base: Optional[KnowledgeBaseAgent] = None
_global_crm: Optional[CRMAgent] = None


def get_communications_supervisor() -> CommunicationsSupervisor:
    """Holt globale Communications Supervisor-Instanz"""
    global _global_communications
    if _global_communications is None:
        _global_communications = CommunicationsSupervisor()
    return _global_communications


def get_integration_agent() -> IntegrationAgent:
    """Holt globale Integration Agent-Instanz"""
    global _global_integration
    if _global_integration is None:
        _global_integration = IntegrationAgent()
    return _global_integration


def get_knowledge_base_agent() -> KnowledgeBaseAgent:
    """Holt globale Knowledge Base Agent-Instanz"""
    global _global_knowledge_base
    if _global_knowledge_base is None:
        _global_knowledge_base = KnowledgeBaseAgent()
    return _global_knowledge_base


def get_crm_agent() -> CRMAgent:
    """Holt globale CRM Agent-Instanz"""
    global _global_crm
    if _global_crm is None:
        _global_crm = CRMAgent()
    return _global_crm
