from typing import List, Dict
from models import AgentSpec, ValidationResult
import logging

logger = logging.getLogger(__name__)

def validate_agent_spec(spec: AgentSpec, available_skills: List[str], available_tools: List[str]) -> ValidationResult:
    """
    Validates the AgentSpec structurally BEFORE generating code.
    Checks for invalid architecture, unknown tools, unknown skills, missing required fields.
    """
    errors = []
    
    if not spec.name or not spec.name.strip():
        errors.append("Missing Agent Name")
        
    if not spec.purpose or not spec.purpose.strip():
        errors.append("Missing Purpose")
        
    valid_architectures = [
        "single-agent", "sequential", "parallel", "router", 
        "supervisor", "orchestrator-workers", "evaluator-optimizer", "handoff", "none"
    ]
    if spec.architecture not in valid_architectures:
        errors.append(f"Invalid Architecture: {spec.architecture}")
        
    # Check tools against single source of truth
    seen_tools = set()
    for tool in spec.tools:
        if tool not in available_tools:
            errors.append(f"Unknown Tool: {tool}")
        elif tool in seen_tools:
            errors.append(f"Duplicate Tool: {tool}")
        seen_tools.add(tool)
        
    # Check skills
    seen_skills = set()
    for skill in spec.skills:
        if skill not in available_skills:
            errors.append(f"Unknown Skill: {skill}")
        elif skill in seen_skills:
            errors.append(f"Duplicate Skill: {skill}")
        seen_skills.add(skill)

    return ValidationResult(valid=len(errors) == 0, errors=errors)
