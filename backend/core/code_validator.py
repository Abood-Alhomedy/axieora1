import os
from pydantic import BaseModel
from typing import List, Optional
from core.errors import EvaluationError
import ast
import logging

logger = logging.getLogger(__name__)

class CodeValidationResult(BaseModel):
    valid: bool
    errors: List[str]

def validate_generated_project(spec, project_dir: str) -> CodeValidationResult:
    """
    Validates structure and syntax of the Jinja2 generated agent code.
    Ensures that for a specific architecture, all required files (e.g. workers) exist.
    Throws EvaluationError if generation essentially failed at core structure level.
    """
    errors = []
    
    agent_file = os.path.join(project_dir, "agent.py")
    if not os.path.exists(agent_file):
        raise EvaluationError(f"Critical failure: Missing {agent_file}")
        
    # Syntax check
    try:
        with open(agent_file, "r", encoding="utf-8") as f:
            ast.parse(f.read())
    except SyntaxError as e:
        errors.append(f"Syntax error in agent.py: {e}")
        
    # Architecture Specific Directory Checks
    if spec.architecture == "orchestrator-workers":
        workers_dir = os.path.join(project_dir, "workers")
        if not os.path.exists(workers_dir):
            errors.append("Missing 'workers' directory required by orchestrator-workers architecture.")
        else:
            if spec.workers:
                for worker in spec.workers:
                    w_file = os.path.join(workers_dir, f"{worker}.py")
                    if not os.path.exists(w_file):
                        errors.append(f"Missing expected worker file: {worker}.py")
                    else:
                        try:
                            with open(w_file, "r", encoding="utf-8") as f:
                                ast.parse(f.read())
                        except SyntaxError as e:
                            errors.append(f"Syntax error in {worker}.py: {e}")

    return CodeValidationResult(valid=len(errors) == 0, errors=errors)
