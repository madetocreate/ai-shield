"""
Intelligent Calendar Agent
Provides natural language scheduling, conflict resolution, and smart calendar management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

try:
    from apps.agents.core.error_handling import retry_with_backoff, ErrorHandler
    from apps.agents.core.caching import cached
except ImportError:
    # Fallback if modules don't exist
    def retry_with_backoff(max_retries=3):
        def decorator(func):
            return func
        return decorator
    
    class ErrorHandler:
        pass
    
    def cached(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EventStatus(Enum):
    """Event status"""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    organizer: Optional[str] = None
    priority: EventPriority = EventPriority.MEDIUM
    status: EventStatus = EventStatus.CONFIRMED
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    recurrence: Optional[str] = None
    reminders: List[int] = field(default_factory=list)
    
    def duration_minutes(self) -> int:
        """Calculate event duration in minutes"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    def conflicts_with(self, other: 'CalendarEvent') -> bool:
        """Check if this event conflicts with another event"""
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'description': self.description,
            'location': self.location,
            'attendees': self.attendees,
            'organizer': self.organizer,
            'priority': self.priority.value,
            'status': self.status.value,
            'source': self.source,
            'metadata': self.metadata,
            'recurrence': self.recurrence,
            'reminders': self.reminders,
        }


@dataclass
class TimeSlot:
    """Represents an available time slot"""
    start: datetime
    end: datetime
    duration_minutes: int


@dataclass
class SchedulingPreferences:
    """User scheduling preferences"""
    work_hours_start: str = "09:00"
    work_hours_end: str = "17:00"
    work_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    preferred_meeting_duration: int = 30
    buffer_time: int = 15
    timezone: str = "Europe/Berlin"
    auto_decline_conflicts: bool = False
    require_agenda_for_long_meetings: bool = True
    long_meeting_threshold: int = 60


