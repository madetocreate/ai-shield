"""
Export/Import API Endpoints - FastAPI Endpoints für Data Export/Import

Endpoints:
- GET /api/v1/export/agents - Export Agents
- GET /api/v1/export/configuration - Export Configuration
- GET /api/v1/export/all - Export All
- POST /api/v1/import - Import Data
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
from apps.agents.core.data_export_import import (
    get_exporter,
    get_importer,
    ExportFormat
)

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/agents")
def export_agents(
    format: str = Query("json", description="json, csv"),
    include_code: bool = Query(False)
):
    """Exportiert Agents"""
    exporter = get_exporter()
    
    try:
        export_format = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {format}")
    
    data = exporter.export_agents(format=export_format, include_code=include_code)
    
    if format == "csv":
        return Response(
            content=data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=agents.csv"}
        )
    else:
        return Response(
            content=data,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=agents.json"}
        )


@router.get("/configuration")
def export_configuration(format: str = Query("json")):
    """Exportiert Konfiguration"""
    exporter = get_exporter()
    
    try:
        export_format = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {format}")
    
    data = exporter.export_configuration(format=export_format)
    
    return Response(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=configuration.json"}
    )


@router.get("/all")
def export_all(format: str = Query("json")):
    """Exportiert alle Daten"""
    exporter = get_exporter()
    
    try:
        export_format = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {format}")
    
    data = exporter.export_all(format=export_format)
    
    return Response(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=full_export.json"}
    )


@router.post("/import")
def import_data(data: str, format: str = Query("json")):
    """Importiert Daten"""
    importer = get_importer()
    
    try:
        import_format = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {format}")
    
    result = importer.import_data(data, format=import_format)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Import fehlgeschlagen"))
    
    return result
