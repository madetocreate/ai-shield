"""
Restaurant Voice Host Agent - Telefon-Host + Chat-Host

Kann:
- Reservierungen annehmen/ändern/stornieren
- Öffnungszeiten/Adresse/Parken beantworten
- "Habt ihr heute noch was frei?" beantworten
- Bei Bedarf an Team eskalieren

Inspiration: Slang AI, SevenRooms Voice AI, Yelp AI Host
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, date, time


@dataclass
class ReservationRequest:
    """Reservierungsanfrage"""
    date: date
    time: time
    guests: int
    name: str
    phone: str
    email: Optional[str] = None
    special_requests: Optional[str] = None


@dataclass
class AvailabilityCheck:
    """Verfügbarkeitsprüfung"""
    date: date
    time: Optional[time] = None
    guests: int = 2
    available: bool = False
    alternatives: List[Dict[str, Any]] = None  # Alternative Zeiten


class RestaurantVoiceHostAgent:
    """
    Voice Host Agent für Restaurant-Empfang
    
    Handhabt Reservierungen, Verfügbarkeitsanfragen und allgemeine Infos.
    """
    
    def __init__(self, account_id: str, integration_agent=None, communications_supervisor=None):
        self.account_id = account_id
        self.integration_agent = integration_agent
        self.communications_supervisor = communications_supervisor
        self.restaurant_info = self._load_restaurant_info()
        
        # Voice Integration
        from apps.agents.core.voice_integration import get_text_to_voice, get_voice_command_processor
        from apps.agents.core.multi_language import get_localization_manager, Language
        self.tts = get_text_to_voice()
        self.voice_commands = get_voice_command_processor()
        self.localization = get_localization_manager()
        self.default_language = Language.GERMAN
        
        # Registriere Voice Commands
        self._setup_voice_commands()
    
    def _load_restaurant_info(self) -> Dict[str, Any]:
        """Lädt Restaurant-Informationen"""
        # TODO: Aus Knowledge Base laden
        return {
            "name": "Restaurant",
            "address": "",
            "phone": "",
            "opening_hours": {
                "monday": {"open": "11:00", "close": "22:00"},
                "tuesday": {"open": "11:00", "close": "22:00"},
                "wednesday": {"open": "11:00", "close": "22:00"},
                "thursday": {"open": "11:00", "close": "22:00"},
                "friday": {"open": "11:00", "close": "23:00"},
                "saturday": {"open": "11:00", "close": "23:00"},
                "sunday": {"open": "12:00", "close": "21:00"},
            },
            "parking": "Parkplätze verfügbar",
        }
    
    def _setup_voice_commands(self):
        """Setzt Voice Commands auf"""
        async def handle_reservation_command(text, context):
            return await self.handle_reservation_request(text, context)
        
        async def handle_availability_command(text, context):
            return await self.check_availability_today()
        
        self.voice_commands.register_command("reservierung", handle_reservation_command)
        self.voice_commands.register_command("termin", handle_reservation_command)
        self.voice_commands.register_command("verfügbar", handle_availability_command)
        self.voice_commands.register_command("frei", handle_availability_command)
    
    async def respond_with_voice(
        self,
        text: str,
        language: Optional[str] = None,
        channel: str = "phone"
    ) -> Dict[str, Any]:
        """
        Antwortet mit Voice (Text-to-Speech)
        
        Args:
            text: Antwort-Text
            language: Sprache (optional)
            channel: Channel (phone, chat, etc.)
        
        Returns:
            Dict mit text und audio_data
        """
        try:
            # Synthetisiere Voice
            audio = await self.tts.synthesize(
                text=text,
                voice="alloy",  # OpenAI TTS Voice
                language=language or self.default_language.value
            )
            
            return {
                "text": text,
                "audio_data": audio.audio_data,
                "audio_format": audio.format,
                "duration": audio.duration
            }
        except Exception as e:
            # Fallback: Nur Text
            return {
                "text": text,
                "audio_data": None,
                "error": str(e)
            }
    
    async def process_voice_input(
        self,
        audio_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Voice-Input (Voice-to-Text + Command Processing)
        
        Args:
            audio_data: Audio-Daten
            context: Kontext
        
        Returns:
            Dict mit transcription und result
        """
        from apps.agents.core.voice_integration import get_voice_to_text
        
        vtt = get_voice_to_text()
        
        # Transkribiere Audio
        transcription = await vtt.transcribe(audio_data)
        
        # Verarbeite Command
        command_result = await self.voice_commands.process_voice_command(
            audio_data,
            context=context
        )
        
        return {
            "transcription": transcription.text,
            "language": transcription.language,
            "command_result": command_result
        }
    
    async def check_availability_today(self) -> Dict[str, Any]:
        """Prüft Verfügbarkeit für heute"""
        from datetime import date
        today = date.today()
        availability = self.check_availability(today)
        return {
            "date": today.isoformat(),
            "available": availability.available,
            "alternatives": availability.alternatives
        }
    
    def handle_reservation_request(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Reservierungsanfrage
        
        Returns:
            Dict mit Status, Reservation ID, Bestätigung
        """
        # TODO: NLP um Datum, Zeit, Gäste, Name, Telefon zu extrahieren
        # TODO: Verfügbarkeit prüfen via Integration Agent
        # TODO: Reservierung buchen via Integration Agent (OpenTable/SevenRooms/etc.)
        
        return {
            "status": "success",
            "message": "Reservierung erfolgreich gebucht",
            "reservation_id": None,  # Wird von Integration gesetzt
        }
    
    def check_availability(
        self,
        date: date,
        time: Optional[time] = None,
        guests: int = 2
    ) -> AvailabilityCheck:
        """
        Prüft Verfügbarkeit für Datum/Zeit/Gäste
        
        Returns:
            AvailabilityCheck mit Ergebnis
        """
        # TODO: Via Integration Agent Verfügbarkeit prüfen
        # TODO: Alternative Zeiten vorschlagen wenn nicht verfügbar
        
        return AvailabilityCheck(
            date=date,
            time=time,
            guests=guests,
            available=True,
            alternatives=[]
        )
    
    def get_opening_hours(self, day: Optional[str] = None) -> str:
        """Gibt Öffnungszeiten zurück"""
        if day:
            hours = self.restaurant_info["opening_hours"].get(day.lower())
            if hours:
                return f"Am {day} haben wir von {hours['open']} bis {hours['close']} Uhr geöffnet."
        else:
            # Alle Öffnungszeiten
            hours_str = "Unsere Öffnungszeiten:\n"
            for day_name, hours in self.restaurant_info["opening_hours"].items():
                hours_str += f"{day_name.capitalize()}: {hours['open']} - {hours['close']} Uhr\n"
            return hours_str
    
    def get_address_info(self) -> str:
        """Gibt Adress-Informationen zurück"""
        info = self.restaurant_info
        return f"Wir befinden uns unter:\n{info['address']}\n\n{info.get('parking', '')}"
    
    def handle_general_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Beantwortet allgemeine Anfragen
        
        Returns:
            Antwort-Text
        """
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["öffnungszeit", "wann", "geöffnet"]):
            return self.get_opening_hours()
        
        if any(kw in query_lower for kw in ["adresse", "wo", "finden", "parken"]):
            return self.get_address_info()
        
        if any(kw in query_lower for kw in ["telefon", "kontakt", "erreichen"]):
            return f"Sie erreichen uns unter: {self.restaurant_info.get('phone', '')}"
        
        # Fallback
        return "Gerne helfe ich Ihnen weiter. Was möchten Sie wissen?"
