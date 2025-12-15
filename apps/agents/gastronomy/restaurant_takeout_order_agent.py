"""
Restaurant Takeout Order Agent - Phone/SMS/Chat Besteller

Kann:
- Takeout/Delivery-Bestellung aufnehmen
- Variationen/Extras, Upsell
- Abholzeit, Zahlungslink/"pay at pickup"
- Order-Summary an Küche/POS

Inspiration: SoundHound Smart Ordering, Toast↔Incept AI
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class OrderItem:
    """Bestellposition"""
    dish_name: str
    quantity: int
    variations: List[str] = None  # z.B. "ohne Zwiebeln", "extra scharf"
    extras: List[str] = None  # z.B. "extra Käse"
    price: float = 0.0


@dataclass
class TakeoutOrder:
    """Takeout-Bestellung"""
    order_id: str
    items: List[OrderItem]
    customer_name: str
    phone: str
    email: Optional[str] = None
    pickup_time: datetime
    payment_method: str  # "pay_at_pickup", "online", "card"
    total_price: float = 0.0
    status: str = "pending"  # pending, confirmed, preparing, ready, completed
    created_at: datetime = None


class RestaurantTakeoutOrderAgent:
    """
    Takeout Order Agent für Bestellungen
    
    Handhabt Bestellaufnahme, Upselling, POS-Integration.
    """
    
    def __init__(self, account_id: str, integration_agent=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.menu: Dict[str, Dict[str, Any]] = {}  # dish_name -> info
        self._load_menu()
    
    def _load_menu(self):
        """Lädt Menü aus Knowledge Base"""
        # TODO: Via Knowledge Base Agent laden
        pass
    
    def start_order(
        self,
        customer_name: str,
        phone: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TakeoutOrder:
        """
        Startet neue Bestellung
        
        Returns:
            TakeoutOrder
        """
        order_id = f"TO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        order = TakeoutOrder(
            order_id=order_id,
            items=[],
            customer_name=customer_name,
            phone=phone,
            pickup_time=datetime.now() + timedelta(minutes=30),  # Default 30 Min
            payment_method="pay_at_pickup",
            created_at=datetime.now()
        )
        
        return order
    
    def add_item(
        self,
        order: TakeoutOrder,
        dish_name: str,
        quantity: int = 1,
        variations: Optional[List[str]] = None,
        extras: Optional[List[str]] = None
    ) -> OrderItem:
        """
        Fügt Position zur Bestellung hinzu
        
        Returns:
            OrderItem
        """
        # TODO: Menü validieren
        # TODO: Preis berechnen
        
        item = OrderItem(
            dish_name=dish_name,
            quantity=quantity,
            variations=variations or [],
            extras=extras or [],
            price=0.0  # TODO: Aus Menü berechnen
        )
        
        order.items.append(item)
        order.total_price += item.price * quantity
        
        return item
    
    def suggest_upsell(
        self,
        order: TakeoutOrder
    ) -> List[str]:
        """
        Schlägt Upsell-Artikel vor
        
        Returns:
            Liste von Vorschlägen
        """
        suggestions = []
        
        # TODO: Basierend auf bereits bestellten Items Vorschläge machen
        # z.B. "Möchten Sie noch ein Getränk dazu?"
        
        return suggestions
    
    def confirm_order(
        self,
        order: TakeoutOrder
    ) -> Dict[str, Any]:
        """
        Bestätigt Bestellung und sendet an POS/Küche
        
        Returns:
            Dict mit Status, Payment Link, etc.
        """
        # TODO: Via Integration Agent an POS senden
        # TODO: Payment Link generieren falls online payment
        # TODO: SMS/E-Mail Bestätigung senden
        
        order.status = "confirmed"
        
        return {
            "status": "confirmed",
            "order_id": order.order_id,
            "pickup_time": order.pickup_time.isoformat(),
            "total_price": order.total_price,
            "payment_link": None,  # Falls online payment
            "message": f"Bestellung {order.order_id} bestätigt. Abholung um {order.pickup_time.strftime('%H:%M')} Uhr."
        }
    
    def handle_order_query(
        self,
        query: str,
        order: Optional[TakeoutOrder] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Verarbeitet Bestellanfrage
        
        Returns:
            Antwort-Text
        """
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["bestellen", "haben", "kann ich"]):
            if not order:
                return "Gerne nehme ich Ihre Bestellung auf. Was möchten Sie bestellen?"
            else:
                return "Was möchten Sie noch hinzufügen?"
        
        if any(kw in query_lower for kw in ["fertig", "abschließen", "bestätigen"]):
            if order and order.items:
                result = self.confirm_order(order)
                return result["message"]
            else:
                return "Ihre Bestellung ist noch leer. Was möchten Sie bestellen?"
        
        # TODO: Weitere Query-Handling
        
        return "Wie kann ich Ihnen bei Ihrer Bestellung helfen?"
