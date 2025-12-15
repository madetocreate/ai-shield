"""
API Endpoints for Calendar Agent
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

try:
    from apps.agents.core.calendar_agent import (
        CalendarAgent,
        CalendarEvent,
        EventPriority,
        EventStatus,
    )
except ImportError:
    # Fallback
    pass

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


class NaturalLanguageRequest(BaseModel):
    text: str = Field(..., description="Natural language scheduling request")
    organizer: str = Field(..., description="Event organizer")
    account_id: str = Field(..., description="Account ID")


class EventCreateRequest(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    organizer: Optional[str] = None
    priority: str = "medium"
    status: str = "confirmed"
    source: Optional[str] = None
    recurrence: Optional[str] = None
    reminders: List[int] = Field(default_factory=list)


# In-memory storage (should be replaced with database)
_calendar_agents: Dict[str, CalendarAgent] = {}


def get_calendar_agent(account_id: str) -> CalendarAgent:
    """Get or create calendar agent for account"""
    if account_id not in _calendar_agents:
        _calendar_agents[account_id] = CalendarAgent(account_id)
    return _calendar_agents[account_id]


@router.post("/schedule/natural-language")
async def schedule_from_natural_language(request: NaturalLanguageRequest):
    """Schedule an event from natural language input"""
    try:
        agent = get_calendar_agent(request.account_id)
        event = agent.create_event_from_natural_language(request.text, request.organizer)
        
        return {
            "success": True,
            "event": event.to_dict(),
            "message": f"Event '{event.title}' scheduled for {event.start_time.strftime('%Y-%m-%d %H:%M')}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events")
async def get_events(account_id: str = Query(...), days: int = Query(7)):
    """Get upcoming events"""
    try:
        agent = get_calendar_agent(account_id)
        events = agent.get_upcoming_events(days)
        
        return {
            "success": True,
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/day/{date_str}")
async def get_day_summary(date_str: str, account_id: str = Query(...)):
    """Get summary for a specific day"""
    try:
        date_obj = datetime.fromisoformat(date_str).date()
        agent = get_calendar_agent(account_id)
        summary = agent.get_day_summary(date_obj)
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slots/suggest")
async def suggest_optimal_time(
    duration_minutes: int = Query(...),
    account_id: str = Query(...),
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
):
    """Suggest optimal meeting time"""
    try:
        agent = get_calendar_agent(account_id)
        pref_date = datetime.fromisoformat(preferred_date).date() if preferred_date else None
        slot = agent.suggest_optimal_time(duration_minutes, pref_date, preferred_time)
        
        if not slot:
            return {
                "success": False,
                "message": "No available slots found"
            }
        
        return {
            "success": True,
            "slot": {
                "start": slot.start.isoformat(),
                "end": slot.end.isoformat(),
                "duration_minutes": slot.duration_minutes
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
