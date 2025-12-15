"""
Restaurant Inventory Procurement Agent - Bestände & Nachbestellung

Kann:
- "Bier/Wein/Verpackung fast leer" erkennen
- Lieferant/Bestellvorschlag generieren
- Ggf. per Integration ordern

V2 Add-on für Gastronomie-Paket
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class InventoryStatus(str, Enum):
    """Bestands-Status"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ORDERED = "ordered"
    ON_THE_WAY = "on_the_way"


@dataclass
class InventoryItem:
    """Lagerbestand-Item"""
    item_id: str
    name: str
    category: str  # Getränk, Verpackung, Lebensmittel, etc.
    current_stock: float
    unit: str  # Liter, Stück, kg, etc.
    min_stock: float  # Mindestbestand
    max_stock: float  # Maximalbestand
    status: InventoryStatus = InventoryStatus.IN_STOCK
    supplier: Optional[str] = None
    last_ordered: Optional[datetime] = None


@dataclass
class ProcurementOrder:
    """Bestellvorschlag"""
    order_id: str
    items: List[Dict[str, Any]]  # item_id, quantity, supplier
    total_estimated_cost: float = 0.0
    urgency: str = "normal"  # normal, urgent, critical
    created_at: datetime = None


class RestaurantInventoryProcurementAgent:
    """
    Inventory Procurement Agent für Bestandsverwaltung
    
    V2 Add-on für Gastronomie-Paket
    """
    
    def __init__(self, account_id: str, integration_agent=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.inventory: List[InventoryItem] = []
        self.suppliers: Dict[str, Dict[str, Any]] = {}
    
    def check_inventory_status(
        self,
        item_name: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[InventoryItem]:
        """
        Prüft Bestandsstatus
        
        Returns:
            Liste von Items mit Status
        """
        filtered = self.inventory
        
        if item_name:
            filtered = [i for i in filtered if item_name.lower() in i.name.lower()]
        
        if category:
            filtered = [i for i in filtered if i.category == category]
        
        # Status aktualisieren basierend auf Bestand
        for item in filtered:
            if item.current_stock <= 0:
                item.status = InventoryStatus.OUT_OF_STOCK
            elif item.current_stock < item.min_stock:
                item.status = InventoryStatus.LOW_STOCK
            else:
                item.status = InventoryStatus.IN_STOCK
        
        return filtered
    
    def generate_procurement_order(
        self,
        low_stock_items: Optional[List[InventoryItem]] = None
    ) -> ProcurementOrder:
        """
        Generiert Bestellvorschlag
        
        Args:
            low_stock_items: Items die nachbestellt werden sollen
        
        Returns:
            ProcurementOrder
        """
        if not low_stock_items:
            # Automatisch Items mit niedrigem Bestand finden
            low_stock_items = [
                i for i in self.inventory
                if i.status == InventoryStatus.LOW_STOCK or i.status == InventoryStatus.OUT_OF_STOCK
            ]
        
        order_id = f"PROC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        order_items = []
        total_cost = 0.0
        
        for item in low_stock_items:
            # Berechne Bestellmenge (bis Max-Bestand)
            quantity = item.max_stock - item.current_stock
            
            if quantity > 0:
                # TODO: Preis vom Lieferanten holen
                estimated_price = 0.0  # Placeholder
                
                order_items.append({
                    "item_id": item.item_id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit": item.unit,
                    "supplier": item.supplier,
                    "estimated_price": estimated_price
                })
                
                total_cost += estimated_price * quantity
        
        # Urgency bestimmen
        urgency = "normal"
        if any(i.status == InventoryStatus.OUT_OF_STOCK for i in low_stock_items):
            urgency = "critical"
        elif len(low_stock_items) > 5:
            urgency = "urgent"
        
        order = ProcurementOrder(
            order_id=order_id,
            items=order_items,
            total_estimated_cost=total_cost,
            urgency=urgency,
            created_at=datetime.now()
        )
        
        return order
    
    def process_procurement_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Nachbestellungs-Anfrage
        
        Returns:
            Dict mit Status, Order Info
        """
        # TODO: NLP um Item-Namen zu extrahieren
        # TODO: Bestand prüfen
        # TODO: Bestellvorschlag generieren
        
        return {
            "status": "processed",
            "message": "Bestellvorschlag wurde erstellt."
        }
    
    def place_order(
        self,
        order: ProcurementOrder
    ) -> Dict[str, Any]:
        """
        Bestellung aufgeben (via Integration)
        
        Returns:
            Dict mit Status, Order ID
        """
        # TODO: Via Integration Agent Bestellung aufgeben
        # TODO: Status auf ORDERED setzen
        
        return {
            "status": "ordered",
            "order_id": order.order_id,
            "message": "Bestellung wurde aufgegeben."
        }
