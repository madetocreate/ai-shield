"""
Collaboration API Endpoints - FastAPI Endpoints für Multi-Agent Collaboration

Endpoints:
- POST /api/v1/collaboration/message - Message zwischen Agents senden
- POST /api/v1/collaboration/workflows - Workflow erstellen
- POST /api/v1/collaboration/workflows/{workflow_id}/execute - Workflow ausführen
- GET /api/v1/collaboration/workflows/{workflow_id} - Workflow Status
- GET /api/v1/collaboration/memory - Shared Memory holen
- POST /api/v1/collaboration/memory - Shared Memory setzen
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from apps.agents.core.multi_agent_collaboration import (
    get_communication_bus,
    get_workflow_orchestrator,
    get_shared_memory,
    MessageType
)

router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration"])


# Request Models
class SendMessageRequest(BaseModel):
    from_agent: str
    to_agent: str
    message_type: str  # request, response, notification, query, result
    payload: Dict[str, Any]
    requires_response: bool = False


class CreateWorkflowRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]  # [{"agent_name": "...", "action": "...", "input_data": {...}, "dependencies": [...]}]


class SetMemoryRequest(BaseModel):
    key: str
    value: Any
    workflow_id: Optional[str] = None


# Response Models
class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    status: str
    steps: List[Dict[str, Any]]
    shared_memory: Dict[str, Any]
    created_at: str
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]


@router.post("/message")
async def send_message(request: SendMessageRequest):
    """Sendet Message zwischen Agents"""
    bus = get_communication_bus()
    
    try:
        message_type = MessageType(request.message_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Message Type: {request.message_type}")
    
    response = await bus.send_message(
        from_agent=request.from_agent,
        to_agent=request.to_agent,
        message_type=message_type,
        payload=request.payload,
        requires_response=request.requires_response
    )
    
    return {
        "success": True,
        "message_sent": True,
        "response": response.payload if response else None
    }


@router.post("/workflows", response_model=WorkflowResponse)
def create_workflow(request: CreateWorkflowRequest):
    """Erstellt Workflow"""
    orchestrator = get_workflow_orchestrator()
    workflow = orchestrator.create_workflow(
        name=request.name,
        steps=request.steps
    )
    
    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        status=workflow.status.value,
        steps=[
            {
                "step_id": s.step_id,
                "agent_name": s.agent_name,
                "action": s.action,
                "input_data": s.input_data,
                "output_data": s.output_data,
                "status": s.status,
                "error": s.error,
                "dependencies": s.dependencies
            }
            for s in workflow.steps
        ],
        shared_memory=workflow.shared_memory,
        created_at=workflow.created_at.isoformat(),
        completed_at=workflow.completed_at.isoformat() if workflow.completed_at else None,
        result=workflow.result
    )


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Führt Workflow aus"""
    orchestrator = get_workflow_orchestrator()
    
    try:
        result = await orchestrator.execute_workflow(workflow_id)
        return {
            "success": True,
            "workflow_id": workflow_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str):
    """Holt Workflow Status"""
    orchestrator = get_workflow_orchestrator()
    
    if workflow_id not in orchestrator.workflows:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    
    workflow = orchestrator.workflows[workflow_id]
    
    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        status=workflow.status.value,
        steps=[
            {
                "step_id": s.step_id,
                "agent_name": s.agent_name,
                "action": s.action,
                "input_data": s.input_data,
                "output_data": s.output_data,
                "status": s.status,
                "error": s.error,
                "dependencies": s.dependencies
            }
            for s in workflow.steps
        ],
        shared_memory=workflow.shared_memory,
        created_at=workflow.created_at.isoformat(),
        completed_at=workflow.completed_at.isoformat() if workflow.completed_at else None,
        result=workflow.result
    )


@router.get("/memory")
async def get_memory(
    key: str,
    workflow_id: Optional[str] = None,
    default: Any = None
):
    """Holt Wert aus Shared Memory"""
    memory = get_shared_memory()
    value = await memory.get(key, workflow_id=workflow_id, default=default)
    return {"key": key, "value": value, "workflow_id": workflow_id}


@router.post("/memory")
async def set_memory(request: SetMemoryRequest):
    """Setzt Wert in Shared Memory"""
    memory = get_shared_memory()
    await memory.set(request.key, request.value, workflow_id=request.workflow_id)
    return {"success": True, "message": f"Memory {request.key} gesetzt"}