class CalendarAgent:
    """
    Intelligent Calendar Agent with NLP scheduling, conflict resolution,
    and context-aware event management.
    """
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.events: Dict[str, CalendarEvent] = {}
        self.preferences = SchedulingPreferences()
        self.error_handler = ErrorHandler()
        
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language scheduling request.
        
        Examples:
        - "Schedule a meeting with John tomorrow at 3 PM"
        - "Book 30 minutes for project review next Monday at 10am"
        """
        parsed = {
            'title': None,
            'attendees': [],
            'duration': self.preferences.preferred_meeting_duration,
            'date': None,
            'time': None,
            'location': None,
            'priority': EventPriority.MEDIUM,
        }
        
        # Extract title
        title_patterns = [
            r'(?:schedule|book|create|add)\s+(?:a\s+)?(?:meeting|call|appointment|event)\s+(?:for|about|with)?\s*(.+?)(?:\s+(?:tomorrow|today|next|at|on))',
            r'(?:meeting|call|appointment)\s+(?:with|for)\s*(.+?)(?:\s+(?:tomorrow|today|next|at|on))',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed['title'] = match.group(1).strip()
                break
        
        if not parsed['title']:
            words = text.split()
            if 'with' in words:
                idx = words.index('with')
                parsed['title'] = ' '.join(words[:idx])
            else:
                parsed['title'] = 'Meeting'
        
        # Extract attendees
        attendee_patterns = [
            r'with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'attendees?:\s*([^,]+(?:,\s*[^,]+)*)',
        ]
        for pattern in attendee_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    parsed['attendees'].extend([a.strip() for a in match.split(',')])
        
        # Extract duration
        duration_patterns = [
            r'(\d+)\s*(?:min|minute|minutes|hour|hours)',
            r'(\d+)min',
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed['duration'] = int(match.group(1))
                if 'hour' in match.group(0).lower():
                    parsed['duration'] *= 60
                break
        
        # Extract date/time
        now = datetime.now()
        
        if re.search(r'\btoday\b', text, re.IGNORECASE):
            parsed['date'] = now.date()
        elif re.search(r'\btomorrow\b', text, re.IGNORECASE):
            parsed['date'] = (now + timedelta(days=1)).date()
        elif re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|week)\b', text, re.IGNORECASE):
            match = re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|week)\b', text, re.IGNORECASE)
            if match:
                day_name = match.group(1).lower()
                if day_name == 'week':
                    parsed['date'] = (now + timedelta(days=7 - now.weekday())).date()
                else:
                    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    target_day = days.index(day_name)
                    days_ahead = target_day - now.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    parsed['date'] = (now + timedelta(days=days_ahead)).date()
        
        # Extract time
        time_patterns = [
            r'(\d{1,2}):(\d{2})',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                am_pm = match.group(3) if len(match.groups()) > 2 else None
                
                if am_pm:
                    if am_pm.lower() == 'pm' and hour < 12:
                        hour += 12
                    elif am_pm.lower() == 'am' and hour == 12:
                        hour = 0
                
                parsed['time'] = f"{hour:02d}:{minute:02d}"
                break
        
        # Extract location
        location_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed['location'] = match.group(1).strip()
                break
        
        # Extract priority
        if re.search(r'\b(urgent|important|high priority)\b', text, re.IGNORECASE):
            parsed['priority'] = EventPriority.HIGH
        elif re.search(r'\b(low priority|optional)\b', text, re.IGNORECASE):
            parsed['priority'] = EventPriority.LOW
        
        return parsed
    
    def find_available_slots(
        self,
        date: datetime.date,
        duration_minutes: int,
        exclude_times: Optional[List[Tuple[datetime, datetime]]] = None
    ) -> List[TimeSlot]:
        """Find available time slots for a given date and duration"""
        slots = []
        exclude_times = exclude_times or []
        
        start_hour, start_min = map(int, self.preferences.work_hours_start.split(':'))
        end_hour, end_min = map(int, self.preferences.work_hours_end.split(':'))
        
        if date.weekday() not in self.preferences.work_days:
            return []
        
        day_events = [
            event for event in self.events.values()
            if event.start_time.date() == date
            and event.status != EventStatus.CANCELLED
        ]
        
        current = datetime.combine(date, datetime.min.time().replace(hour=start_hour, minute=start_min))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour, minute=end_min))
        
        while current + timedelta(minutes=duration_minutes) <= end_time:
            slot_end = current + timedelta(minutes=duration_minutes)
            
            has_conflict = False
            for event in day_events:
                if event.conflicts_with(CalendarEvent(
                    id='temp',
                    title='',
                    start_time=current,
                    end_time=slot_end
                )):
                    has_conflict = True
                    break
            
            for excl_start, excl_end in exclude_times:
                if not (slot_end <= excl_start or current >= excl_end):
                    has_conflict = True
                    break
            
            if not has_conflict:
                slots.append(TimeSlot(
                    start=current,
                    end=slot_end,
                    duration_minutes=duration_minutes
                ))
            
            current += timedelta(minutes=duration_minutes + self.preferences.buffer_time)
        
        return slots
    
    def suggest_optimal_time(
        self,
        duration_minutes: int,
        preferred_date: Optional[datetime.date] = None,
        preferred_time: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[TimeSlot]:
        """Suggest optimal meeting time"""
        start_date = preferred_date or datetime.now().date()
        
        for day_offset in range(14):
            check_date = start_date + timedelta(days=day_offset)
            slots = self.find_available_slots(check_date, duration_minutes)
            
            if slots:
                if preferred_time:
                    try:
                        hour, minute = map(int, preferred_time.split(':'))
                        preferred_dt = datetime.combine(check_date, datetime.min.time().replace(hour=hour, minute=minute))
                        
                        for slot in slots:
                            if abs((slot.start - preferred_dt).total_seconds()) < 3600:
                                return slot
                    except:
                        pass
                
                return slots[0]
        
        return None
    
    def create_event_from_natural_language(self, text: str, organizer: str) -> CalendarEvent:
        """Create a calendar event from natural language input"""
        parsed = self.parse_natural_language(text)
        
        date = parsed['date'] or datetime.now().date()
        
        if parsed['time']:
            hour, minute = map(int, parsed['time'].split(':'))
            start_time = datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
        else:
            slot = self.suggest_optimal_time(parsed['duration'], date)
            if slot:
                start_time = slot.start
            else:
                hour, minute = map(int, self.preferences.work_hours_start.split(':'))
                start_time = datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
        
        end_time = start_time + timedelta(minutes=parsed['duration'])
        
        conflicts = self.check_conflicts(start_time, end_time)
        if conflicts:
            slot = self.suggest_optimal_time(parsed['duration'], date)
            if slot:
                start_time = slot.start
                end_time = slot.end
        
        event = CalendarEvent(
            id=f"event_{datetime.now().timestamp()}",
            title=parsed['title'] or 'Meeting',
            start_time=start_time,
            end_time=end_time,
            description=parsed.get('description'),
            location=parsed.get('location'),
            attendees=parsed.get('attendees', []),
            organizer=organizer,
            priority=parsed.get('priority', EventPriority.MEDIUM),
            status=EventStatus.CONFIRMED,
            source='calendar_agent',
            metadata={'created_from_nlp': True, 'original_text': text}
        )
        
        if event.duration_minutes() >= self.preferences.long_meeting_threshold:
            if self.preferences.require_agenda_for_long_meetings:
                event.metadata['agenda_required'] = True
        
        self.events[event.id] = event
        return event
    
    def check_conflicts(self, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Check for scheduling conflicts"""
        temp_event = CalendarEvent(
            id='temp',
            title='',
            start_time=start_time,
            end_time=end_time
        )
        
        conflicts = []
        for event in self.events.values():
            if event.status != EventStatus.CANCELLED and event.conflicts_with(temp_event):
                conflicts.append(event)
        
        return conflicts
    
    def resolve_conflicts(
        self,
        new_event: CalendarEvent,
        strategy: str = "suggest_alternative"
    ) -> Dict[str, Any]:
        """Resolve scheduling conflicts"""
        conflicts = self.check_conflicts(new_event.start_time, new_event.end_time)
        
        if not conflicts:
            return {'resolved': True, 'conflicts': []}
        
        result = {
            'resolved': False,
            'conflicts': [c.to_dict() for c in conflicts],
            'suggestions': []
        }
        
        if strategy == "suggest_alternative":
            for _ in range(3):
                slot = self.suggest_optimal_time(
                    new_event.duration_minutes(),
                    new_event.start_time.date()
                )
                if slot:
                    alt_event = CalendarEvent(
                        id=new_event.id,
                        title=new_event.title,
                        start_time=slot.start,
                        end_time=slot.end,
                        description=new_event.description,
                        location=new_event.location,
                        attendees=new_event.attendees,
                        organizer=new_event.organizer,
                        priority=new_event.priority,
                        status=new_event.status,
                        source=new_event.source,
                        metadata=new_event.metadata
                    )
                    
                    if not self.check_conflicts(alt_event.start_time, alt_event.end_time):
                        result['suggestions'].append(alt_event.to_dict())
                        result['resolved'] = True
                        break
        
        return result
    
    def get_upcoming_events(self, days: int = 7) -> List[CalendarEvent]:
        """Get upcoming events for the next N days"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        upcoming = [
            event for event in self.events.values()
            if event.start_time >= now
            and event.start_time <= end_date
            and event.status != EventStatus.CANCELLED
        ]
        
        return sorted(upcoming, key=lambda e: e.start_time)
    
    def get_day_summary(self, date: datetime.date) -> Dict[str, Any]:
        """Get summary of events for a specific day"""
        day_events = [
            event for event in self.events.values()
            if event.start_time.date() == date
            and event.status != EventStatus.CANCELLED
        ]
        
        total_duration = sum(e.duration_minutes() for e in day_events)
        work_hours = 8 * 60
        
        return {
            'date': date.isoformat(),
            'total_events': len(day_events),
            'total_duration_minutes': total_duration,
            'utilization_percent': min(100, (total_duration / work_hours) * 100),
            'events': [e.to_dict() for e in sorted(day_events, key=lambda e: e.start_time)],
            'focus_time_available': max(0, work_hours - total_duration),
        }
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update scheduling preferences"""
        for key, value in preferences.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
    
    def add_event(self, event: CalendarEvent):
        """Add an event to the calendar"""
        conflicts = self.check_conflicts(event.start_time, event.end_time)
        if conflicts and not self.preferences.auto_decline_conflicts:
            raise ValueError(f"Event conflicts with {len(conflicts)} existing events")
        
        self.events[event.id] = event
        return event
    
    def remove_event(self, event_id: str):
        """Remove an event from the calendar"""
        if event_id in self.events:
            del self.events[event_id]
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[CalendarEvent]:
        """Update an existing event"""
        if event_id not in self.events:
            return None
        
        event = self.events[event_id]
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        return event
