"""
Reporting Service - Custom Reports, Scheduled Reports, Export Formats
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class ReportFormat(Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class ReportTemplate:
    id: str
    name: str
    description: Optional[str] = None
    query: str = ""
    format: ReportFormat = ReportFormat.PDF
    fields: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Report:
    id: str
    name: str
    account_id: str
    template_id: Optional[str] = None
    format: ReportFormat = ReportFormat.PDF
    status: ReportStatus = ReportStatus.DRAFT
    query: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    data: Optional[List[Dict[str, Any]]] = None
    file_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    generated_at: Optional[datetime] = None
    error: Optional[str] = None

@dataclass
class ScheduledReport:
    id: str
    report_id: str
    frequency: ReportFrequency
    next_run: datetime
    recipients: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class ReportingService:
    def __init__(self):
        self.reports: Dict[str, Report] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.scheduled_reports: Dict[str, ScheduledReport] = {}
        self._setup_default_templates()
    
    def _setup_default_templates(self):
        self.templates["agent_performance"] = ReportTemplate(id="agent_performance", name="Agent Performance Report", description="Performance metrics for all agents", format=ReportFormat.PDF, fields=["agent_name", "requests", "avg_latency", "success_rate", "cost"])
        self.templates["cost_breakdown"] = ReportTemplate(id="cost_breakdown", name="Cost Breakdown Report", description="Cost breakdown by agent and account", format=ReportFormat.EXCEL, fields=["account_id", "agent_name", "total_cost", "requests", "avg_cost_per_request"])
        self.templates["usage_summary"] = ReportTemplate(id="usage_summary", name="Usage Summary Report", description="Usage statistics summary", format=ReportFormat.CSV, fields=["date", "total_requests", "unique_users", "active_agents"])
    
    def create_template(self, name: str, description: Optional[str] = None, query: str = "", format: ReportFormat = ReportFormat.PDF, fields: Optional[List[str]] = None) -> ReportTemplate:
        template = ReportTemplate(id=f"template_{datetime.now().timestamp()}", name=name, description=description, query=query, format=format, fields=fields or [])
        self.templates[template.id] = template
        return template
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        return self.templates.get(template_id)
    
    def get_templates(self) -> List[ReportTemplate]:
        return list(self.templates.values())
    
    def create_report(self, name: str, account_id: str, template_id: Optional[str] = None, format: ReportFormat = ReportFormat.PDF, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Report:
        report = Report(id=f"report_{datetime.now().timestamp()}", name=name, account_id=account_id, template_id=template_id, format=format, query=query, filters=filters or {}, status=ReportStatus.DRAFT)
        self.reports[report.id] = report
        return report
    
    def generate_report(self, report_id: str, data: Optional[List[Dict[str, Any]]] = None) -> Report:
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} nicht gefunden")
        report.status = ReportStatus.GENERATING
        try:
            if data:
                report.data = data
            else:
                report.data = [{"field1": "value1", "field2": "value2"}, {"field1": "value3", "field2": "value4"}]
            report.file_path = f"/reports/{report.id}.{report.format.value}"
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.now()
        except Exception as e:
            logger.error(f"Report Generation failed: {e}")
            report.status = ReportStatus.FAILED
            report.error = str(e)
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        return self.reports.get(report_id)
    
    def get_reports(self, account_id: Optional[str] = None, status: Optional[ReportStatus] = None) -> List[Report]:
        reports = list(self.reports.values())
        if account_id:
            reports = [r for r in reports if r.account_id == account_id]
        if status:
            reports = [r for r in reports if r.status == status]
        return reports
    
    def schedule_report(self, report_id: str, frequency: ReportFrequency, next_run: datetime, recipients: Optional[List[str]] = None) -> ScheduledReport:
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} nicht gefunden")
        scheduled = ScheduledReport(id=f"scheduled_{datetime.now().timestamp()}", report_id=report_id, frequency=frequency, next_run=next_run, recipients=recipients or [], is_active=True)
        self.scheduled_reports[scheduled.id] = scheduled
        return scheduled
    
    def get_scheduled_reports(self, report_id: Optional[str] = None, is_active: Optional[bool] = None) -> List[ScheduledReport]:
        scheduled = list(self.scheduled_reports.values())
        if report_id:
            scheduled = [s for s in scheduled if s.report_id == report_id]
        if is_active is not None:
            scheduled = [s for s in scheduled if s.is_active == is_active]
        return scheduled
    
    def export_report(self, report_id: str) -> Dict[str, Any]:
        report = self.reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} nicht gefunden")
        if report.status != ReportStatus.COMPLETED:
            raise ValueError(f"Report {report_id} ist noch nicht generiert")
        return {"id": report.id, "name": report.name, "format": report.format.value, "data": report.data, "generated_at": report.generated_at.isoformat() if report.generated_at else None, "file_path": report.file_path}

_global_reporting_service: Optional[ReportingService] = None

def get_reporting_service() -> ReportingService:
    global _global_reporting_service
    if _global_reporting_service is None:
        _global_reporting_service = ReportingService()
    return _global_reporting_service
