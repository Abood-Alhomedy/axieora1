"""Orchestrator Agent – uses Skills to create / edit Agents and Workflows.

This module implements the core logic that:
1. Loads the agent-creator and workflow-creator Skills
2. Uses LLM to interpret natural-language requests
3. Generates YAML + Python artefacts
4. Runs validation (in-process)
5. Persists results
"""
from __future__ import annotations

import uuid
from models import ChatMessage
from models import ChatSession
from datetime import datetime
from models import TaskState
from Tools.base import ToolRegistry
import json
import logging
import textwrap
from pathlib import Path

import yaml

# from config import AGENTS_DIR, AZURE_OPENAI_ENDPOINT, SKILLS_DIR, WORKFLOWS_DIR
from config import AGENTS_DIR, OPENROUTER_API_KEY, OPENROUTER_MODEL, SKILLS_DIR, WORKFLOWS_DIR
from llm_client import chat_completion, chat_completion_json
from models import (
    AgentCreateResponse,
    AgentDefinition,
    EdgeDef,
    ExecutorDef,
    ValidationResult,
    WorkflowCreateResponse,
    WorkflowDefinition,
)

from core.pipeline import run_agent_factory_pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Skill loading (progressive disclosure – stage 2: load full SKILL.md)
# ---------------------------------------------------------------------------

def _load_skill(name: str) -> str:
    """Read the full SKILL.md body for a named skill."""
    skill_path = SKILLS_DIR / name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill '{name}' not found at {skill_path}")
    text = skill_path.read_text(encoding="utf-8")
    # Strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


def _load_skill_resource(name: str, resource_path: str) -> str:
    """Read a skill resource file."""
    full_path = SKILLS_DIR / name / resource_path
    if not full_path.exists():
        raise FileNotFoundError(f"Skill resource not found: {full_path}")
    return full_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation helpers (in-process – avoids subprocess crash on --reload)
# ---------------------------------------------------------------------------

