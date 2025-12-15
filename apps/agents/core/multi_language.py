"""
Multi-Language Support - Language Detection, Translation, Localization

Features:
- Automatic Language Detection
- Translation (via LLM or Translation API)
- Localization (Agent Responses, Prompts)
- Multi-Language Agent Support
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Unterstützte Sprachen"""
    GERMAN = "de"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    POLISH = "pl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    TURKISH = "tr"
    AUTO = "auto"  # Automatische Erkennung


@dataclass
class LanguageDetectionResult:
    """Language Detection Ergebnis"""
    language: Language
    confidence: float
    detected_text: Optional[str] = None


@dataclass
class TranslationResult:
    """Translation Ergebnis"""
    original_text: str
    translated_text: str
    source_language: Language
    target_language: Language
    confidence: float = 1.0


class LanguageDetector:
    """
    Language Detector
    
    Erkennt Sprache automatisch aus Text.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialisiert Language Detector
        
        Args:
            llm_client: LLM Client für Language Detection (optional)
        """
        self.llm_client = llm_client
        self._setup_llm()
    
    def _setup_llm(self):
        """Setzt LLM Client auf"""
        if self.llm_client is None:
            try:
                import litellm
                self.llm_client = litellm
            except ImportError:
                try:
                    import openai
                    self.llm_client = openai
                except ImportError:
                    logger.warning("Kein LLM Client verfügbar für Language Detection")
                    self.llm_client = None
    
    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Erkennt Sprache aus Text
        
        Args:
            text: Text zur Analyse
        
        Returns:
            LanguageDetectionResult
        """
        if not text or len(text.strip()) < 3:
            return LanguageDetectionResult(
                language=Language.ENGLISH,  # Default
                confidence=0.5
            )
        
        # Nutze LLM für Language Detection (genauer)
        if self.llm_client:
            return self._detect_with_llm(text)
        
        # Fallback: Einfache Heuristik
        return self._detect_with_heuristics(text)
    
    def _detect_with_llm(self, text: str) -> LanguageDetectionResult:
        """Erkennt Sprache mit LLM"""
        try:
            prompt = f"""Erkenne die Sprache des folgenden Textes und antworte nur mit dem ISO 639-1 Sprachcode (z.B. "de", "en", "fr").

Text: {text[:500]}

Sprachcode:"""
            
            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du bist ein Language Detection Expert. Antworte nur mit dem ISO 639-1 Sprachcode."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                detected_code = response.choices[0].message.content.strip().lower()
            else:
                response = self.llm_client.completion(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du bist ein Language Detection Expert. Antworte nur mit dem ISO 639-1 Sprachcode."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                detected_code = response.choices[0].message.content.strip().lower()
            
            # Konvertiere zu Language Enum
            try:
                language = Language(detected_code)
            except ValueError:
                language = Language.ENGLISH  # Fallback
            
            return LanguageDetectionResult(
                language=language,
                confidence=0.9,
                detected_text=text
            )
        except Exception as e:
            logger.warning(f"LLM Language Detection fehlgeschlagen: {e}, nutze Heuristik")
            return self._detect_with_heuristics(text)
    
    def _detect_with_heuristics(self, text: str) -> LanguageDetectionResult:
        """Erkennt Sprache mit Heuristik (Fallback)"""
        text_lower = text.lower()
        
        # Einfache Heuristik basierend auf häufigen Wörtern
        german_indicators = ["der", "die", "das", "und", "ist", "für", "mit", "auf", "zu"]
        english_indicators = ["the", "and", "is", "for", "with", "on", "to", "a", "an"]
        french_indicators = ["le", "la", "les", "et", "est", "pour", "avec", "sur", "de"]
        spanish_indicators = ["el", "la", "los", "y", "es", "para", "con", "en", "de"]
        
        scores = {
            Language.GERMAN: sum(1 for word in german_indicators if word in text_lower),
            Language.ENGLISH: sum(1 for word in english_indicators if word in text_lower),
            Language.FRENCH: sum(1 for word in french_indicators if word in text_lower),
            Language.SPANISH: sum(1 for word in spanish_indicators if word in text_lower),
        }
        
        detected_language = max(scores, key=scores.get)
        confidence = min(0.7, scores[detected_language] / 5.0)  # Max 0.7 für Heuristik
        
        return LanguageDetectionResult(
            language=detected_language,
            confidence=confidence,
            detected_text=text
        )


class Translator:
    """
    Translator
    
    Übersetzt Text zwischen Sprachen.
    """
    
    def __init__(self, llm_client=None, target_language: Language = Language.ENGLISH):
        """
        Initialisiert Translator
        
        Args:
            llm_client: LLM Client für Translation
            target_language: Standard-Zielsprache
        """
        self.llm_client = llm_client
        self.target_language = target_language
        self._setup_llm()
    
    def _setup_llm(self):
        """Setzt LLM Client auf"""
        if self.llm_client is None:
            try:
                import litellm
                self.llm_client = litellm
            except ImportError:
                try:
                    import openai
                    self.llm_client = openai
                except ImportError:
                    logger.warning("Kein LLM Client verfügbar für Translation")
                    self.llm_client = None
    
    def translate(
        self,
        text: str,
        target_language: Optional[Language] = None,
        source_language: Optional[Language] = None
    ) -> TranslationResult:
        """
        Übersetzt Text
        
        Args:
            text: Text zum Übersetzen
            target_language: Zielsprache (default: self.target_language)
            source_language: Quellsprache (optional, wird erkannt falls None)
        
        Returns:
            TranslationResult
        """
        target_language = target_language or self.target_language
        
        # Erkenne Quellsprache falls nicht gegeben
        if source_language is None:
            detector = LanguageDetector(self.llm_client)
            detection = detector.detect(text)
            source_language = detection.language
        
        # Keine Übersetzung nötig wenn Sprachen gleich
        if source_language == target_language:
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence=1.0
            )
        
        # Übersetze mit LLM
        if self.llm_client:
            translated_text = self._translate_with_llm(text, source_language, target_language)
        else:
            translated_text = text  # Fallback: kein Übersetzen
        
        return TranslationResult(
            original_text=text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence=0.9
        )
    
    def _translate_with_llm(
        self,
        text: str,
        source_language: Language,
        target_language: Language
    ) -> str:
        """Übersetzt mit LLM"""
        try:
            language_names = {
                Language.GERMAN: "Deutsch",
                Language.ENGLISH: "English",
                Language.FRENCH: "Français",
                Language.SPANISH: "Español",
                Language.ITALIAN: "Italiano",
                Language.PORTUGUESE: "Português",
                Language.DUTCH: "Nederlands",
                Language.POLISH: "Polski",
                Language.RUSSIAN: "Русский",
                Language.CHINESE: "中文",
                Language.JAPANESE: "日本語",
                Language.KOREAN: "한국어",
                Language.ARABIC: "العربية",
                Language.TURKISH: "Türkçe",
            }
            
            source_name = language_names.get(source_language, source_language.value)
            target_name = language_names.get(target_language, target_language.value)
            
            prompt = f"""Übersetze den folgenden Text von {source_name} nach {target_name}. Übersetze nur den Text, keine Erklärungen.

