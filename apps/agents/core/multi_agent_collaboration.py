"""
Multi-Agent Collaboration - Agent Communication, Workflows, Shared Memory

Features:
- Agent-to-Agent Communication
- Multi-Agent Workflows
- Shared Memory
- Collaborative Problem Solving
- Workflow Orchestration
"""

from typing import Dict, Optional, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Message Type"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    RESULT = "result"


class WorkflowStatus(str, Enum):
    """Workflow Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentMessage:
    """Agent-to-Agent Message"""
    id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # Für Request-Response Matching
    requires_response: bool = False


@dataclass
class WorkflowStep:
    """Workflow Step"""
    step_id: str
    agent_name: str
    action: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # Step IDs die vorher laufen müssen


@dataclass
class MultiAgentWorkflow:
    """Multi-Agent Workflow"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


class AgentCommunicationBus:
    """
    Agent Communication Bus
    
    Ermöglicht Agent-to-Agent Communication.
    """
    
    def __init__(self):
        """Initialisiert Communication Bus"""
        self.message_handlers: Dict[str, List[Callable]] = {}  # agent_name -> [handlers]
        self.message_queue: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []
    
    def register_handler(self, agent_name: str, handler: Callable):
        """
        Registriert Message Handler für Agent
        
        Args:
            agent_name: Agent Name
            handler: Handler Function (async)
        """
        if agent_name not in self.message_handlers:
            self.message_handlers[agent_name] = []
        self.message_handlers[agent_name].append(handler)
        logger.info(f"Message Handler für {agent_name} registriert")
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        requires_response: bool = False
    ) -> Optional[AgentMessage]:
        """
        Sendet Message zwischen Agents
        
        Args:
            from_agent: Sender Agent
            to_agent: Empfänger Agent
            message_type: Message Type
            payload: Message Payload
            requires_response: Ob Response erwartet wird
        
        Returns:
            Response Message (falls requires_response=True)
        """
        correlation_id = str(uuid.uuid4()) if requires_response else None
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id,
            requires_response=requires_response
        )
        
        self.message_queue.append(message)
        self.message_history.append(message)
        
        # Behalte nur letzte 1000 Messages
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
        
        # Sende an Handler
        if to_agent in self.message_handlers:
            for handler in self.message_handlers[to_agent]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(message)
                    else:
                        result = handler(message)
                    
                    # Wenn Response erwartet wird, sende zurück
                    if requires_response and result:
                        response = AgentMessage(
                            id=str(uuid.uuid4()),
                            from_agent=to_agent,
                            to_agent=from_agent,
                            message_type=MessageType.RESPONSE,
                            payload=result if isinstance(result, dict) else {"result": result},
                            correlation_id=correlation_id
                        )
                        return response
                except Exception as e:
                    logger.error(f"Message Handler Fehler für {to_agent}: {e}")
        
        return None
    
    async def query_agent(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sendet Query an Agent und wartet auf Response
        
        Args:
            from_agent: Sender Agent
            to_agent: Empfänger Agent
            query: Query
            context: Kontext
        
        Returns:
            Response
        """
        response = await self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.QUERY,
            payload={"query": query, "context": context or {}},
            requires_response=True
        )
        
        return response.payload if response else None


class SharedMemory:
    """
    Shared Memory
    
    Geteilter Speicher für Multi-Agent Workflows.
    """
    
    def __init__(self):
        """Initialisiert Shared Memory"""
        self.memory: Dict[str, Any] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
    
    async def set(self, key: str, value: Any, workflow_id: Optional[str] = None):
        """
        Setzt Wert in Shared Memory
        
        Args:
            key: Key
            value: Wert
            workflow_id: Workflow ID (optional, für Isolation)
        """
        full_key = f"{workflow_id}:{key}" if workflow_id else key
        
        if full_key not in self.locks:
            self.locks[full_key] = asyncio.Lock()
        
        async with self.locks[full_key]:
            self.memory[full_key] = value
    
    async def get(self, key: str, workflow_id: Optional[str] = None, default: Any = None) -> Any:
        """
        Holt Wert aus Shared Memory
        
        Args:
            key: Key
            workflow_id: Workflow ID (optional)
            default: Default-Wert
        
        Returns:
            Wert oder Default
        """
        full_key = f"{workflow_id}:{key}" if workflow_id else key
        return self.memory.get(full_key, default)
    
    async def delete(self, key: str, workflow_id: Optional[str] = None):
        """Löscht Wert aus Shared Memory"""
        full_key = f"{workflow_id}:{key}" if workflow_id else key
        if full_key in self.memory:
            del self.memory[full_key]


class WorkflowOrchestrator:
    """
    Workflow Orchestrator
    
    Orchestriert Multi-Agent Workflows.
    """
    
    def __init__(self):
        """Initialisiert Workflow Orchestrator"""
        self.workflows: Dict[str, MultiAgentWorkflow] = {}
        self.communication_bus = AgentCommunicationBus()
        self.shared_memory = SharedMemory()
    
    def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]]
    ) -> MultiAgentWorkflow:
        """
        Erstellt Workflow
        
        Args:
            name: Workflow Name
            steps: Workflow Steps
        
        Returns:
            MultiAgentWorkflow
        """
        workflow_id = str(uuid.uuid4())
        
        workflow_steps = [
            WorkflowStep(
                step_id=step.get("step_id", str(uuid.uuid4())),
                agent_name=step["agent_name"],
                action=step["action"],
                input_data=step.get("input_data", {}),
                dependencies=step.get("dependencies", [])
            )
            for step in steps
        ]
        
        workflow = MultiAgentWorkflow(
            workflow_id=workflow_id,
            name=name,
            steps=workflow_steps
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow {name} erstellt: {workflow_id}")
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Führt Workflow aus
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow Result
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} nicht gefunden")
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        
        try:
            # Führe Steps in Reihenfolge aus (mit Dependency-Check)
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                # Finde Steps die ausgeführt werden können
                ready_steps = [
                    step for step in workflow.steps
                    if step.step_id not in completed_steps
                    and all(dep in completed_steps for dep in step.dependencies)
                ]
                
                if not ready_steps:
                    # Deadlock oder fehlende Dependencies
                    workflow.status = WorkflowStatus.FAILED
                    raise ValueError("Workflow Deadlock oder fehlende Dependencies")
                
                # Führe Steps parallel aus
                tasks = [self._execute_step(workflow, step) for step in ready_steps]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for step, result in zip(ready_steps, results):
                    if isinstance(result, Exception):
                        step.status = "failed"
                        step.error = str(result)
                        workflow.status = WorkflowStatus.FAILED
                        raise result
                    else:
                        step.status = "completed"
                        step.output_data = result
                        completed_steps.add(step.step_id)
            
            # Workflow erfolgreich
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.result = {
                "success": True,
                "steps_completed": len(completed_steps),
                "shared_memory": workflow.shared_memory
            }
            
            return workflow.result
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.result = {
                "success": False,
                "error": str(e)
            }
            raise
    
    async def _execute_step(
        self,
        workflow: MultiAgentWorkflow,
        step: WorkflowStep
    ) -> Dict[str, Any]:
        """Führt einzelnen Step aus"""
        from apps.agents.core.agent_registry import get_registry
        
        step.status = "running"
        
        try:
            # Hole Agent
            registry = get_registry()
            agent = registry.get_agent(step.agent_name, account_id="workflow")
            
            if not agent:
                raise ValueError(f"Agent {step.agent_name} nicht gefunden")
            
            # Führe Action aus
            if hasattr(agent, step.action):
                action_method = getattr(agent, step.action)
                
                # Nutze Shared Memory für Input
                input_data = step.input_data.copy()
                for key, value in input_data.items():
                    if isinstance(value, str) and value.startswith("$memory."):
                        memory_key = value.replace("$memory.", "")
                        input_data[key] = await self.shared_memory.get(
                            memory_key,
                            workflow_id=workflow.workflow_id
                        )
                
                # Führe Action aus
                if asyncio.iscoroutinefunction(action_method):
                    result = await action_method(**input_data)
                else:
                    result = action_method(**input_data)
                
                # Speichere Output in Shared Memory
                if isinstance(result, dict):
                    for key, value in result.items():
                        await self.shared_memory.set(
                            f"step_{step.step_id}_{key}",
                            value,
                            workflow_id=workflow.workflow_id
                        )
                
                return result if isinstance(result, dict) else {"result": result}
            else:
                raise ValueError(f"Action {step.action} nicht gefunden in Agent {step.agent_name}")
                
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            raise


# Globale Instanzen
_global_communication_bus: Optional[AgentCommunicationBus] = None
_global_workflow_orchestrator: Optional[WorkflowOrchestrator] = None
_global_shared_memory: Optional[SharedMemory] = None


def get_communication_bus() -> AgentCommunicationBus:
    """Holt globale Communication Bus-Instanz"""
    global _global_communication_bus
    if _global_communication_bus is None:
        _global_communication_bus = AgentCommunicationBus()
    return _global_communication_bus


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """Holt globale Workflow Orchestrator-Instanz"""
    global _global_workflow_orchestrator
    if _global_workflow_orchestrator is None:
        _global_workflow_orchestrator = WorkflowOrchestrator()
    return _global_workflow_orchestrator


def get_shared_memory() -> SharedMemory:
    """Holt globale Shared Memory-Instanz"""
    global _global_shared_memory
    if _global_shared_memory is None:
        _global_shared_memory = SharedMemory()
    return _global_shared_memory
