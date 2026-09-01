from pydantic import BaseModel
from models import TaskSpec, ArchitecturePlan
from llm_client import chat_completion_json
import logging

logger = logging.getLogger(__name__)

ARCHITECTURE_PROMPT = """
You are an expert AI Software Architect.
Given a Task Specification, select the most appropriate execution architecture.

Supported Architectures:
1. single-agent       - One agent handles the complete task. Use for simple, focused tasks.
2. sequential         - Agents execute in a fixed order. Use when each stage depends on the previous.
3. parallel           - Independent agents run concurrently. Use when subtasks are independent.
4. router             - Classifies and routes requests to a specialist. Use when requests belong to distinct categories.
5. supervisor         - A supervisor dynamically delegates to specialized workers. Use when delegation is context-dependent.
6. orchestrator-workers - A central orchestrator decomposes tasks and coordinates workers. Use for complex dynamic tasks.
7. evaluator-optimizer - Generator + Evaluator loop. Use when output requires iterative critique and improvement.
8. handoff            - One agent transfers full responsibility to a specialist. Use when ownership must change completely.

Selection Rules:
- If the task is simple and focused → single-agent
- If stages have strict ordering → sequential
- If subtasks are independent → parallel
- If requests need classification → router
- If dynamic delegation to specialists is needed → supervisor
- If complex decomposition with multiple workers is needed → orchestrator-workers
- If iterative quality improvement is needed → evaluator-optimizer
- If complete ownership transfer to a specialist is needed → handoff

Your response MUST be a valid JSON object matching this structure:
{
  "architecture_type": "string (one of the 8 above)",
  "rationale": "string explaining why this architecture was selected",
  "num_agents": integer,
  "workers": ["list of worker names if architecture requires workers, else empty list"]
}
"""

async def plan_architecture(task: TaskSpec) -> ArchitecturePlan:
    """
    Takes a TaskSpec and selects an appropriate architecture based on the requirements.
    """
    logger.info("Planning architecture for TaskSpec...")
    user_context = (
        f"Goal: {task.goal}\n"
        f"Subtasks: {', '.join(task.subtasks)}\n"
        f"Needed Capabilities: {', '.join(task.required_capabilities)}"
    )
    
    data = await chat_completion_json(
        system_prompt=ARCHITECTURE_PROMPT,
        user_message=f"Please choose an architecture for the following task:\n{user_context}",
        temperature=0.1
    )
    
    return ArchitecturePlan(**data)