Text: {text}

Übersetzung:"""
            
            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Du bist ein professioneller Übersetzer. Übersetze präzise von {source_name} nach {target_name}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            else:
                response = self.llm_client.completion(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Du bist ein professioneller Übersetzer. Übersetze präzise von {source_name} nach {target_name}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Translation fehlgeschlagen: {e}")
            return text  # Fallback: Original-Text


class LocalizationManager:
    """
    Localization Manager
    
    Verwaltet lokalisierte Texte für Agents.
    """
    
    def __init__(self):
        """Initialisiert Localization Manager"""
        self.localizations: Dict[str, Dict[Language, str]] = {}
        self._load_default_localizations()
    
    def _load_default_localizations(self):
        """Lädt Standard-Lokalisierungen"""
        # Standard-Lokalisierungen für häufige Agent-Responses
        self.localizations = {
            "greeting": {
                Language.GERMAN: "Hallo! Wie kann ich Ihnen helfen?",
                Language.ENGLISH: "Hello! How can I help you?",
                Language.FRENCH: "Bonjour! Comment puis-je vous aider?",
                Language.SPANISH: "¡Hola! ¿Cómo puedo ayudarte?",
            },
            "goodbye": {
                Language.GERMAN: "Auf Wiedersehen!",
                Language.ENGLISH: "Goodbye!",
                Language.FRENCH: "Au revoir!",
                Language.SPANISH: "¡Adiós!",
            },
            "error": {
                Language.GERMAN: "Entschuldigung, ein Fehler ist aufgetreten.",
                Language.ENGLISH: "Sorry, an error occurred.",
                Language.FRENCH: "Désolé, une erreur s'est produite.",
                Language.SPANISH: "Lo siento, ocurrió un error.",
            },
        }
    
    def get(self, key: str, language: Language, default: Optional[str] = None) -> str:
        """
        Holt lokalisierte Text
        
        Args:
            key: Text-Key
            language: Sprache
            default: Default-Text falls nicht gefunden
        
        Returns:
            Lokalisierter Text
        """
        if key in self.localizations:
            return self.localizations[key].get(language, default or key)
        return default or key
    
    def register(self, key: str, localizations: Dict[Language, str]):
        """Registriert neue Lokalisierung"""
        self.localizations[key] = localizations


# Globale Instanzen
_global_language_detector: Optional[LanguageDetector] = None
_global_translator: Optional[Translator] = None
_global_localization: Optional[LocalizationManager] = None


def get_language_detector() -> LanguageDetector:
    """Holt globale Language Detector-Instanz"""
    global _global_language_detector
    if _global_language_detector is None:
        _global_language_detector = LanguageDetector()
    return _global_language_detector


def get_translator(target_language: Language = Language.ENGLISH) -> Translator:
    """Holt globale Translator-Instanz"""
    global _global_translator
    if _global_translator is None:
        _global_translator = Translator(target_language=target_language)
    elif _global_translator.target_language != target_language:
        _global_translator.target_language = target_language
    return _global_translator


def get_localization_manager() -> LocalizationManager:
    """Holt globale Localization Manager-Instanz"""
    global _global_localization
    if _global_localization is None:
        _global_localization = LocalizationManager()
    return _global_localization
