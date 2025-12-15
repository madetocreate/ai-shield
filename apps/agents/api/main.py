"""
Main API - FastAPI App mit allen Endpoints

Kombiniert:
- Health Endpoints
- Metrics Endpoints
- Marketplace Endpoints
- Analytics Endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from apps.agents.api.health_endpoints import router as health_router
from apps.agents.api.metrics_endpoint import router as metrics_router
from apps.agents.api.marketplace_endpoints import router as marketplace_router
from apps.agents.api.analytics_endpoints import router as analytics_router
from apps.agents.api.config_endpoints import router as config_router
from apps.agents.api.realtime_endpoints import router as realtime_router
from apps.agents.api.version_endpoints import router as version_router
from apps.agents.api.webhook_endpoints import router as webhook_router
from apps.agents.api.cost_endpoints import router as cost_router
from apps.agents.api.export_endpoints import router as export_router
from apps.agents.api.learning_endpoints import router as learning_router
from apps.agents.api.collaboration_endpoints import router as collaboration_router
from apps.agents.api.notification_endpoints import router as notification_router
from apps.agents.api.reporting_endpoints import router as reporting_router
from apps.agents.api.user_endpoints import router as user_router
from apps.agents.api.backup_endpoints import router as backup_router
from apps.agents.api.performance_endpoints import router as performance_router
from apps.agents.api.i18n_endpoints import router as i18n_router
from apps.agents.api.model_endpoints import router as model_router
from apps.agents.api.calendar_endpoints import router as calendar_router

app = FastAPI(
    title="AI Shield Agents API",
    description="API für Agent-System mit Marketplace, Analytics, Health Checks, Configuration Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Custom OpenAPI Schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI Shield Agents API",
        version="1.0.0",
        description="""
        ## AI Shield Agents API
        
        Vollständige API für das Agent-System mit:
        - **Marketplace**: Agent Discovery, Installation, Rating
        - **Analytics**: Business Intelligence, Forecasting, Anomaly Detection
        - **Configuration**: Feature Flags, A/B Testing, Dynamische Konfiguration
        - **Health**: Health Checks für alle Agents
        - **Metrics**: Prometheus-kompatible Metrics
        
        ## Authentication
        
        Die meisten Endpoints benötigen einen API Key im Header:
        ```
        Authorization: Bearer YOUR_API_KEY
        ```
        
        ## Rate Limiting
        
        Standard: 60 Requests/Minute pro Account
        
        ## Examples
        
        Siehe `/docs` für interaktive API-Dokumentation mit "Try it out" Funktion.
        """,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(marketplace_router)
app.include_router(analytics_router)
app.include_router(config_router)
app.include_router(realtime_router)
app.include_router(version_router)
app.include_router(webhook_router)
app.include_router(cost_router)
app.include_router(export_router)
app.include_router(learning_router)
app.include_router(collaboration_router)
app.include_router(notification_router)
app.include_router(reporting_router)
app.include_router(user_router)
app.include_router(backup_router)
app.include_router(performance_router)
app.include_router(i18n_router)
app.include_router(model_router)
app.include_router(calendar_router)


@app.get("/")
def root():
    """Root Endpoint"""
    return {
        "name": "AI Shield Agents API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "marketplace": "/api/v1/marketplace",
            "analytics": "/api/v1/analytics",
            "configuration": "/api/v1/config",
            "realtime": "/api/v1/realtime",
            "versions": "/api/v1/versions",
            "webhooks": "/api/v1/webhooks",
            "costs": "/api/v1/costs",
            "export": "/api/v1/export",
            "learning": "/api/v1/learning",
            "collaboration": "/api/v1/collaboration",
            "notifications": "/api/v1/notifications",
            "reports": "/api/v1/reports",
            "users": "/api/v1/users",
            "backup": "/api/v1/backup",
            "performance": "/api/v1/performance",
            "i18n": "/api/v1/i18n",
            "models": "/api/v1/models",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
