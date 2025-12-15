"""
AI Enhancements API Endpoints
"""
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from apps.agents.core.model_management import get_model_management, ModelType, ModelStatus, ABTestStatus

router = APIRouter(prefix="/api/v1/models", tags=["models"])

class CreateModelRequest(BaseModel):
    name: str
    model_type: str
    base_model: Optional[str] = None
    description: Optional[str] = None

class ModelResponse(BaseModel):
    id: str
    name: str
    model_type: str
    base_model: Optional[str]
    version: str
    status: str
    description: Optional[str]
    performance_metrics: Dict[str, float]
    created_at: str
    updated_at: str

class FineTuningRequest(BaseModel):
    model_id: str
    training_data: List[Dict[str, Any]]
    hyperparameters: Optional[Dict[str, Any]] = None

class FineTuningJobResponse(BaseModel):
    id: str
    model_id: str
    status: str
    progress: float
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result_model_id: Optional[str] = None

class CreateABTestRequest(BaseModel):
    name: str
    model_a_id: str
    model_b_id: str
    traffic_split: float = 0.5
    description: Optional[str] = None

class ABTestResponse(BaseModel):
    id: str
    name: str
    model_a_id: str
    model_b_id: str
    status: str
    traffic_split: float
    metrics: Dict[str, float]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    winner_model_id: Optional[str] = None

class ModelPerformanceRequest(BaseModel):
    model_id: str
    accuracy: Optional[float] = None
    latency_ms: Optional[float] = None
    cost_per_request: Optional[float] = None
    success: bool = True

@router.post("", response_model=ModelResponse)
async def create_model(request: CreateModelRequest):
    service = get_model_management()
    try:
        model_type = ModelType(request.model_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültiger Model Type: {request.model_type}")
    model = service.create_model(request.name, model_type, request.base_model, request.description)
    return ModelResponse(id=model.id, name=model.name, model_type=model.model_type.value, base_model=model.base_model, version=model.version, status=model.status.value, description=model.description, performance_metrics=model.performance_metrics, created_at=model.created_at.isoformat(), updated_at=model.updated_at.isoformat())

@router.get("", response_model=List[ModelResponse])
async def get_models(model_type: Optional[str] = Query(None), status: Optional[str] = Query(None)):
    service = get_model_management()
    model_type_enum = None
    if model_type:
        try:
            model_type_enum = ModelType(model_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Model Type: {model_type}")
    status_enum = None
    if status:
        try:
            status_enum = ModelStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Status: {status}")
    models = service.get_models(model_type=model_type_enum, status=status_enum)
    return [ModelResponse(id=m.id, name=m.name, model_type=m.model_type.value, base_model=m.base_model, version=m.version, status=m.status.value, description=m.description, performance_metrics=m.performance_metrics, created_at=m.created_at.isoformat(), updated_at=m.updated_at.isoformat()) for m in models]

@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    service = get_model_management()
    model = service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model nicht gefunden")
    return ModelResponse(id=model.id, name=model.name, model_type=model.model_type.value, base_model=model.base_model, version=model.version, status=model.status.value, description=model.description, performance_metrics=model.performance_metrics, created_at=model.created_at.isoformat(), updated_at=model.updated_at.isoformat())

@router.post("/fine-tune", response_model=FineTuningJobResponse)
async def create_fine_tuning_job(request: FineTuningRequest):
    service = get_model_management()
    job = service.create_fine_tuning_job(request.model_id, request.training_data, request.hyperparameters)
    return FineTuningJobResponse(id=job.id, model_id=job.model_id, status=job.status, progress=job.progress, created_at=job.created_at.isoformat(), started_at=job.started_at.isoformat() if job.started_at else None, completed_at=job.completed_at.isoformat() if job.completed_at else None, error=job.error, result_model_id=job.result_model_id)

@router.get("/fine-tune/{job_id}", response_model=FineTuningJobResponse)
async def get_fine_tuning_job(job_id: str):
    service = get_model_management()
    job = service.get_fine_tuning_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Fine-Tuning Job nicht gefunden")
    return FineTuningJobResponse(id=job.id, model_id=job.model_id, status=job.status, progress=job.progress, created_at=job.created_at.isoformat(), started_at=job.started_at.isoformat() if job.started_at else None, completed_at=job.completed_at.isoformat() if job.completed_at else None, error=job.error, result_model_id=job.result_model_id)

@router.post("/ab-test", response_model=ABTestResponse)
async def create_ab_test(request: CreateABTestRequest):
    service = get_model_management()
    try:
        ab_test = service.create_ab_test(request.name, request.model_a_id, request.model_b_id, request.traffic_split)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ABTestResponse(id=ab_test.id, name=ab_test.name, model_a_id=ab_test.model_a_id, model_b_id=ab_test.model_b_id, status=ab_test.status.value, traffic_split=ab_test.traffic_split, metrics=ab_test.metrics, start_date=ab_test.start_date.isoformat() if ab_test.start_date else None, end_date=ab_test.end_date.isoformat() if ab_test.end_date else None, winner_model_id=ab_test.winner_model_id)

@router.post("/ab-test/{ab_test_id}/start")
async def start_ab_test(ab_test_id: str):
    service = get_model_management()
    success = service.start_ab_test(ab_test_id)
    if not success:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden")
    return {"success": True}

@router.post("/ab-test/{ab_test_id}/stop")
async def stop_ab_test(ab_test_id: str, winner_model_id: Optional[str] = Body(None)):
    service = get_model_management()
    success = service.stop_ab_test(ab_test_id, winner_model_id=winner_model_id)
    if not success:
        raise HTTPException(status_code=404, detail="A/B Test nicht gefunden")
    return {"success": True}

@router.get("/ab-test", response_model=List[ABTestResponse])
async def get_ab_tests(status: Optional[str] = Query(None)):
    service = get_model_management()
    status_enum = None
    if status:
        try:
            status_enum = ABTestStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Ungültiger Status: {status}")
    tests = service.get_ab_tests(status=status_enum)
    return [ABTestResponse(id=t.id, name=t.name, model_a_id=t.model_a_id, model_b_id=t.model_b_id, status=t.status.value, traffic_split=t.traffic_split, metrics=t.metrics, start_date=t.start_date.isoformat() if t.start_date else None, end_date=t.end_date.isoformat() if t.end_date else None, winner_model_id=t.winner_model_id) for t in tests]

@router.post("/performance")
async def record_performance(request: ModelPerformanceRequest):
    service = get_model_management()
    service.record_model_performance(request.model_id, request.accuracy, request.latency_ms, request.cost_per_request, request.success)
    return {"success": True}

@router.get("/compare")
async def compare_models(model_a_id: str = Query(...), model_b_id: str = Query(...)):
    service = get_model_management()
    try:
        return service.compare_models(model_a_id, model_b_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
