"""
Cost API Endpoints - FastAPI Endpoints für Cost Tracking

Endpoints:
- POST /api/v1/costs/track - Kosten tracken
- GET /api/v1/costs/{account_id} - Kosten für Account
- GET /api/v1/costs/{account_id}/breakdown - Cost Breakdown
- GET /api/v1/costs/{account_id}/alerts - Cost Alerts
- POST /api/v1/costs/{account_id}/threshold - Alert Threshold setzen
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel
from apps.agents.core.cost_tracking import (
    get_cost_tracker,
    CostType
)

router = APIRouter(prefix="/api/v1/costs", tags=["costs"])


# Request Models
class TrackCostRequest(BaseModel):
    account_id: str
    cost_type: str
    amount: float
    quantity: float = 1.0
    unit_price: Optional[float] = None
    agent_name: Optional[str] = None
    metadata: Dict[str, Any] = {}


class SetThresholdRequest(BaseModel):
    period: str  # daily, weekly, monthly
    threshold: float


# Response Models
class CostBreakdownResponse(BaseModel):
    account_id: str
    period: str
    total: float
    breakdown: Dict[str, Dict[str, float]]


@router.post("/track")
def track_cost(request: TrackCostRequest):
    """Trackt Kosten"""
    tracker = get_cost_tracker()
    
    try:
        cost_type = CostType(request.cost_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Cost Type: {request.cost_type}")
    
    tracker.track_cost(
        account_id=request.account_id,
        cost_type=cost_type,
        amount=request.amount,
        quantity=request.quantity,
        unit_price=request.unit_price,
        agent_name=request.agent_name,
        metadata=request.metadata
    )
    
    return {"success": True, "message": "Cost tracked"}


@router.get("/{account_id}")
def get_costs(
    account_id: str,
    period: str = Query("monthly", description="daily, weekly, monthly"),
    agent_name: Optional[str] = Query(None),
    cost_type: Optional[str] = Query(None)
):
    """Holt Kosten für Account"""
    tracker = get_cost_tracker()
    
    cost_type_enum = None
    if cost_type:
        try:
            cost_type_enum = CostType(cost_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Cost Type: {cost_type}")
    
    total = tracker.get_total_cost(
        account_id=account_id,
        period=period,
        agent_name=agent_name,
        cost_type=cost_type_enum
    )
    
    return {
        "account_id": account_id,
        "period": period,
        "total": total,
        "agent_name": agent_name,
        "cost_type": cost_type
    }


@router.get("/{account_id}/breakdown", response_model=CostBreakdownResponse)
def get_cost_breakdown(
    account_id: str,
    period: str = Query("monthly")
):
    """Holt Cost Breakdown"""
    tracker = get_cost_tracker()
    breakdown = tracker.get_cost_breakdown(account_id, period=period)
    
    return CostBreakdownResponse(
        account_id=breakdown["account_id"],
        period=breakdown["period"],
        total=breakdown["total"],
        breakdown=breakdown["breakdown"]
    )


@router.get("/{account_id}/alerts")
def get_cost_alerts(account_id: str):
    """Holt Cost Alerts"""
    tracker = get_cost_tracker()
    alerts = tracker.get_active_alerts(account_id=account_id)
    
    return {
        "alerts": [
            {
                "account_id": a.account_id,
                "threshold": a.threshold,
                "current_cost": a.current_cost,
                "period": a.period,
                "alert_level": a.alert_level,
                "timestamp": a.timestamp.isoformat()
            }
            for a in alerts
        ],
        "count": len(alerts)
    }


@router.post("/{account_id}/threshold")
def set_alert_threshold(account_id: str, request: SetThresholdRequest):
    """Setzt Alert Threshold"""
    tracker = get_cost_tracker()
    tracker.set_alert_threshold(account_id, request.period, request.threshold)
    return {"success": True, "message": f"Threshold für {request.period} gesetzt"}