def _validate_agent_in_process(agent_dir: str) -> ValidationResult:
    """Validate agent artefacts directly (no subprocess)."""
    import ast
    errors: list[str] = []
    agent_path = Path(agent_dir)

    yaml_path = agent_path / "agent.yaml"
    if not yaml_path.exists():
        errors.append("agent.yaml not found")
    else:
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append("agent.yaml must be a YAML mapping")
            else:
                for field in ("name", "description", "instructions", "model"):
                    if field not in data:
                        errors.append(f"Missing required field: {field}")
                instructions = data.get("instructions", "")
                if isinstance(instructions, str):
                    if len(instructions) < 10:
                        errors.append(f"Instructions too short ({len(instructions)} chars, min 10)")
                    if len(instructions) > 32_000:
                        errors.append(f"Instructions too long ({len(instructions)} chars, max 32000)")
        except yaml.YAMLError as exc:
            errors.append(f"YAML parse error: {exc}")

    py_path = agent_path / "agent.py"
    if not py_path.exists():
        errors.append("agent.py not found")
    else:
        try:
            ast.parse(py_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"Python syntax error in agent.py: {exc}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def _validate_workflow_in_process(workflow_dir: str) -> ValidationResult:
    """Validate workflow artefacts directly (no subprocess)."""
    import ast
    errors: list[str] = []
    wf_path = Path(workflow_dir)

    yaml_path = wf_path / "workflow.yaml"
    if not yaml_path.exists():
        errors.append("workflow.yaml not found")
    else:
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append("workflow.yaml must be a YAML mapping")
            else:
                for field in ("name", "description", "start", "executors", "edges"):
                    if field not in data:
                        errors.append(f"Missing required field: {field}")

                executors = data.get("executors", [])
                edges = data.get("edges", [])
                start = data.get("start", "")
                executor_names = {e["name"] for e in executors if isinstance(e, dict) and "name" in e}

                if start and start not in executor_names:
                    errors.append(f"Start executor '{start}' not found in executor list")

                for i, edge in enumerate(edges):
                    if not isinstance(edge, dict):
                        errors.append(f"Edge {i} is not a mapping")
                        continue
                    src = edge.get("source", "")
                    tgt = edge.get("target", "")
                    if src not in executor_names:
                        errors.append(f"Edge {i}: source '{src}' not in executors")
                    if tgt not in executor_names:
                        errors.append(f"Edge {i}: target '{tgt}' not in executors")

                # Check graph connectivity (BFS from start)
                if start and executor_names and not errors:
                    adj: dict[str, list[str]] = {n: [] for n in executor_names}
                    for edge in edges:
                        if isinstance(edge, dict):
                            adj.setdefault(edge.get("source", ""), []).append(edge.get("target", ""))
                    visited: set[str] = set()
                    queue = [start]
                    while queue:
                        node = queue.pop(0)
                        if node in visited:
                            continue
                        visited.add(node)
                        queue.extend(adj.get(node, []))
                    unreachable = executor_names - visited
                    if unreachable:
                        errors.append(f"Unreachable executors from '{start}': {sorted(unreachable)}")

        except yaml.YAMLError as exc:
            errors.append(f"YAML parse error: {exc}")

    py_path = wf_path / "workflow.py"
    if not py_path.exists():
        errors.append("workflow.py not found")
    else:
        try:
            ast.parse(py_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"Python syntax error in workflow.py: {exc}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Agent creation
# ---------------------------------------------------------------------------

_AGENT_SYSTEM_PROMPT = """\
You are an expert AI agent designer for Microsoft Agent Framework.
Your task is to create a complete agent definition from the user's request.

You MUST return a JSON object with exactly these fields:
{
  "name": "snake_case_name",
  "description": "Short description",
  "instructions": "Detailed system prompt for the agent (200-2000 chars)",
  "model": "gpt-4o",
  "tools": [],
  "temperature": 0.7
}

Guidelines:
- name: lowercase snake_case, max 64 chars, derived from description
- instructions: Be specific. Include the agent's expertise, tone, constraints,
  response format guidance, and safety guardrails.
- description: One concise sentence
- Always include out-of-scope handling in instructions

IMPORTANT – Language Rule:
- Detect the language of the user's request.
- "description" and "instructions" MUST be written in the SAME language as the
  user's request. If the user writes in Japanese, respond in Japanese. If in
  English, respond in English.
- "name" is always snake_case ASCII.## Available Tools

The following tools are available to agents:

{AVAILABLE_TOOLS}

When creating an agent:
- Select only tools that are actually required by the user's request.
- The "tools" field must contain the tool IDs exactly as provided.
- Never invent tool IDs.
- If no tool is required, return an empty tools list.

"""


async def create_agent_from_prompt(prompt: str) -> AgentCreateResponse:
    """Create an agent using the new fully modular Agent Factory Pipeline."""
    logger.info(f"Starting modular pipeline for prompt: {prompt}")
    
    result = await run_agent_factory_pipeline(prompt)
    
    if result.get("status") in ["error", "missing_capability"]:
        # نعيد رسالة خطأ صريحة إن فشل الـ Pipeline
        msg = result.get('message', '')
        if result.get("status") == "missing_capability":
            msg += f" Missing: {result.get('missing')}"
        raise Exception(f"Pipeline flow error: {msg}")
        
    return AgentCreateResponse(
        name=result["name"],
        definition=AgentDefinition(
            name=result["name"],
            description=result.get("description", "Created via Modular Pipeline"),
            instructions=result.get("instructions", ""),
            model="gpt-4o",
            tools=result["tools"],
            temperature=0.7
        ),
        code=result["code"],
        validation=result["validation"],
        message="Agent created successfully based on the factory pipeline."
    )
    """Create an agent from a natural-language prompt."""

    # Load skill context for best practices
    skill_instructions = _load_skill("agent-creator")
    schema_ref = _load_skill_resource(
        "agent-creator",
        "references/AGENT_SCHEMA.md"
    )

    # Get all registered tools
    tool_catalog = "\n".join(
        f"- {tool['function']['name']}: "
        f"{tool['function']['description']}"
        for tool in ToolRegistry.get_all_llm_schemas()
    )

    if not tool_catalog:
        tool_catalog = "- No tools are currently registered."

    system = f"""
{_AGENT_SYSTEM_PROMPT}

## Available Tools

{tool_catalog}

## Skill Instructions

{skill_instructions}

## Schema Reference

{schema_ref}
"""

    logger.info("Available tools for agent creation:\n%s", tool_catalog)

    data = await chat_completion_json(
        system,
        f"Create an agent for: {prompt}"
    )

    definition = AgentDefinition(**data)
    return await _finalize_agent(definition)


async def create_agent_from_definition(definition: AgentDefinition) -> AgentCreateResponse:
    """Create an agent from an explicit definition."""
    return await _finalize_agent(definition)


async def edit_agent(agent_name: str, edit_prompt: str) -> AgentCreateResponse:
    """Edit an existing agent via natural language."""
    agent_dir = AGENTS_DIR / agent_name
    yaml_path = agent_dir / "agent.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"Agent '{agent_name}' not found")

    current_yaml = yaml_path.read_text(encoding="utf-8")

    skill_instructions = _load_skill("agent-creator")
    schema_ref = _load_skill_resource("agent-creator", "references/AGENT_SCHEMA.md")

    system = f"""{_AGENT_SYSTEM_PROMPT}

## Current Agent Definition (to be edited)
```yaml
{current_yaml}
```

## Skill Instructions
{skill_instructions}

## Schema Reference
{schema_ref}

Apply the user's edit request to the current agent.
Return the COMPLETE updated agent definition as JSON (not just the changes).
"""

    data = await chat_completion_json(system, f"Edit this agent: {edit_prompt}")

    definition = AgentDefinition(**data)
    return await _finalize_agent(definition)


async def _finalize_agent(definition: AgentDefinition) -> AgentCreateResponse:
    """Generate code, validate, and persist an agent definition."""
    agent_dir = AGENTS_DIR / definition.name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Write agent.yaml
    yaml_data = definition.model_dump()
    yaml_data["tools"] = definition.tools 
    yaml_path = agent_dir / "agent.yaml"
    yaml_path.write_text(yaml.dump(yaml_data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Generate agent.py
    code = _generate_agent_code(definition)
    py_path = agent_dir / "agent.py"
    py_path.write_text(code, encoding="utf-8")

    # Validate (in-process to avoid subprocess crash during --reload)
    validation = _validate_agent_in_process(str(agent_dir))

    return AgentCreateResponse(
        name=definition.name,
        definition=definition,
        code=code,
        validation=validation,
        message="Agent created successfully" if validation.valid else f"Agent created with validation errors: {validation.errors}",
    )


def _generate_agent_code(defn: AgentDefinition) -> str:
    """Generate executable Python code for an agent using Agent Framework's Agent class."""
    tools_import = ""
    tools_list = ""
    if defn.tools:
        tools_list = "\nTOOLS = " + repr(defn.tools) + "\n"

    instructions_escaped = defn.instructions.replace('"""', '\\"\\"\\"')

    lines = [
        f'"""Agent: {defn.name} – {defn.description}',
        '',
        'Auto-generated by the Agent Creator skill.',
        'Uses OpenRouter via AsyncOpenAI.',
        '"""',
        '',
        'import asyncio',
        'import os',
        '',
        'from openai import AsyncOpenAI',
    ]
    if tools_import:
        lines.append(tools_import)
    lines += [
        '',
        f'API_KEY = os.environ.get("OPENROUTER_API_KEY", "{OPENROUTER_API_KEY}")',
        f'MODEL = os.environ.get("OPENROUTER_MODEL", "{OPENROUTER_MODEL}")',
        '',
        'INSTRUCTIONS = """\\',
        instructions_escaped,
        '"""',
    ]
    if tools_list:
        lines.append(tools_list)
    lines += [
        '',
        '',
        'async def chat(message: str) -> str:',
        '    """Send a message and return the response."""',
        '    client = AsyncOpenAI(',
        '        base_url="https://openrouter.ai/api/v1",',
        '        api_key=API_KEY,',
        '    )',
        '    resp = await client.chat.completions.create(',
        '        model=MODEL,',
        '        messages=[',
        '            {"role": "system", "content": INSTRUCTIONS},',
        '            {"role": "user", "content": message},',
        '        ],',
        '    )',
        '    return resp.choices[0].message.content or ""',
        '',
        '',
        'async def main():',
        '    """Run the agent with a sample message."""',
        '    response = await chat("Hello! What can you help me with?")',
        '    print(response)',
        '',
        '',
        'if __name__ == "__main__":',
        '    asyncio.run(main())',
        '',
    ]
    return '\n'.join(lines)


def _generate_agent_code_raw(name: str, description: str, instructions: str, model: str) -> str:
    """Generate agent Python code using Agent Framework's Agent class directly.
    
    Does not require an AgentDefinition object (useful for workflow executor
    names that may not pass Pydantic validation).
    """
    instructions_escaped = instructions.replace('"""', '\\"\\"\\"')
    lines = [
        f'"""Agent: {name} – {description}',
        '',
        'Auto-generated from workflow executor.',
        'Uses Microsoft Agent Framework\'s Agent class directly.',
        '"""',
        '',
        # 'import asyncio',
        # 'import os',
        # '',
        # 'from azure.identity.aio import DefaultAzureCredential',
        # 'from agent_framework import Agent',
        # 'from agent_framework.azure import AzureOpenAIChatClient',
        # '',
        # f'ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "{AZURE_OPENAI_ENDPOINT}")',
        # f'DEPLOYMENT = "{model}"',
        # '',
        # 'INSTRUCTIONS = """\\',
        # instructions_escaped,
        # '"""',
        # '',
        # '',
        # 'async def create_agent() -> Agent:',
        # '    """Create and return the configured Agent instance."""',
        # '    credential = DefaultAzureCredential()',
        # '    client = AzureOpenAIChatClient(',
        # '        credential=credential,',
        # '        endpoint=ENDPOINT,',
        # '        deployment=DEPLOYMENT,',
        # '    )',

        'import asyncio',
        'import os',
        '',
        'from agent_framework import Agent',
        'from agent_framework.openai import OpenAIChatClient',
        '',
        f'API_KEY = os.environ.get("OPENROUTER_API_KEY", "{OPENROUTER_API_KEY}")',
        f'MODEL = os.environ.get("OPENROUTER_MODEL", "{OPENROUTER_MODEL}")',
        '',
        'INSTRUCTIONS = """\\',
        instructions_escaped,
        '"""',
        '',
        '',
        'async def create_agent() -> Agent:',
        '    """Create and return the configured Agent instance."""',
        '    client = OpenAIChatClient(',
        '        api_key=API_KEY,',
        '        base_url="https://openrouter.ai/api/v1",',
        '        model=MODEL,',
        '    )',
        '',
        '    agent = Agent(',
        f'        name="{name}",',
        '        instructions=INSTRUCTIONS,',
        '        model_client=client,',
        '        model_settings={"temperature": 0.7},',
        '    )',
        '    return agent',
        '',
        '',
        'async def main():',
        '    """Run the agent with a sample message."""',
        '    agent = await create_agent()',
        '    response = await agent.run("Hello! What can you help me with?")',
        '    print(response.text)',
        '',
        '',
        'if __name__ == "__main__":',
        '    asyncio.run(main())',
        '',
    ]
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Workflow creation
# ---------------------------------------------------------------------------

_WORKFLOW_SYSTEM_PROMPT = """\
You are an expert workflow designer for Microsoft Agent Framework.
Your task is to create a complete workflow definition from the user's request.

You MUST return a JSON object with exactly these fields:
{
  "name": "snake_case_name",
  "description": "What the workflow does",
  "start": "name_of_starting_executor",
  "executors": [
    {
      "name": "executor_name",
      "type": "agent|function",
      "instructions": "What this executor does",
      "model": "gpt-4o"
    }
  ],
  "edges": [
    {
      "source": "source_executor_name",
      "target": "target_executor_name",
      "condition": "optional condition description or null",
      "fan_in": false
    }
  ]
}

Guidelines:
- Identify each processing step as an executor
- If a step needs LLM reasoning → type "agent"
- If a step is pure logic/transformation → type "function"
- Map data flow with edges:
  - "then/next" → direct edge
  - "if ... else" → conditional edges
  - "in parallel" → fan-out (multiple edges from same source)
  - "combine/merge" → fan-in edges
- All executor names must be snake_case
- Every executor must be reachable from start

IMPORTANT – Language Rule:
- Detect the language of the user's request.
- "description" and all executor "instructions" MUST be written in the SAME
  language as the user's request. If the user writes in Japanese, respond in
  Japanese. If in English, respond in English.
- "name" fields are always snake_case ASCII.
"""


async def create_workflow_from_prompt(prompt: str) -> WorkflowCreateResponse:
    """Create a workflow from a natural-language prompt."""
    skill_instructions = _load_skill("workflow-creator")
    patterns_ref = _load_skill_resource("workflow-creator", "references/WORKFLOW_PATTERNS.md")

    system = f"{_WORKFLOW_SYSTEM_PROMPT}\n\n## Skill Instructions\n{skill_instructions}\n\n## Workflow Patterns\n{patterns_ref}"

    data = await chat_completion_json(system, f"Create a workflow for: {prompt}")

    # Parse executors and edges
    executors = [ExecutorDef(**e) for e in data.get("executors", [])]
    edges = [EdgeDef(**e) for e in data.get("edges", [])]

    definition = WorkflowDefinition(
        name=data["name"],
        description=data["description"],
        start=data["start"],
        executors=executors,
        edges=edges,
    )
    return await _finalize_workflow(definition)


async def create_workflow_from_definition(definition: WorkflowDefinition) -> WorkflowCreateResponse:
    """Create a workflow from an explicit definition."""
    return await _finalize_workflow(definition)


async def edit_workflow(workflow_name: str, edit_prompt: str) -> WorkflowCreateResponse:
    """Edit an existing workflow via natural language."""
    wf_dir = WORKFLOWS_DIR / workflow_name
    yaml_path = wf_dir / "workflow.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"Workflow '{workflow_name}' not found")

    current_yaml = yaml_path.read_text(encoding="utf-8")
    current_data = yaml.safe_load(current_yaml)

    skill_instructions = _load_skill("workflow-creator")

    system = f"""{_WORKFLOW_SYSTEM_PROMPT}

## Current Workflow Definition (to be edited)
```yaml
{current_yaml}
```

## Skill Instructions
{skill_instructions}

Apply the user's edit request to the current workflow.
Return the COMPLETE updated workflow definition as JSON (not just the changes).
"""

    data = await chat_completion_json(system, f"Edit this workflow: {edit_prompt}")

    executors = [ExecutorDef(**e) for e in data.get("executors", [])]
    edges = [EdgeDef(**e) for e in data.get("edges", [])]

    definition = WorkflowDefinition(
        name=data["name"],
        description=data["description"],
        start=data["start"],
        executors=executors,
        edges=edges,
    )
    return await _finalize_workflow(definition)


async def _finalize_workflow(definition: WorkflowDefinition) -> WorkflowCreateResponse:
    """Generate code, validate, and persist a workflow definition."""
    wf_dir = WORKFLOWS_DIR / definition.name
    wf_dir.mkdir(parents=True, exist_ok=True)

    # Write workflow.yaml
    yaml_data = definition.model_dump()
    yaml_path = wf_dir / "workflow.yaml"
    yaml_path.write_text(yaml.dump(yaml_data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Generate workflow.py
    code = _generate_workflow_code(definition)
    py_path = wf_dir / "workflow.py"
    py_path.write_text(code, encoding="utf-8")

    # Auto-register agent-type executors as standalone agents
    _register_workflow_agents(definition)

    # Validate (in-process to avoid subprocess crash during --reload)
    validation = _validate_workflow_in_process(str(wf_dir))

    return WorkflowCreateResponse(
        name=definition.name,
        definition=definition,
        code=code,
        validation=validation,
        message="Workflow created successfully" if validation.valid else f"Workflow created with validation errors: {validation.errors}",
    )


def _register_workflow_agents(definition: WorkflowDefinition) -> None:
    """Auto-register each agent-type executor as a standalone agent."""
    for executor in definition.executors:
        if executor.type != "agent":
            continue

        try:
            agent_dir = AGENTS_DIR / executor.name
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Build agent definition
            description = (executor.instructions[:120] if executor.instructions
                           else f"Agent node from workflow '{definition.name}'")
            instructions = (executor.instructions
                            or f"You are {executor.name}. Process the input and produce a result.")

            agent_yaml = {
                "name": executor.name,
                "description": description,
                "instructions": instructions,
                "model": executor.model or "gpt-4o",
                "tools": [],
                "temperature": 0.7,
                "source_workflow": definition.name,
            }
            yaml_path = agent_dir / "agent.yaml"
            yaml_path.write_text(
                yaml.dump(agent_yaml, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

            # Generate agent.py using safe construction (skip Pydantic validation
            # which may reject names that are valid workflow executor names)
            instructions_escaped = instructions.replace('"""', '\\"\\"\\"')
            code = _generate_agent_code_raw(
                name=executor.name,
                description=description[:256],
                instructions=instructions,
                model=executor.model or "gpt-4o",
            )
            py_path = agent_dir / "agent.py"
            py_path.write_text(code, encoding="utf-8")

            logger.info("Auto-registered agent '%s' from workflow '%s'", executor.name, definition.name)
        except Exception:
            logger.exception("Failed to register agent '%s' from workflow '%s'", executor.name, definition.name)


def _generate_workflow_code(defn: WorkflowDefinition) -> str:
    """Generate executable Python code for a workflow using Agent Framework.

    Architecture:
    - Agent-type executors are imported from generated/agents/{name}/agent.py
      via their `create_agent()` function, then passed directly to
      WorkflowBuilder (which auto-wraps them in AgentExecutor).
    - Function-type executors remain as inline Executor subclasses.
    - Conditional edges use `add_switch_case_edge_group` with Case/Default.
    - Edits to agents in the Agent tab are automatically reflected in the
      workflow because the agent modules are imported, not duplicated.
    """

    agent_executors = [ex for ex in defn.executors if ex.type == "agent"]
    func_executors = [ex for ex in defn.executors if ex.type != "agent"]

    # --- Imports ----------------------------------------------------------
    imports: list[str] = [
        f'"""Workflow: {defn.name} – {defn.description}',
        '',
        'Auto-generated by the Workflow Creator skill.',
        'Uses Microsoft Agent Framework with AgentExecutor wrapping Agent instances.',
        '',
        'Agent-type nodes are imported from the agents tab (generated/agents/).',
        'Editing an agent in the Agent tab will be automatically reflected here.',
        '"""',
        '',
        'import asyncio',
        'import os',
        'import sys',
        '',
        '# Add the generated agents directory to the import path',
        '# so we can import each agent module by folder name.',
        '_AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "agents")',
        'if _AGENTS_DIR not in sys.path:',
        '    sys.path.insert(0, _AGENTS_DIR)',
        '',
    ]

    # Conditional imports based on what's needed
    framework_items: list[str] = ['WorkflowBuilder']
    if func_executors:
        framework_items.extend(['Executor', 'WorkflowContext', 'handler'])

    # Check if we need Case/Default for switch-case edge groups
    has_conditions = any(e.condition for e in defn.edges)
    if has_conditions:
        framework_items.extend(['Case', 'Default'])

    imports.append(f'from agent_framework import {", ".join(framework_items)}')
    imports.append('')

    # --- Agent imports (from agents tab) ----------------------------------
    agent_import_lines: list[str] = []
    agent_import_lines.append('')
    agent_import_lines.append('# -- Import agents from the Agent tab ------------------------------------')
    agent_import_lines.append('# These are auto-registered when the workflow is created.')
    agent_import_lines.append('# Edit them in the Agent tab and changes are reflected here automatically.')
    agent_import_lines.append('')
    for ex in agent_executors:
        # Import create_agent as create_{name}
        alias = f'create_{ex.name}'
        agent_import_lines.append(
            f'from {ex.name}.agent import create_agent as {alias}'
            f'  # noqa: E402'
        )
    agent_import_lines.append('')

    # --- Function executor classes ----------------------------------------
    func_class_lines: list[str] = []
    func_instance_lines: list[str] = []
    if func_executors:
        func_class_lines.append('')
        func_class_lines.append(
            '# -- Function Executors '
            '-------------------------------------------------'
        )
        func_class_lines.append('')
        for ex in func_executors:
            class_name = "".join(w.capitalize() for w in ex.name.split("_"))
            instr_escaped = ex.instructions.replace('"""', '\\"\\"\\"')
            func_class_lines.extend([
                f'class {class_name}(Executor):',
                f'    """Function Executor: {ex.name} – {ex.instructions[:80]}"""',
                '',
                '    @handler',
                '    async def handle(self, message, ctx: WorkflowContext) -> None:',
                f'        # {instr_escaped[:200]}',
                f'        result = f"[{ex.name}] processed: {{message}}"',
                '        await ctx.send_message(result)',
                '',
                '',
            ])
            func_instance_lines.append(f'{ex.name} = {class_name}()')

    # --- Build workflow function ------------------------------------------
    build_lines: list[str] = [
        '',
        '# -- Build Workflow '
        '-----------------------------------------------------',
        '',
        'async def build_workflow():',
        '    """Create Agent instances and assemble the workflow graph.',
        '',
        '    Agent instances are created by calling create_agent() from each',
        '    agent module. WorkflowBuilder auto-wraps them in AgentExecutor.',
        '    """',
    ]

    # Create agent instances
    if agent_executors:
        build_lines.append('    # Create agents (imported from agents tab)')
        for ex in agent_executors:
            build_lines.append(f'    {ex.name} = await create_{ex.name}()')
        build_lines.append('')

    # Build workflow
    build_lines.append(f'    builder = WorkflowBuilder(start_executor={defn.start})')
    build_lines.append('')

    # --- Edges ------------------------------------------------------------
    # Group edges by source to detect switch-case patterns
    edges_by_source: dict[str, list] = {}
    for edge in defn.edges:
        edges_by_source.setdefault(edge.source, []).append(edge)

    fan_in_targets: dict[str, list[str]] = {}

    for source_name, source_edges in edges_by_source.items():
        # Separate fan-in from regular edges
        regular = [e for e in source_edges if not e.fan_in]
        fan_in = [e for e in source_edges if e.fan_in]

        for e in fan_in:
            fan_in_targets.setdefault(e.target, []).append(e.source)

        conditional = [e for e in regular if e.condition]
        unconditional = [e for e in regular if not e.condition]

        if conditional:
            # Use switch-case pattern: Case for each condition, Default for
            # the last one if there's no explicit default
            build_lines.append(f'    # Conditional routing from {source_name}')
            build_lines.append(f'    builder.add_switch_case_edge_group(')
            build_lines.append(f'        {source_name},')
            build_lines.append(f'        [')
            for i, ce in enumerate(conditional):
                cond_str = ce.condition.replace('"', '\\"')
                # For the last conditional edge, make it Default if no
                # unconditional edges exist
                if i == len(conditional) - 1 and not unconditional:
                    build_lines.append(
                        f'            Default(target={ce.target}),'
                        f'  # fallback: {cond_str}'
                    )
                else:
                    build_lines.append(
                        f'            Case('
                        f'condition=lambda data: '
                        f'"{ce.condition.lower()}" in str(data).lower(), '
                        f'target={ce.target}),  # {cond_str}'
                    )
            if unconditional:
                # Add the first unconditional edge as Default
                build_lines.append(
                    f'            Default(target={unconditional[0].target}),'
                )
            build_lines.append(f'        ],')
            build_lines.append(f'    )')
            # Add remaining unconditional edges as regular edges
            for ue in unconditional[1:]:
                build_lines.append(
                    f'    builder.add_edge({source_name}, {ue.target})'
                )
        else:
            for ue in unconditional:
                build_lines.append(
                    f'    builder.add_edge({source_name}, {ue.target})'
                )

    # Fan-in edges
    for target, sources in fan_in_targets.items():
        sources_str = ", ".join(sources)
        build_lines.append(
            f'    builder.add_fan_in_edges([{sources_str}], {target})'
        )

    build_lines.extend([
        '',
        '    return builder.build()',
    ])

    # --- Main -------------------------------------------------------------
    main_lines = [
        '',
        '',
        'async def main():',
        '    workflow = await build_workflow()',
        '    events = await workflow.run("Hello, start the workflow!")',
        '    print(f"Workflow output: {events.get_outputs()}")',
        '',
        '',
        'if __name__ == "__main__":',
        '    asyncio.run(main())',
        '',
    ]

    # --- Assemble ---------------------------------------------------------
    all_lines = imports + agent_import_lines
    if func_class_lines:
        all_lines += func_class_lines
    if func_instance_lines:
        all_lines += [''] + func_instance_lines
    all_lines += build_lines + main_lines

    return '\n'.join(all_lines)
SESSIONS: dict[str, ChatSession] = {}
MESSAGES: dict[str, list[ChatMessage]] = {}
def get_or_create_session(session_id: str) -> ChatSession:
    if session_id not in SESSIONS:
        now = datetime.now().isoformat()
        SESSIONS[session_id] = ChatSession(
            id=session_id,
            created_at=now,
            updated_at=now
        )
        MESSAGES[session_id] = []
    return SESSIONS[session_id]
def save_message(session_id: str, role: str, content: str):
    msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content
    )
    MESSAGES[session_id].append(msg)
    return msg
_COPILOT_SYSTEM_PROMPT = """\
You are an Agentic Copilot for creating real Microsoft Agent Framework agents and workflows.

Your job is to understand the user's request, maintain a structured TaskState, identify missing requirements, and decide what should happen next.

Current TaskState:
{TASK_STATE}

Available Tools:
{AVAILABLE_TOOLS}

You MUST return ONLY one valid JSON object with exactly these fields:

{{
  "updated_task_state": {{
    "goal": null,
    "integrations": [],
    "trigger": null,
    "conditions": [],
    "actions": [],
    "approval_policy": null,
    "schedule": null,
    "output_requirements": [],
    "constraints": [],
    "missing_requirements": [],
    "proposed_plan": null,
    "status": "gathering_requirements"
  }},
  "decision": "ASK_USER",
  "message_to_user": "",
  "questions": [],
  "tool_name": "",
  "tool_args": {{}}
}}

TASK STATE RULES:

1. "updated_task_state" MUST contain the COMPLETE TaskState.
   Never return only changed fields.

2. "trigger" MUST be either null or an OBJECT.
   NEVER make trigger a string.

3. A trigger object should use this structure:

   {{
     "type": "trigger_type",
     "name": "human readable name",
     "config": {{}}
   }}

4. "actions" MUST ALWAYS be an ARRAY OF OBJECTS.
   NEVER use an array of strings.

5. Every action object should use this structure:

   {{
     "type": "tool_id_or_action_type",
     "name": "human readable name",
     "config": {{}}
   }}

6. "conditions" MUST ALWAYS be an ARRAY OF OBJECTS.
   NEVER use an array of strings.

7. "config" MUST ALWAYS be an OBJECT.

8. Tool IDs MUST come from the Available Tools list.
   NEVER invent a tool ID.

9. If the user requests an operation that requires a registered tool,
   use the exact tool ID from Available Tools.

10. For example, if Available Tools contains:

   gmail_send

   then an email sending action may be represented as:

   {{
     "type": "gmail_send",
     "name": "إرسال البريد الإلكتروني",
     "config": {{}}
   }}

11. Do NOT represent actions like this:

   "actions": [
     "الرد التلقائي على البريد الإلكتروني"
   ]

   That is INVALID.

12. The correct representation is:

   "actions": [
     {{
       "type": "gmail_send",
       "name": "الرد التلقائي على البريد الإلكتروني",
       "config": {{}}
     }}
   ]

13. Do not invent critical information.
   For example, do not invent:
   - email addresses
   - email subject
   - email body
   - schedules
   - conditions
   - credentials

14. If required information is missing:
   - add it to "missing_requirements"
   - set decision to "ASK_USER"
   - ask for it using "message_to_user"
   - keep status as "gathering_requirements"

15. If all required information is available:
   - set decision to "BUILD_AGENT"
   - set status to "ready_for_building"
   BUILD READINESS RULES:

15A. "BUILD_AGENT" is a strict decision and MUST NOT be used
     unless the agent requirements are sufficiently specified.

15B. A generic intention to create an agent is NOT sufficient.

     For example:

     "اريد وكيل"
     "أريد إنشاء وكيل"
     "أريد Agent"
     "أريد وكيل للذكاء الاصطناعي"

     MUST result in:

     - decision = "ASK_USER"
     - status = "gathering_requirements"
     - non-empty "missing_requirements"
     - a useful "message_to_user"
     - "questions" when predefined choices are useful
15C. Before "BUILD_AGENT", the following must be sufficiently
     known from the user's conversation:

     - the specific goal or responsibility of the agent
     - what action or actions the agent should perform
     - what should trigger the agent, ONLY IF the agent's behavior
       depends on an explicit trigger (e.g. schedule, webhook, event).
       A simple on-demand/reactive agent does NOT require a trigger.
     - required integrations or tools, when the requested behavior
       depends on them

15D. Do NOT consider a requirement satisfied merely because the
     corresponding TaskState field exists.

     A field containing null, an empty array, an empty object,
     or a vague generic value does NOT satisfy a required
     requirement.

15E. If the user's goal is vague or generic, the goal is NOT
     considered sufficiently specified.

15F. If the trigger is unknown and the agent's behavior depends
     on a trigger, ask the user for the trigger.

15G. If the required action is unknown, ask the user what the
     agent should do.

15H. If a required integration or tool is unknown but can be
     determined from the user's intended behavior, ask the user
     instead of assuming one.

15I. When any essential requirement is missing or ambiguous:

     - decision MUST be "ASK_USER"
     - status MUST remain "gathering_requirements"
     - add the missing information to "missing_requirements"
     - ask the user for the missing information
     - do NOT generate an agent
     - do NOT call the agent creation process

15J. Never infer that the agent is ready merely because the user
     used words such as "create", "build", "make", or "I want an
     agent".

15K. The following example MUST produce ASK_USER:

     User:
     "اريد وكيل"

     Correct reasoning:

     - specific goal is missing
     - trigger is missing
     - action is missing

     Therefore:

     - decision = "ASK_USER"
     - status = "gathering_requirements"
     - missing_requirements is NOT empty

15L. Only use "BUILD_AGENT" after the conversation contains
     enough concrete information to create a useful agent without
     inventing critical requirements.

16. "tool_name" MUST be an empty string unless decision is "CALL_TOOL".

17. "tool_args" MUST be an empty object unless decision is "CALL_TOOL".

18. Preserve information already present in TaskState unless the user explicitly changes it.
18A. Never mark a requirement as satisfied based only on an
     assumption or generic wording.

18B. Empty arrays, null values, and vague generic text must remain
     unresolved when that information is required to build the agent.

18C. "missing_requirements" MUST accurately describe all essential
     information that is still unknown.
18D. When decision is "ASK_USER", "missing_requirements" should
     normally contain at least one concrete missing requirement.

18E. Distinguish between the user's intention to create an agent
     and the actual goal of the agent.

     Example:

     "اريد وكيل"

     means the user wants to create an agent, but it does NOT
     specify the agent's goal.

     Therefore it MUST NOT be treated as a completed "goal".

     Example:

     "أريد وكيلاً يرد تلقائياً على رسائل العملاء عبر Gmail"

     contains an actual agent goal and may satisfy the goal
     requirement, but other requirements may still be missing.

19. The user's language should be preserved in:
   - goal
   - trigger.name
   - action.name
   - message_to_user
   - missing_requirements
   - proposed_plan descriptions
20. Return ONLY JSON.
   Do not return Markdown.
   Do not use ```json.
   Do not add explanations outside the JSON.

21. Valid values for "decision" are exactly:
    "ASK_USER", "BUILD_AGENT", "CALL_TOOL", or "CHAT"
    (use "CHAT" only for conversational replies that don't change
    TaskState and don't require gathering more info, e.g. greetings
    or clarifying small talk).

QUESTION / OPTIONS RULES:
1. When decision is "ASK_USER", determine whether the missing
   requirement can reasonably be represented by a small set of
   predefined choices.

2. If predefined choices are useful, return them in the
   "questions" field.

3. "questions" MUST always be an array.

4. Each question MUST have this structure:

{{
  "id": "unique_question_id",
  "question": "Human-readable question",
  "options": [
   {{
      "label": "Human-readable option",
      "value": "machine-readable value"
    }}
  ],
  "default_value": "value_of_suggested_option"
}}

5. "default_value" is ONLY a recommended option.

6. NEVER treat "default_value" as the user's answer.

7. NEVER update TaskState using "default_value" unless the user
   explicitly selects that option.

8. The user is ALWAYS allowed to answer using the normal chat
   input, even when predefined options are displayed.

9. The predefined options are only shortcuts that make answering
   easier and faster.

10. If the user writes a custom answer instead of selecting one
    of the options, treat the user's written answer as the actual
    answer.

11. Never reject a user's custom answer merely because it is not
    one of the predefined options.

12. Do NOT create a separate "custom answer" UI or require the
    user to choose from the predefined options.

13. The existing chat input remains the primary free-form input.

14. "label" is the text displayed to the user.

15. "value" is the machine-readable value used internally.

16. "default_value" MUST either match one of the option values or
    be null.

17. If there is no reasonable suggested option, use null for
    "default_value".

18. Use approximately 2-5 options when choices are useful.

19. Do not generate options merely for the sake of generating
    options.

    However, when the missing requirement can be reasonably
    narrowed down using common categories or choices, you SHOULD
    provide 2-5 predefined options.

    Examples include:

    - type or category of agent
    - type of trigger
    - type of integration
    - type of action
    - communication channel
    - common workflow type

    The options are suggestions only. The user can always provide
    a completely different free-form answer through the normal
    chat input.

20. If the user only says that they want an agent and the agent
    goal is unknown, prefer asking:

    "ما نوع المهمة التي تريد أن ينفذها الوكيل؟"

    and provide useful starter options when possible.

21. If the missing requirement genuinely cannot be represented
    by a small set of reasonable choices, return:

    "questions": []

    and ask for the information using "message_to_user".

22. Never omit useful predefined options merely because the user
    can provide a free-form answer.
23. The question and option labels MUST use the same language as
    the user's request.

24. Do not put the options inside "message_to_user". Options
    belong exclusively to "questions".

25. When the user explicitly selects one of the predefined
    options, treat that selected option as the user's answer.

26. When the user writes a free-form answer, use the free-form
    answer as the user's answer even if it does not match any
    predefined option.

27. Never assume that the user selected the default option merely
    because it was marked as default.
     USER OPTION SELECTION:

When the user response represents a selected predefined option,
the system may receive:

{{
  "question_id": "...",
  "answer": "...",
  "answer_label": "..."
}}
EXAMPLE — GENERIC AGENT REQUEST:

User:
"اريد وكيل"

Correct response:

{{
  "updated_task_state": {{
    "goal": null,
    "integrations": [],
    "trigger": null,
    "conditions": [],
    "actions": [],
    "approval_policy": null,
    "schedule": null,
    "output_requirements": [],
    "constraints": [],
    "missing_requirements": [
      "الهدف المحدد للوكيل"
    ],
    "proposed_plan": null,
    "status": "gathering_requirements"
  }},
  "decision": "ASK_USER",
  "message_to_user": "ما نوع المهمة التي تريد أن ينفذها الوكيل؟",
  "questions": [
    {{
      "id": "agent_goal",
      "question": "ما نوع المهمة التي تريد أن ينفذها الوكيل؟",
      "options": [
        {{
          "label": "خدمة العملاء",
          "value": "customer_support"
        }},
        {{
          "label": "البريد الإلكتروني",
          "value": "email_automation"
        }},
        {{
          "label": "متابعة الطلبات",
          "value": "order_followup"
        }},
        {{
          "label": "المبيعات",
          "value": "sales"
        }}
      ],
      "default_value": null
    }}
  ],
  "tool_name": "",
  "tool_args": {{}}
}}
In this case:

- "answer" is the selected machine-readable value.
- "answer_label" is the human-readable selected option.
- Treat the selected option as the user's explicit answer.
- Update TaskState based on the selected answer.
- Do not treat default_value as an answer unless the user
  explicitly selected that option.
  QUESTION CONTINUATION:

After the user explicitly answers a question, do not ask the
same question again unless the user's answer is ambiguous or
incomplete.

If the answer satisfies the missing requirement:

- update TaskState
- remove that requirement from missing_requirements
- continue gathering the next missing requirement
- or build the agent if all requirements are satisfied
"""
async def run_copilot_turn(session_id: str, user_message: str):
    session = get_or_create_session(session_id)
    save_message(session_id, "user", user_message)

    history = MESSAGES[session_id][-10:]
    formatted_history = "\n".join(
        f"{m.role}: {m.content}"
        for m in history
    )

    # Build the real tool catalog from the registered tools.
    tool_catalog = "\n".join(
        f"- {tool['function']['name']}: {tool['function']['description']}"
        for tool in ToolRegistry.get_all_llm_schemas()
    )

    if not tool_catalog:
        tool_catalog = "- No tools are currently registered."

    # Give the Copilot the current state AND the real available tools.
    prompt = _COPILOT_SYSTEM_PROMPT.format(
        TASK_STATE=session.task_state.model_dump_json(),
        AVAILABLE_TOOLS=tool_catalog,
    )

    user_prompt = (
        f"History:\n{formatted_history}\n\n"
        f"New Message: {user_message}"
    )

    response_data = await chat_completion_json(
        prompt,
        user_prompt
    )

    updated_state_dict = response_data.get(
        "updated_task_state",
        {}
    )

    decision = response_data.get(
        "decision",
        "CHAT"
    )

    message_to_user = response_data.get(
        "message_to_user",
        ""
    )
    questions = response_data.get(
        "questions",
        []
    )
    # Validate the LLM output against the real TaskState schema.
    session.task_state = TaskState(
        **updated_state_dict
    )

    session.updated_at = datetime.now().isoformat()

    if decision in ["ASK_USER", "CHAT"]:
        save_message(
            session_id,
            "assistant",
            message_to_user,
       
        )

        return {
            "status": "waiting_for_user",
            "decision": decision,
            "message": message_to_user,
            "questions": questions,
            "state": session.task_state.model_dump(),
        }

    elif decision == "BUILD_AGENT":
        save_message(
            session_id,
            "assistant",
            "All requirements gathered. Generating the Agent Definition now..."
        )

        # 1. تحويل المتطلبات إلى نص
        state_str = json.dumps(session.task_state.model_dump(), ensure_ascii=False)
        build_prompt = f"قم ببناء وكيل بناءً على المتطلبات والمواصفات التالية:\n{state_str}"
        
        # 2. استدعاء دالة البناء لتوليد الملفات فعلياً
        try:
            agent_res = await create_agent_from_prompt(build_prompt)
            friendly_msg = f"ممتاز! لقد قمت بإنشاء الوكيل «{agent_res.name}» بنجاح وبناء ملفاته."
            save_message(session_id, "assistant", friendly_msg)
            return {
                "status": "building",
                "decision": decision,
                "message": friendly_msg,
                "state": session.task_state.model_dump(),
                "agent": agent_res.model_dump()
            }
        except Exception as build_err:
            err_str = str(build_err)
            # هل المشكلة أدوات مفقودة؟
            if "missing" in err_str.lower() or "missing_capability" in err_str.lower():
                missing_part = err_str.split("Missing:")[-1].strip() if "Missing:" in err_str else err_str
                friendly_msg = (
                    f"عذراً، لا أستطيع إنشاء هذا الوكيل حالياً لأن الأدوات المطلوبة غير متوفرة في النظام.\n\n"
                    f"🔧 الأدوات المفقودة: {missing_part}\n\n"
                    f"يمكنك طلب وكيل يعتمد على الأدوات المتاحة مثل: البحث في الويب، إرسال الإيميل عبر Gmail، إلخ."
                )
            else:
                friendly_msg = (
                    f"حدث خطأ أثناء إنشاء الوكيل. يرجى المحاولة مرة أخرى أو تحديد متطلبات مختلفة.\n\n"
                    f"تفاصيل الخطأ: {err_str[:300]}"
                )
            save_message(session_id, "assistant", friendly_msg)
            return {
                "status": "waiting_for_user",
                "decision": "ASK_USER",
                "message": friendly_msg,
                "questions": [],
                "state": session.task_state.model_dump(),
            }
    elif decision == "CALL_TOOL":
        tool_name = response_data.get("tool_name")
        tool_args = response_data.get("tool_args", {})

        return {
            "status": "executing_tool",
            "decision": decision,
            "tool": tool_name,
            "args": tool_args,
            "state": session.task_state.model_dump()
        }

    return {
        "status": "error",
        "message": "Unknown decision"
    }

    # if not tool_catalog:
    #     tool_catalog = "- No tools are currently registered."

    #     prompt = _COPILOT_SYSTEM_PROMPT.format(
    #         TASK_STATE=session.task_state.model_dump_json(),
    #         AVAILABLE_TOOLS=tool_catalog,
    #     )
    #     user_prompt = f"History:\n{formatted_history}\n\nNew Message: {user_message}"
        
    #     response_data = await chat_completion_json(prompt, user_prompt)
        
    #     updated_state_dict = response_data.get("updated_task_state", {})
    #     decision = response_data.get("decision", "CHAT")
    #     message_to_user = response_data.get("message_to_user", "")
        
    #     session.task_state = TaskState(**updated_state_dict)
    #     session.updated_at = datetime.now().isoformat()
        
    #     if decision in ["ASK_USER", "CHAT"]:
    #         save_message(session_id, "assistant", message_to_user)
    #         return {
    #             "status": "waiting_for_user",
    #             "decision": decision,
    #             "message": message_to_user,
    #             "state": session.task_state.model_dump(),   
    #         }
            
    #     elif decision == "BUILD_AGENT":
    #         save_message(session_id, "assistant", "All requirements gathered. Generating the Agent Definition now...")
    #         # يمكنك هنا استدعاء create_agent_from_prompt لبناء الوكيل فعلياً
    #         return {
    #             "status": "building",
    #             "decision": decision,
    #             "message": "ممتاز! تم جمع كل المتطلبات. جاري بناء الوكيل الآن...",
    #             "state": session.task_state.model_dump()
    #         }
            
    #     elif decision == "CALL_TOOL":
    #         tool_name = response_data.get("tool_name")
    #         tool_args = response_data.get("tool_args", {})
    #         return {
    #             "status": "executing_tool",
    #             "decision": decision,
    #             "tool": tool_name,
    #             "args": tool_args,
    #             "state": session.task_state.model_dump()
    #         }
    #     return {"status": "error", "message": "Unknown decision"}