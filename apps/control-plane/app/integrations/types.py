"""
Type definitions for integrations module.
"""
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Provider(str, Enum):
    """Supported integration providers."""
    # General
    GOOGLE = "google"
    GOOGLE_DRIVE = "google-drive"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    HUBSPOT = "hubspot"
    ZENDESK = "zendesk"
    NOTION = "notion"
    SLACK = "slack"
    WHATSAPP = "whatsapp"  # Meta/WhatsApp Business
    
    # Hotel & Booking Platforms
    BOOKING_COM = "booking-com"
    AIRBNB = "airbnb"
    EXPEDIA = "expedia"
    HRS = "hrs"
    HOTELS_COM = "hotels-com"
    TRIVAGO = "trivago"
    AGODA = "agoda"
    PADEL = "padel"  # Padel (Spanien)
    
    # Real Estate Platforms
    IMMOBILIENSCOUT24 = "immobilienscout24"
    IDEALISTA = "idealista"
    IMMOWELT = "immowelt"
    EBAY_KLEINANZEIGEN = "ebay-kleinanzeigen"
    WOHNUNG_DE = "wohnung-de"
    IMMONET = "immonet"
    FOTOCASA = "fotocasa"  # Spanien
    HABITACLIA = "habitaclia"  # Spanien
    
    # Health & Practice Management Platforms
    MICROSOFT_365 = "microsoft-365"  # Outlook Calendar, Email
    ZOOM = "zoom"  # Telemedizin, Video-Konsultationen
    CALENDLY = "calendly"  # Terminbuchung
    DOXY_ME = "doxy-me"  # Telemedizin
    SIMPLEPRACTICE = "simplepractice"  # Practice Management
    JANE_APP = "jane-app"  # Practice Management
    EPIC_MYCHART = "epic-mychart"  # EHR Integration
    DOCTOLIB = "doctolib"  # Terminbuchung (Europa)
    
    # Apple Services
    APPLE_SIGNIN = "apple-signin"  # Apple ID Authentication
    ICLOUD_CALENDAR = "icloud-calendar"  # iCloud Calendar
    ICLOUD_DRIVE = "icloud-drive"  # iCloud Drive
    APPLE_PUSH_NOTIFICATIONS = "apple-push-notifications"  # APNs
    
    # Review Platforms
    TRUSTPILOT = "trustpilot"  # Trustpilot Reviews
    TRIPADVISOR = "tripadvisor"  # Tripadvisor Reviews
    GOOGLE_REVIEWS = "google-reviews"  # Google My Business Reviews
    YELP = "yelp"  # Yelp Reviews
    FACEBOOK_REVIEWS = "facebook-reviews"  # Facebook Reviews


class ConnectionStatus(str, Enum):
    """Connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"


class Connection(BaseModel):
    """Connection model."""
    tenant_id: str = Field(..., description="Tenant/Workspace ID")
    provider: Provider = Field(..., description="Provider name")
    nango_connection_id: Optional[str] = Field(None, description="Nango connection ID")
    status: ConnectionStatus = Field(ConnectionStatus.DISCONNECTED, description="Connection status")
    scopes: list[str] = Field(default_factory=list, description="Granted scopes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApprovalRequest(BaseModel):
    """Approval request for write operations."""
    request_id: str = Field(..., description="Unique request ID")
    tenant_id: str = Field(..., description="Tenant/Workspace ID")
    provider: Provider = Field(..., description="Provider name")
    connection_id: str = Field(..., description="Connection ID")
    operation: str = Field(..., description="Operation name (e.g., 'calendar_create_event')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    preview: Optional[Dict[str, Any]] = Field(None, description="Preview of what will happen")
    status: str = Field("pending", description="Approval status: pending, approved, rejected")
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
