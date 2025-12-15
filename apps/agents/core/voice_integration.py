"""
Voice Integration - Verbesserte Voice Integration

Features:
- Voice-to-Text (Speech Recognition)
- Text-to-Voice (TTS)
- Voice Commands
- Real-time Voice Processing
- Multi-Language Voice Support
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import os
import logging
import asyncio

logger = logging.getLogger(__name__)


class VoiceProvider(str, Enum):
    """Voice Provider"""
    OPENAI_WHISPER = "openai_whisper"  # Speech-to-Text
    OPENAI_TTS = "openai_tts"  # Text-to-Speech
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    TWILIO = "twilio"
    ELEVENLABS = "elevenlabs"


@dataclass
class SpeechToTextResult:
    """Speech-to-Text Ergebnis"""
    text: str
    language: Optional[str] = None
    confidence: float = 1.0
    duration: Optional[float] = None  # Sekunden


@dataclass
class TextToSpeechResult:
    """Text-to-Speech Ergebnis"""
    audio_data: bytes
    format: str = "mp3"  # mp3, wav, ogg
    duration: Optional[float] = None  # Sekunden


class VoiceToText:
    """
    Voice-to-Text (Speech Recognition)
    
    Konvertiert Audio zu Text.
    """
    
    def __init__(self, provider: VoiceProvider = VoiceProvider.OPENAI_WHISPER):
        """
        Initialisiert Voice-to-Text
        
        Args:
            provider: Voice Provider
        """
        self.provider = provider
        self._setup_provider()
    
    def _setup_provider(self):
        """Setzt Provider auf"""
        if self.provider == VoiceProvider.OPENAI_WHISPER:
            try:
                import openai
                self.client = openai
            except ImportError:
                logger.warning("OpenAI nicht verfügbar, nutze Fallback")
                self.client = None
        elif self.provider == VoiceProvider.GOOGLE_CLOUD:
            try:
                from google.cloud import speech
                self.client = speech.SpeechClient()
            except ImportError:
                logger.warning("Google Cloud Speech nicht verfügbar")
                self.client = None
        else:
            self.client = None
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "mp3"
    ) -> SpeechToTextResult:
        """
        Transkribiert Audio zu Text
        
        Args:
            audio_data: Audio-Daten (Bytes)
            language: Sprache (optional, wird erkannt falls None)
            format: Audio-Format (mp3, wav, ogg, etc.)
        
        Returns:
            SpeechToTextResult
        """
        if self.provider == VoiceProvider.OPENAI_WHISPER:
            return await self._transcribe_openai(audio_data, language, format)
        elif self.provider == VoiceProvider.GOOGLE_CLOUD:
            return await self._transcribe_google(audio_data, language, format)
        else:
            raise ValueError(f"Provider {self.provider} nicht unterstützt")
    
    async def _transcribe_openai(
        self,
        audio_data: bytes,
        language: Optional[str],
        format: str
    ) -> SpeechToTextResult:
        """Transkribiert mit OpenAI Whisper"""
        try:
            if not self.client:
                raise ValueError("OpenAI Client nicht verfügbar")
            
            # Speichere temporäre Datei
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            try:
                with open(tmp_file_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json"
                    )
                
                return SpeechToTextResult(
                    text=transcript.text,
                    language=transcript.language,
                    confidence=1.0
                )
            finally:
                os.unlink(tmp_file_path)
        except Exception as e:
            logger.error(f"OpenAI Whisper Fehler: {e}")
            raise
    
    async def _transcribe_google(
        self,
        audio_data: bytes,
        language: Optional[str],
        format: str
    ) -> SpeechToTextResult:
        """Transkribiert mit Google Cloud Speech"""
        try:
            if not self.client:
                raise ValueError("Google Cloud Speech Client nicht verfügbar")
            
            from google.cloud.speech import RecognitionConfig, RecognitionAudio
            
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16 if format == "wav" else RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=16000,
                language_code=language or "de-DE",
                enable_automatic_punctuation=True,
            )
            
            audio = RecognitionAudio(content=audio_data)
            
            response = self.client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                return SpeechToTextResult(
                    text=result.alternatives[0].transcript,
                    language=language,
                    confidence=result.alternatives[0].confidence
                )
            else:
                return SpeechToTextResult(text="", language=language, confidence=0.0)
        except Exception as e:
            logger.error(f"Google Cloud Speech Fehler: {e}")
            raise


class TextToVoice:
    """
    Text-to-Voice (TTS)
    
    Konvertiert Text zu Audio.
    """
    
    def __init__(self, provider: VoiceProvider = VoiceProvider.OPENAI_TTS):
        """
        Initialisiert Text-to-Voice
        
        Args:
            provider: Voice Provider
        """
        self.provider = provider
        self._setup_provider()
    
    def _setup_provider(self):
        """Setzt Provider auf"""
        if self.provider == VoiceProvider.OPENAI_TTS:
            try:
                import openai
                self.client = openai
            except ImportError:
                logger.warning("OpenAI nicht verfügbar")
                self.client = None
        elif self.provider == VoiceProvider.ELEVENLABS:
            try:
                import requests
                self.client = requests
            except ImportError:
                logger.warning("Requests nicht verfügbar für ElevenLabs")
                self.client = None
        else:
            self.client = None
    
    async def synthesize(
        self,
        text: str,
        voice: str = "alloy",  # OpenAI: alloy, echo, fable, onyx, nova, shimmer
        language: Optional[str] = None,
        speed: float = 1.0
    ) -> TextToSpeechResult:
        """
        Synthetisiert Text zu Audio
        
        Args:
            text: Text zum Synthetisieren
            voice: Stimme
            language: Sprache (optional)
            speed: Geschwindigkeit (0.25 - 4.0)
        
        Returns:
            TextToSpeechResult
        """
        if self.provider == VoiceProvider.OPENAI_TTS:
            return await self._synthesize_openai(text, voice, speed)
        elif self.provider == VoiceProvider.ELEVENLABS:
            return await self._synthesize_elevenlabs(text, voice)
        else:
            raise ValueError(f"Provider {self.provider} nicht unterstützt")
    
    async def _synthesize_openai(
        self,
        text: str,
        voice: str,
        speed: float
    ) -> TextToSpeechResult:
        """Synthetisiert mit OpenAI TTS"""
        try:
            if not self.client:
                raise ValueError("OpenAI Client nicht verfügbar")
            
            response = self.client.audio.speech.create(
                model="tts-1",  # oder tts-1-hd für höhere Qualität
                voice=voice,
                input=text,
                speed=speed
            )
            
            audio_data = response.content
            
            return TextToSpeechResult(
                audio_data=audio_data,
                format="mp3",
                duration=len(audio_data) / 16000.0  # Geschätzt
            )
        except Exception as e:
            logger.error(f"OpenAI TTS Fehler: {e}")
            raise
    
    async def _synthesize_elevenlabs(
        self,
        text: str,
        voice: str
    ) -> TextToSpeechResult:
        """Synthetisiert mit ElevenLabs"""
        try:
            if not self.client:
                raise ValueError("ElevenLabs Client nicht verfügbar")
            
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY nicht gesetzt")
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = self.client.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            return TextToSpeechResult(
                audio_data=response.content,
                format="mp3"
            )
        except Exception as e:
            logger.error(f"ElevenLabs TTS Fehler: {e}")
            raise


class VoiceCommandProcessor:
    """
    Voice Command Processor
    
    Verarbeitet Voice Commands für Agents.
    """
    
    def __init__(self, voice_to_text: Optional[VoiceToText] = None):
        """
        Initialisiert Voice Command Processor
        
        Args:
            voice_to_text: Voice-to-Text Instanz
        """
        self.voice_to_text = voice_to_text or VoiceToText()
        self.commands: Dict[str, callable] = {}
    
    def register_command(self, command: str, handler: callable):
        """Registriert Voice Command"""
        self.commands[command.lower()] = handler
    
    async def process_voice_command(
        self,
        audio_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Voice Command
        
        Args:
            audio_data: Audio-Daten
            context: Kontext
        
        Returns:
            Command-Ergebnis
        """
        # Transkribiere Audio
        transcription = await self.voice_to_text.transcribe(audio_data)
        text = transcription.text.lower()
        
        # Finde passenden Command
        for command, handler in self.commands.items():
            if command in text:
                try:
                    result = await handler(text, context or {})
                    return {
                        "success": True,
                        "command": command,
                        "result": result,
                        "transcription": transcription.text
                    }
                except Exception as e:
                    logger.error(f"Command Handler Fehler: {e}")
                    return {
                        "success": False,
                        "error": str(e),
                        "transcription": transcription.text
                    }
        
        # Kein Command gefunden
        return {
            "success": False,
            "error": "Kein passender Command gefunden",
            "transcription": transcription.text
        }


# Globale Instanzen
_global_voice_to_text: Optional[VoiceToText] = None
_global_text_to_voice: Optional[TextToVoice] = None
_global_voice_commands: Optional[VoiceCommandProcessor] = None


def get_voice_to_text(provider: VoiceProvider = VoiceProvider.OPENAI_WHISPER) -> VoiceToText:
    """Holt globale Voice-to-Text Instanz"""
    global _global_voice_to_text
    if _global_voice_to_text is None or _global_voice_to_text.provider != provider:
        _global_voice_to_text = VoiceToText(provider=provider)
    return _global_voice_to_text


def get_text_to_voice(provider: VoiceProvider = VoiceProvider.OPENAI_TTS) -> TextToVoice:
    """Holt globale Text-to-Voice Instanz"""
    global _global_text_to_voice
    if _global_text_to_voice is None or _global_text_to_voice.provider != provider:
        _global_text_to_voice = TextToVoice(provider=provider)
    return _global_text_to_voice


def get_voice_command_processor() -> VoiceCommandProcessor:
    """Holt globale Voice Command Processor Instanz"""
    global _global_voice_commands
    if _global_voice_commands is None:
        _global_voice_commands = VoiceCommandProcessor()
    return _global_voice_commands
