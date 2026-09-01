"""Pydantic models for API request / response schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from typing import Optional, List, Dict, Any
import datetime


from pydantic import BaseModel, Field
from typing import List, Optional

class TaskSpec(BaseModel):
    goal: str
    subtasks: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)

class ArchitecturePlan(BaseModel):
    architecture_type: str = "single-agent"
    rationale: str
    num_agents: int = 1
    workers: Optional[List[str]] = None

class AgentSpec(BaseModel):
    name: str
    purpose: str
    architecture: str
    instructions: str
    skills: List[str] = []
    tools: List[str] = []
    inputs: List[str] = []
    outputs: List[str] = []
    # New Fields for Architecture Overhaul
    workflow: Optional[List[str]] = None
    workers: Optional[List[str]] = None
    worker_instructions: Optional[Dict[str, str]] = None
    routes: Optional[Dict[str, str]] = None
    constraints: Optional[str] = None

class AgentDefinition(BaseModel):
    """Declarative agent definition (mirrors agent.yaml)."""

    name: str = Field(..., max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(..., max_length=256)
    instructions: str = Field(..., min_length=0, max_length=32_000)
    model: str = "gpt-4o"
    tools: list[str] = []
    temperature: float = 0.7


class AgentCreateRequest(BaseModel):
    """Request to create an agent – either via natural language or explicit fields."""

    # If provided, the orchestrator will generate the definition from NL
    prompt: Optional[str] = None
    # If provided, these are used directly (manual mode)
    definition: Optional[AgentDefinition] = None


class AgentCreateResponse(BaseModel):
    name: str
    definition: AgentDefinition
    code: str  # generated Python source
    validation: ValidationResult
    message: str


class AgentEditRequest(BaseModel):
    """Request to edit an existing agent via natural language."""

    agent_name: str
    prompt: str  # natural language edit instruction


# ---------------------------------------------------------------------------
# Workflow models
# ---------------------------------------------------------------------------
class ExecutorDef(BaseModel):
    name: str
    type: str = "agent"  # "agent" | "function"
    instructions: str = ""
    model: str = "gpt-4o"


class EdgeDef(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None
    fan_in: bool = False


class WorkflowDefinition(BaseModel):
    """Declarative workflow definition (mirrors workflow.yaml)."""

    name: str = Field(..., max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(..., max_length=512)
    start: str
    executors: list[ExecutorDef]
    edges: list[EdgeDef]


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow – NL prompt or explicit definition."""

    prompt: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None


class WorkflowEditRequest(BaseModel):
    """Request to edit an existing workflow via natural language."""

    workflow_name: str
    prompt: str  # natural language edit instruction


class WorkflowCreateResponse(BaseModel):
    name: str
    definition: WorkflowDefinition
    code: str
    validation: ValidationResult
    message: str


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------
class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []

# 1. Detailed Task State
class TaskState(BaseModel):
    goal: Optional[str] = None
    integrations: list[str] = Field(default_factory=list)
    trigger: Optional[dict] = None
    conditions: list[dict] = Field(default_factory=list)
    actions: list[dict] = Field(default_factory=list)
    approval_policy: Optional[str] = None
    schedule: Optional[dict] = None
    output_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    proposed_plan: Optional[dict] = None
    status: str = "gathering_requirements"
# 2. Persistence Models (Can be mapped to DB/Redis later)
class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
class ChatSession(BaseModel):
    id: str
    status: str = "active"
    task_state: TaskState = Field(default_factory=TaskState)
    created_at: str
    updated_at: str
# 3. API Request Model (No longer trusts frontend with state)
class ChatRequest(BaseModel):
    session_id: str
    message: str
# Rebuild forward-ref models
AgentCreateResponse.model_rebuild()
WorkflowCreateResponse.model_rebuild()
