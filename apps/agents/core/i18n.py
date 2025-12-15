"""
Internationalization (i18n) - Multi-Language UI, Locale Management
"""
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class Language(Enum):
    DE = "de"
    EN = "en"
    FR = "fr"
    ES = "es"
    IT = "it"
    PT = "pt"
    NL = "nl"
    PL = "pl"
    RU = "ru"
    ZH = "zh"
    JA = "ja"
    KO = "ko"

class Locale(Enum):
    DE_DE = "de_DE"
    EN_US = "en_US"
    EN_GB = "en_GB"
    FR_FR = "fr_FR"
    ES_ES = "es_ES"

@dataclass
class LocaleConfig:
    locale: Locale
    language: Language
    date_format: str = "%d.%m.%Y"
    time_format: str = "%H:%M:%S"
    currency: str = "EUR"
    currency_symbol: str = "€"
    number_separator: str = ","
    thousand_separator: str = "."

class I18nService:
    def __init__(self):
        self.translations: Dict[str, Dict[Language, str]] = {}
        self.locale_configs: Dict[Locale, LocaleConfig] = {}
        self._setup_default_translations()
        self._setup_default_locales()
    
    def _setup_default_translations(self):
        self.translations = {
            "welcome": {Language.DE: "Willkommen", Language.EN: "Welcome", Language.FR: "Bienvenue"},
            "error": {Language.DE: "Fehler", Language.EN: "Error", Language.FR: "Erreur"},
            "success": {Language.DE: "Erfolg", Language.EN: "Success", Language.FR: "Succès"},
            "loading": {Language.DE: "Lädt...", Language.EN: "Loading...", Language.FR: "Chargement..."},
            "save": {Language.DE: "Speichern", Language.EN: "Save", Language.FR: "Enregistrer"},
            "cancel": {Language.DE: "Abbrechen", Language.EN: "Cancel", Language.FR: "Annuler"}
        }
    
    def _setup_default_locales(self):
        self.locale_configs[Locale.DE_DE] = LocaleConfig(Locale.DE_DE, Language.DE, "%d.%m.%Y", "%H:%M:%S", "EUR", "€", ",", ".")
        self.locale_configs[Locale.EN_US] = LocaleConfig(Locale.EN_US, Language.EN, "%m/%d/%Y", "%I:%M:%S %p", "USD", "$", ".", ",")
        self.locale_configs[Locale.EN_GB] = LocaleConfig(Locale.EN_GB, Language.EN, "%d/%m/%Y", "%H:%M:%S", "GBP", "£", ".", ",")
    
    def translate(self, key: str, language: Language, default: Optional[str] = None, **kwargs) -> str:
        if key in self.translations:
            translations = self.translations[key]
            if language in translations:
                text = translations[language]
                if kwargs:
                    try:
                        text = text.format(**kwargs)
                    except KeyError:
                        pass
                return text
        return default or key
    
    def add_translation(self, key: str, language: Language, value: str):
        if key not in self.translations:
            self.translations[key] = {}
        self.translations[key][language] = value
    
    def get_locale_config(self, locale: Locale) -> LocaleConfig:
        return self.locale_configs.get(locale, self.locale_configs[Locale.EN_US])
    
    def format_date(self, date: datetime, locale: Locale, format_type: str = "date") -> str:
        config = self.get_locale_config(locale)
        if format_type == "date":
            return date.strftime(config.date_format)
        elif format_type == "time":
            return date.strftime(config.time_format)
        return date.strftime(f"{config.date_format} {config.time_format}")
    
    def format_currency(self, amount: float, locale: Locale) -> str:
        config = self.get_locale_config(locale)
        formatted = f"{amount:,.2f}"
        if config.currency_symbol == "€":
            parts = formatted.split(".")
            if len(parts) == 2:
                integer_part = parts[0].replace(",", config.thousand_separator)
                return f"{integer_part}{config.number_separator}{parts[1]} {config.currency_symbol}"
        return f"{config.currency_symbol}{formatted}"
    
    def format_number(self, number: float, locale: Locale, decimals: int = 2) -> str:
        config = self.get_locale_config(locale)
        formatted = f"{number:,.{decimals}f}"
        if config.number_separator == ",":
            parts = formatted.split(".")
            if len(parts) == 2:
                integer_part = parts[0].replace(",", config.thousand_separator)
                return f"{integer_part}{config.number_separator}{parts[1]}"
        return formatted
    
    def detect_language(self, text: str) -> Language:
        text_lower = text.lower()
        if any(word in text_lower for word in ["der", "die", "das", "und"]):
            return Language.DE
        if any(word in text_lower for word in ["le", "la", "les", "et"]):
            return Language.FR
        if any(word in text_lower for word in ["el", "la", "los", "y"]):
            return Language.ES
        return Language.EN
    
    def get_supported_languages(self) -> List[str]:
        return [lang.value for lang in Language]
    
    def get_supported_locales(self) -> List[str]:
        return [loc.value for loc in Locale]

_global_i18n_service: Optional[I18nService] = None

def get_i18n_service() -> I18nService:
    global _global_i18n_service
    if _global_i18n_service is None:
        _global_i18n_service = I18nService()
    return _global_i18n_service
