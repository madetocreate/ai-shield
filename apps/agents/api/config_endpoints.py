"""
Configuration API Endpoints - FastAPI Endpoints für Configuration Management

Endpoints:
- GET /api/v1/config/features - Liste aller Feature Flags
- GET /api/v1/config/features/{name} - Feature Flag Details
- POST /api/v1/config/features - Feature Flag erstellen
- PUT /api/v1/config/features/{name}/enable - Feature aktivieren
- PUT /api/v1/config/features/{name}/disable - Feature deaktivieren
- GET /api/v1/config/ab-tests - Liste aller A/B Tests
- POST /api/v1/config/ab-tests - A/B Test erstellen
- GET /api/v1/config/ab-tests/{name}/variant - Variante für Account holen
- GET /api/v1/config/{namespace} - Konfiguration holen
- POST /api/v1/config/{namespace} - Konfiguration setzen
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.configuration_management import (
    get_config_manager,
    FeatureFlagStatus,
    ABTestVariant
)

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])


# Request Models
class CreateFeatureFlagRequest(BaseModel):
    name: str
    status: str = "disabled"  # enabled, disabled, percentage
    percentage: float = 100.0


class CreateABTestRequest(BaseModel):
    name: str
    variants: List[Dict[str, Any]]  # [{"name": "A", "weight": 50.0, "config": {}}, ...]
    metrics: List[str] = []


class SetConfigRequest(BaseModel):
    key: str
    value: Any


# Response Models
class FeatureFlagResponse(BaseModel):
    name: str
    status: str
    percentage: float
    enabled_accounts: List[str]
    disabled_accounts: List[str]
    created_at: str
    updated_at: str


class ABTestResponse(BaseModel):
    name: str
    variants: List[Dict[str, Any]]
    active: bool
    start_date: str
    end_date: Optional[str]
    metrics: List[str]
    winner: Optional[str]


@router.get("/features", response_model=List[FeatureFlagResponse])
def list_feature_flags():
    """Listet alle Feature Flags"""
    manager = get_config_manager()
    return [
        FeatureFlagResponse(
            name=flag.name,
            status=flag.status.value,
            percentage=flag.percentage,
            enabled_accounts=flag.enabled_accounts,
            disabled_accounts=flag.disabled_accounts,
            created_at=flag.created_at.isoformat(),
            updated_at=flag.updated_at.isoformat()
        )
        for flag in manager.feature_flags.values()
    ]


@router.get("/features/{name}", response_model=FeatureFlagResponse)
def get_feature_flag(name: str):
    """Holt Feature Flag Details"""
    manager = get_config_manager()
    if name not in manager.feature_flags:
        raise HTTPException(status_code=404, detail="Feature Flag nicht gefunden")
    
    flag = manager.feature_flags[name]
    return FeatureFlagResponse(
        name=flag.name,
        status=flag.status.value,
        percentage=flag.percentage,
        enabled_accounts=flag.enabled_accounts,
        disabled_accounts=flag.disabled_accounts,
        created_at=flag.created_at.isoformat(),
        updated_at=flag.updated_at.isoformat()
    )


@router.get("/features/{name}/check")
def check_feature_flag(name: str, account_id: Optional[str] = Query(None)):
    """Prüft ob Feature aktiviert ist"""
    manager = get_config_manager()
    enabled = manager.is_feature_enabled(name, account_id)
    return {"feature": name, "enabled": enabled, "account_id": account_id}


@router.post("/features", response_model=FeatureFlagResponse)
def create_feature_flag(request: CreateFeatureFlagRequest):
    """Erstellt Feature Flag"""
    manager = get_config_manager()
    
    try:
        status = FeatureFlagStatus(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status: {request.status}")
    
    flag = manager.create_feature_flag(
        name=request.name,
        status=status,
        percentage=request.percentage
    )
    
    return FeatureFlagResponse(
        name=flag.name,
        status=flag.status.value,
        percentage=flag.percentage,
        enabled_accounts=flag.enabled_accounts,
        disabled_accounts=flag.disabled_accounts,
        created_at=flag.created_at.isoformat(),
        updated_at=flag.updated_at.isoformat()
    )


@router.put("/features/{name}/enable")
def enable_feature(name: str, percentage: float = Body(100.0, embed=True)):
    """Aktiviert Feature"""
    manager = get_config_manager()
    manager.enable_feature(name, percentage)
    return {"success": True, "message": f"Feature {name} aktiviert"}


@router.put("/features/{name}/disable")
def disable_feature(name: str):
    """Deaktiviert Feature"""
    manager = get_config_manager()
    manager.disable_feature(name)
    return {"success": True, "message": f"Feature {name} deaktiviert"}


@router.get("/ab-tests", response_model=List[ABTestResponse])
def list_ab_tests():
    """Listet alle A/B Tests"""
    manager = get_config_manager()
    return [
        ABTestResponse(
            name=test.name,
            variants=[
                {
                    "name": v.name,
                    "weight": v.weight,
                    "config": v.config
                }
                for v in test.variants
            ],
            active=test.active,
            start_date=test.start_date.isoformat(),
            end_date=test.end_date.isoformat() if test.end_date else None,
            metrics=test.metrics,
            winner=test.winner
        )
        for test in manager.ab_tests.values()
    ]


@router.post("/ab-tests", response_model=ABTestResponse)
def create_ab_test(request: CreateABTestRequest):
    """Erstellt A/B Test"""
    manager = get_config_manager()
    
    variants = [
        ABTestVariant(
            name=v["name"],
            weight=v.get("weight", 50.0),
            config=v.get("config", {})
        )
        for v in request.variants
    ]
    
    test = manager.create_ab_test(
        name=request.name,
        variants=variants,
        metrics=request.metrics
    )
    
    return ABTestResponse(
        name=test.name,
        variants=[
            {
                "name": v.name,
                "weight": v.weight,
                "config": v.config
            }
            for v in test.variants
        ],
        active=test.active,
        start_date=test.start_date.isoformat(),
        end_date=test.end_date.isoformat() if test.end_date else None,
        metrics=test.metrics,
        winner=test.winner
    )


@router.get("/ab-tests/{name}/variant")
def get_ab_test_variant(name: str, account_id: Optional[str] = Query(None)):
    """Holt Variante für A/B Test"""
    manager = get_config_manager()
    variant = manager.get_ab_test_variant(name, account_id)
    
    if not variant:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden oder inaktiv")
    
    return {
        "test_name": name,
        "variant": variant.name,
        "weight": variant.weight,
        "config": variant.config,
        "account_id": account_id
    }


@router.get("/{namespace}")
def get_configs(namespace: str = "default"):
    """Holt alle Konfigurationen eines Namespaces"""
    manager = get_config_manager()
    return manager.get_all_configs(namespace)


@router.post("/{namespace}")
def set_config(namespace: str, request: SetConfigRequest):
    """Setzt Konfiguration"""
    manager = get_config_manager()
    manager.set_config(request.key, request.value, namespace)
    return {"success": True, "message": f"Config {request.key} gesetzt"}
