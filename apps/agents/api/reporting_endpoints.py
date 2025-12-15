"""
Reporting Service API Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from apps.agents.core.reporting import get_reporting_service, ReportFormat, ReportStatus, ReportFrequency

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

class CreateTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    query: str = ""
    format: str = "pdf"
    fields: Optional[List[str]] = None

class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    format: str
    fields: List[str]
    created_at: str

class CreateReportRequest(BaseModel):
    name: str
    account_id: str
    template_id: Optional[str] = None
    format: str = "pdf"
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    id: str
    name: str
    account_id: str
    template_id: Optional[str]
    format: str
    status: str
    created_at: str
    generated_at: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None

class ScheduleReportRequest(BaseModel):
    report_id: str
    frequency: str
    next_run: str
    recipients: Optional[List[str]] = None

class ScheduledReportResponse(BaseModel):
    id: str
    report_id: str
    frequency: str
    next_run: str
    recipients: List[str]
    is_active: bool
    created_at: str

@router.post("/templates", response_model=TemplateResponse)
async def create_template(request: CreateTemplateRequest):
    service = get_reporting_service()
    try:
        format_enum = ReportFormat(request.format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {request.format}")
    template = service.create_template(name=request.name, description=request.description, query=request.query, format=format_enum, fields=request.fields)
    return TemplateResponse(id=template.id, name=template.name, description=template.description, format=template.format.value, fields=template.fields, created_at=template.created_at.isoformat())

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates():
    service = get_reporting_service()
    templates = service.get_templates()
    return [TemplateResponse(id=t.id, name=t.name, description=t.description, format=t.format.value, fields=t.fields, created_at=t.created_at.isoformat()) for t in templates]

@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    service = get_reporting_service()
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    return TemplateResponse(id=template.id, name=template.name, description=template.description, format=template.format.value, fields=template.fields, created_at=template.created_at.isoformat())

@router.post("", response_model=ReportResponse)
async def create_report(request: CreateReportRequest):
    service = get_reporting_service()
    try:
        format_enum = ReportFormat(request.format)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiges Format: {request.format}")
    report = service.create_report(name=request.name, account_id=request.account_id, template_id=request.template_id, format=format_enum, query=request.query, filters=request.filters)
    return ReportResponse(id=report.id, name=report.name, account_id=report.account_id, template_id=report.template_id, format=report.format.value, status=report.status.value, created_at=report.created_at.isoformat(), generated_at=report.generated_at.isoformat() if report.generated_at else None, file_path=report.file_path, error=report.error)

@router.post("/{report_id}/generate", response_model=ReportResponse)
async def generate_report(report_id: str, data: Optional[List[Dict[str, Any]]] = Body(None)):
    service = get_reporting_service()
    try:
        report = service.generate_report(report_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ReportResponse(id=report.id, name=report.name, account_id=report.account_id, template_id=report.template_id, format=report.format.value, status=report.status.value, created_at=report.created_at.isoformat(), generated_at=report.generated_at.isoformat() if report.generated_at else None, file_path=report.file_path, error=report.error)

@router.get("", response_model=List[ReportResponse])
async def get_reports(account_id: Optional[str] = Query(None), status: Optional[str] = Query(None)):
    service = get_reporting_service()
    status_enum = None
    if status:
        try:
            status_enum = ReportStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Status: {status}")
    reports = service.get_reports(account_id=account_id, status=status_enum)
    return [ReportResponse(id=r.id, name=r.name, account_id=r.account_id, template_id=r.template_id, format=r.format.value, status=r.status.value, created_at=r.created_at.isoformat(), generated_at=r.generated_at.isoformat() if r.generated_at else None, file_path=r.file_path, error=r.error) for r in reports]

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    service = get_reporting_service()
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report nicht gefunden")
    return ReportResponse(id=report.id, name=report.name, account_id=report.account_id, template_id=report.template_id, format=report.format.value, status=report.status.value, created_at=report.created_at.isoformat(), generated_at=report.generated_at.isoformat() if report.generated_at else None, file_path=report.file_path, error=report.error)

@router.get("/{report_id}/export")
async def export_report(report_id: str):
    service = get_reporting_service()
    try:
        return service.export_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/schedule", response_model=ScheduledReportResponse)
async def schedule_report(request: ScheduleReportRequest):
    service = get_reporting_service()
    try:
        frequency = ReportFrequency(request.frequency)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Frequency: {request.frequency}")
    try:
        next_run = datetime.fromisoformat(request.next_run)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datum Format")
    try:
        scheduled = service.schedule_report(report_id=request.report_id, frequency=frequency, next_run=next_run, recipients=request.recipients)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ScheduledReportResponse(id=scheduled.id, report_id=scheduled.report_id, frequency=scheduled.frequency.value, next_run=scheduled.next_run.isoformat(), recipients=scheduled.recipients, is_active=scheduled.is_active, created_at=scheduled.created_at.isoformat())

@router.get("/schedule", response_model=List[ScheduledReportResponse])
async def get_scheduled_reports(report_id: Optional[str] = Query(None), is_active: Optional[bool] = Query(None)):
    service = get_reporting_service()
    scheduled = service.get_scheduled_reports(report_id=report_id, is_active=is_active)
    return [ScheduledReportResponse(id=s.id, report_id=s.report_id, frequency=s.frequency.value, next_run=s.next_run.isoformat(), recipients=s.recipients, is_active=s.is_active, created_at=s.created_at.isoformat()) for s in scheduled]
