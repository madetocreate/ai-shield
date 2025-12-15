"""
Internationalization (i18n) API Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from apps.agents.core.i18n import get_i18n_service, Language, Locale

router = APIRouter(prefix="/api/v1/i18n", tags=["i18n"])

class TranslateRequest(BaseModel):
    key: str
    language: str
    default: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class TranslationResponse(BaseModel):
    key: str
    language: str
    value: str

class LocaleConfigResponse(BaseModel):
    locale: str
    language: str
    date_format: str
    time_format: str
    currency: str
    currency_symbol: str

@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslateRequest):
    service = get_i18n_service()
    try:
        language = Language(request.language)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Sprache: {request.language}")
    value = service.translate(request.key, language, request.default, **(request.variables or {}))
    return TranslationResponse(key=request.key, language=request.language, value=value)

@router.get("/languages", response_model=List[str])
async def get_languages():
    service = get_i18n_service()
    return service.get_supported_languages()

@router.get("/locales", response_model=List[str])
async def get_locales():
    service = get_i18n_service()
    return service.get_supported_locales()

@router.get("/locale/{locale}", response_model=LocaleConfigResponse)
async def get_locale_config(locale: str):
    service = get_i18n_service()
    try:
        locale_enum = Locale(locale)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Locale: {locale}")
    config = service.get_locale_config(locale_enum)
    return LocaleConfigResponse(locale=config.locale.value, language=config.language.value, date_format=config.date_format, time_format=config.time_format, currency=config.currency, currency_symbol=config.currency_symbol)

@router.post("/format")
async def format_value(value: Any = Body(...), locale: str = Body(...), format_type: str = Body(...)):
    service = get_i18n_service()
    try:
        locale_enum = Locale(locale)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Locale: {locale}")
    if format_type == "currency":
        if not isinstance(value, (int, float)):
            raise HTTPException(status_code=400, detail="Currency value must be a number")
        formatted = service.format_currency(value, locale_enum)
    elif format_type == "number":
        if not isinstance(value, (int, float)):
            raise HTTPException(status_code=400, detail="Number value must be a number")
        formatted = service.format_number(value, locale_enum)
    elif format_type in ["date", "time", "datetime"]:
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        elif isinstance(value, datetime):
            dt = value
        else:
            raise HTTPException(status_code=400, detail="Value must be a date/datetime")
        formatted = service.format_date(dt, locale_enum, format_type)
    else:
        raise HTTPException(status_code=400, detail=f"Ungültiger Format Type: {format_type}")
    return {"formatted": formatted, "locale": locale, "format_type": format_type}

@router.post("/detect-language")
async def detect_language(text: str = Body(...)):
    service = get_i18n_service()
    language = service.detect_language(text)
    return {"language": language.value, "text": text[:100]}

@router.post("/translations")
async def add_translation(key: str = Body(...), language: str = Body(...), value: str = Body(...)):
    service = get_i18n_service()
    try:
        language_enum = Language(language)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Sprache: {language}")
    service.add_translation(key, language_enum, value)
    return {"success": True, "key": key, "language": language, "value": value}
