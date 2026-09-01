from models import AgentSpec
from llm_client import chat_completion_json
from core.template_resolver import TemplateResolver
from core.errors import GenerationError
import os
import yaml
import logging

logger = logging.getLogger(__name__)

GENERATOR_PROMPT = """
You are the Agent Generator for an AI Factory. 
Read the Agent Specification carefully.

If the architecture is "single-agent", provide instructions for that single agent.
If the architecture is "orchestrator-workers", you MUST provide instructions for the orchestrator, and a separate set of precise instructions for EACH worker specified in the "workers" list.

Be specific about the domain, boundaries, and expected JSON output structure if any.
Include safety guardrails and step-by-step reasoning directives.

Your response MUST be a valid JSON object matching this structure:
{
  "instructions": "The detailed system prompt text for the main agent or orchestrator",
  "worker_instructions": {
       "worker_name_1": "Instructions for worker 1",
       "worker_name_2": "Instructions for worker 2"
  } // Provide an empty object {} if no workers exist
}
"""

async def generate_agent_prompt(spec: AgentSpec) -> dict:
    """Uses LLM to write the precise system instructions for the new agent and its workers."""
    logger.info("Generating specialized instructions for the agent ecosystem...")
    workers_text = f"Workers needed: {', '.join(spec.workers)}" if spec.workers else "No workers needed."
    
    user_context = (
        f"Name: {spec.name}\n"
        f"Purpose: {spec.purpose}\n"
        f"Architecture: {spec.architecture}\n"
        f"{workers_text}\n"
        f"Tools Allowed: {', '.join(spec.tools)}\n"
        f"Skills Allowed: {', '.join(spec.skills)}\n"
        f"Expected Inputs: {', '.join(spec.inputs)}\n"
        f"Expected Outputs: {', '.join(spec.outputs)}"
    )
    
    data = await chat_completion_json(
        system_prompt=GENERATOR_PROMPT,
        user_message=user_context,
        temperature=0.3
    )
    
    raw_instructions = data.get("instructions", "You are a helpful AI assistant.")
    if isinstance(raw_instructions, dict):
        # Fallback in case the LLM still returns a dict for instructions
        raw_instructions = str(raw_instructions)

    return {
        "instructions": raw_instructions,
        "worker_instructions": data.get("worker_instructions", {})
    }


async def generate_agent_files(spec: AgentSpec, base_dir: str = "generated/agents") -> str:
    """
    Creates the physical files using Jinja2 Templates based on ArchitectureRegistry.
    """
    logger.info("Rendering agent templates to disk...")
    import re
    clean_name = re.sub(r'[^a-z0-9_]', '', spec.name.lower())
    if not clean_name: clean_name = "default_agent"
    
    agent_dir = os.path.join(base_dir, clean_name)
    os.makedirs(agent_dir, exist_ok=True)
    
    resolver = TemplateResolver()
    
    try:
        resolver.render_agent_files(spec, agent_dir)
        
        yaml_path = os.path.join(agent_dir, "agent.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(spec.model_dump(), f, allow_unicode=True, default_flow_style=False)
            
        return agent_dir
    except Exception as e:
        raise GenerationError(f"Failed to generate template: {e}")