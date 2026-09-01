from models import AgentSpec, ValidationResult
import os
import ast
import logging
from core.code_validator import validate_generated_project

logger = logging.getLogger(__name__)


def evaluate_agent(spec: AgentSpec, agent_dir: str) -> ValidationResult:
    """
    Evaluates the correctness of the generated project.
    Validates structure + Python syntax + File presence without executing malicious code.
    """
    logger.info("Evaluating generated agent correctness...")

    val_result = validate_generated_project(spec, agent_dir)

    return ValidationResult(
        valid=val_result.valid,
        errors=val_result.errors
    )