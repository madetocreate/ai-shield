"""
Practice Document Inbox Agent - Fax/Briefe/Befunde

Kann:
- Dokumente klassifizieren
- Extrahieren (Überweisung, Labor, Befund)
- Ans Team routen

Inspiration: Luma "Fax Transform (AI)"

V2 Add-on für Praxis-Paket
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DocumentCategory(str, Enum):
    """Dokument-Kategorien"""
    REFERRAL = "referral"  # Überweisung
    LAB_RESULT = "lab_result"  # Laborbefund
    IMAGING_RESULT = "imaging_result"  # Bildgebung
    INSURANCE = "insurance"  # Versicherung
    CORRESPONDENCE = "correspondence"  # Korrespondenz
    OTHER = "other"


@dataclass
class InboxDocument:
    """Eingangsdokument"""
    document_id: str
    source: str  # fax, email, mail, upload
    category: DocumentCategory
    patient_id: Optional[str] = None
    extracted_data: Dict[str, Any] = None
    routing_target: Optional[str] = None  # team member, department
    status: str = "pending"  # pending, processed, routed
    created_at: datetime = None


class PracticeDocumentInboxAgent:
    """
    Document Inbox Agent für Dokumentenverwaltung
    
    Klassifiziert und extrahiert Dokumente, routet ans Team.
    
    V2 Add-on für Praxis-Paket
    """
    
    def __init__(
        self,
        account_id: str,
        document_intelligence_agent=None,
        integration_agent=None
    ):
        self.account_id = account_id
        self.document_intelligence_agent = document_intelligence_agent
        self.integration_agent = integration_agent
        self.documents: List[InboxDocument] = []
    
    def process_document(
        self,
        document_content: bytes,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InboxDocument:
        """
        Verarbeitet eingehendes Dokument
        
        Args:
            document_content: Dokument-Inhalt (Bytes)
            source: Quelle (fax, email, mail, upload)
            metadata: Zusätzliche Metadaten
        
        Returns:
            InboxDocument
        """
        document_id = f"DOC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Via Document Intelligence Agent klassifizieren und extrahieren
        classification = self._classify_document(document_content)
        extracted_data = self._extract_document_data(document_content, classification)
        
        # Patient-ID extrahieren (falls vorhanden)
        patient_id = extracted_data.get("patient_id")
        
        # Routing-Target bestimmen
        routing_target = self._determine_routing_target(classification, extracted_data)
        
        document = InboxDocument(
            document_id=document_id,
            source=source,
            category=classification,
            patient_id=patient_id,
            extracted_data=extracted_data,
            routing_target=routing_target,
            status="processed",
            created_at=datetime.now()
        )
        
        self.documents.append(document)
        return document
    
    def _classify_document(self, document_content: bytes) -> DocumentCategory:
        """
        Klassifiziert Dokument
        
        Returns:
            DocumentCategory
        """
        # TODO: Via Document Intelligence Agent klassifizieren
        # - OCR/Text-Extraktion
        # - NLP-basierte Klassifikation
        
        # Placeholder: Basierend auf Keywords
        content_str = str(document_content).lower()
        
        if any(kw in content_str for kw in ["überweisung", "weisung", "zuweisung"]):
            return DocumentCategory.REFERRAL
        
        if any(kw in content_str for kw in ["labor", "blutwert", "befund"]):
            return DocumentCategory.LAB_RESULT
        
        if any(kw in content_str for kw in ["mrt", "ct", "röntgen", "ultraschall"]):
            return DocumentCategory.IMAGING_RESULT
        
        if any(kw in content_str for kw in ["versicherung", "kasse", "gkv", "pkv"]):
            return DocumentCategory.INSURANCE
        
        return DocumentCategory.OTHER
    
    def _extract_document_data(
        self,
        document_content: bytes,
        category: DocumentCategory
    ) -> Dict[str, Any]:
        """
        Extrahiert strukturierte Daten aus Dokument
        
        Returns:
            Dict mit extrahierten Daten
        """
        # TODO: Via Document Intelligence Agent extrahieren
        # - Patient-ID, Name, Geburtsdatum
        # - Datum, Arzt, Diagnose (falls vorhanden)
        
        return {
            "patient_id": None,  # Wird extrahiert
            "patient_name": None,
            "date": None,
            "provider": None,
            "diagnosis": None
        }
    
    def _determine_routing_target(
        self,
        category: DocumentCategory,
        extracted_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Bestimmt Routing-Target basierend auf Kategorie
        
        Returns:
            Routing-Target (Team-Mitglied, Abteilung)
        """
        routing_map = {
            DocumentCategory.REFERRAL: "reception",
            DocumentCategory.LAB_RESULT: "physician",
            DocumentCategory.IMAGING_RESULT: "physician",
            DocumentCategory.INSURANCE: "billing",
            DocumentCategory.CORRESPONDENCE: "reception",
            DocumentCategory.OTHER: "reception"
        }
        
        return routing_map.get(category)
    
    def route_document(
        self,
        document_id: str
    ) -> Dict[str, Any]:
        """
        Routet Dokument ans Team
        
        Returns:
            Dict mit Status, Routing Info
        """
        document = next((d for d in self.documents if d.document_id == document_id), None)
        
        if not document:
            return {"status": "error", "message": "Dokument nicht gefunden"}
        
        # TODO: Via Integration Agent ans Team routen
        # - Task erstellen
        - E-Mail/Notification senden
        
        document.status = "routed"
        
        return {
            "status": "routed",
            "document_id": document_id,
            "routing_target": document.routing_target,
            "message": f"Dokument wurde an {document.routing_target} geroutet."
        }
