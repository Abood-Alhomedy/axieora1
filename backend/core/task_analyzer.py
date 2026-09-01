from pydantic import BaseModel
from typing import List, Optional
from models import TaskSpec
from llm_client import chat_completion_json
import logging

logger = logging.getLogger(__name__)

# Prompt for the analyzer
TASK_ANALYZER_PROMPT = """
You are a highly capable AI Agent Architect.
Your task is to analyze the user's natural language request and turn it into a clear Task Specification (TaskSpec).

Identify:
- The main goal of the agent or system.
- The subtasks required to achieve the goal.
- The expected inputs and outputs.
- Any required capabilities (tools like web-search, python or skills like data-analysis).

Your response MUST be a valid JSON object matching the following structure:
{
  "goal": "string",
  "subtasks": ["string"],
  "inputs": ["string"],
  "outputs": ["string"],
  "required_capabilities": ["string"]
}
"""

async def analyze_task(user_request: str) -> TaskSpec:
    """
    Takes natural language user request and returns a Pydantic TaskSpec model.
    """
    logger.info("Analyzing user request to generate TaskSpec...")
    data = await chat_completion_json(
        system_prompt=TASK_ANALYZER_PROMPT,
        user_message=user_request,
        temperature=0.1
    )
    
    # Map the JSON dictionary to the Pydantic model
    return TaskSpec(**data)
