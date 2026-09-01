"""FastAPI application – API endpoints for Agent & Workflow creation."""
from __future__ import annotations
from orchestrator import run_copilot_turn


from models import ChatRequest
# from conversational_orchestrator import run_copilot_turn

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import AsyncGenerator

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import AGENTS_DIR, WORKFLOWS_DIR
from llm_client import chat_completion
from models import (
    AgentCreateRequest,
    AgentCreateResponse,
    AgentDefinition,
    AgentEditRequest,
    EdgeDef,
    ExecutorDef,
    ValidationResult,
    WorkflowCreateRequest,
    WorkflowCreateResponse,
    WorkflowDefinition,
    WorkflowEditRequest,
)
from orchestrator import (
    create_agent_from_definition,
    create_agent_from_prompt,
    create_workflow_from_definition,
    create_workflow_from_prompt,
    edit_agent,
    edit_workflow,
)
import json
import Tools.gmail # لتسجيل أدوات جي ميل
import Tools.web_search # لتسجيل أداة البحث الحقيقية
from Tools.clean_registry import CleanToolRegistry
from Tools.oauth import router as oauth_router, USER_TOKENS

# أضف مسارات الـ OAuth للتطبيق
from llm_client import chat_completion, chat_completion_stream, chat_completion_json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent & Workflow Builder",
    description="Natural-language powered Agent & Workflow creation using Microsoft Agent Framework Skills",
    version="0.1.0",
)
app.include_router(oauth_router)
# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================================================
# Health
# ===========================================================================
@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ===========================================================================
# Agent endpoints
# ===========================================================================
@app.post("/api/agents", response_model=AgentCreateResponse)
async def create_agent(req: AgentCreateRequest):
    """Create a new agent from natural language or explicit definition."""
    try:
        if req.prompt:
            return await create_agent_from_prompt(req.prompt)
        elif req.definition:
            return await create_agent_from_definition(req.definition)
        else:
            raise HTTPException(400, "Provide either 'prompt' or 'definition'")
    except Exception as exc:
        logger.exception("Agent creation failed")
        raise HTTPException(500, str(exc))


@app.get("/api/agents")
async def list_agents():
    """List all created agents."""
    agents = []
    if AGENTS_DIR.exists():
        for agent_dir in sorted(AGENTS_DIR.iterdir()):
            yaml_path = agent_dir / "agent.yaml"
            if yaml_path.exists():
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                agents.append({
                    "name": data.get("name", agent_dir.name),
                    "description": data.get("description", ""),
                    "model": data.get("model", ""),
                    "source_workflow": data.get("source_workflow", None),
                })
    return {"agents": agents}


@app.get("/api/agents/{name}")
async def get_agent(name: str):
    """Get a specific agent's full definition and code."""
    agent_dir = AGENTS_DIR / name
    yaml_path = agent_dir / "agent.yaml"
    py_path = agent_dir / "agent.py"

    if not yaml_path.exists():
        raise HTTPException(404, f"Agent '{name}' not found")

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    code = py_path.read_text(encoding="utf-8") if py_path.exists() else ""

    return {
        "name": name,
        "definition": data,
        "code": code,
    }


@app.delete("/api/agents/{name}")
async def delete_agent(name: str):
    """Delete an agent."""
    agent_dir = AGENTS_DIR / name
    if not agent_dir.exists():
        raise HTTPException(404, f"Agent '{name}' not found")
    import shutil
    shutil.rmtree(agent_dir)
    return {"message": f"Agent '{name}' deleted"}


@app.put("/api/agents/{name}/edit", response_model=AgentCreateResponse)
async def edit_agent_endpoint(name: str, req: AgentEditRequest):
    """Edit an existing agent via natural language."""
    try:
        return await edit_agent(name, req.prompt)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        logger.exception("Agent edit failed")
        raise HTTPException(500, str(exc))


# ===========================================================================
# Workflow endpoints
# ===========================================================================
@app.post("/api/workflows", response_model=WorkflowCreateResponse)
async def create_workflow(req: WorkflowCreateRequest):
    """Create a new workflow from natural language or explicit definition."""
    try:
        if req.prompt:
            return await create_workflow_from_prompt(req.prompt)
        elif req.definition:
            return await create_workflow_from_definition(req.definition)
        else:
            raise HTTPException(400, "Provide either 'prompt' or 'definition'")
    except Exception as exc:
        logger.exception("Workflow creation failed")
        raise HTTPException(500, str(exc))


@app.put("/api/workflows/{name}/edit", response_model=WorkflowCreateResponse)
async def edit_workflow_endpoint(name: str, req: WorkflowEditRequest):
    """Edit an existing workflow via natural language."""
    try:
        return await edit_workflow(name, req.prompt)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        logger.exception("Workflow edit failed")
        raise HTTPException(500, str(exc))


@app.get("/api/workflows")
async def list_workflows():
    """List all created workflows."""
    workflows = []
    if WORKFLOWS_DIR.exists():
        for wf_dir in sorted(WORKFLOWS_DIR.iterdir()):
            yaml_path = wf_dir / "workflow.yaml"
            if yaml_path.exists():
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                workflows.append({
                    "name": data.get("name", wf_dir.name),
                    "description": data.get("description", ""),
                    "executors_count": len(data.get("executors", [])),
                    "edges_count": len(data.get("edges", [])),
                })
    return {"workflows": workflows}


@app.get("/api/workflows/{name}")
async def get_workflow(name: str):
    """Get a specific workflow's full definition and code."""
    wf_dir = WORKFLOWS_DIR / name
    yaml_path = wf_dir / "workflow.yaml"
    py_path = wf_dir / "workflow.py"

    if not yaml_path.exists():
        raise HTTPException(404, f"Workflow '{name}' not found")

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    code = py_path.read_text(encoding="utf-8") if py_path.exists() else ""

    return {
        "name": name,
        "definition": data,
        "code": code,
    }

@app.post("/api/copilot")
async def copilot_chat(req: ChatRequest):
    """
    Agentic Copilot Endpoint.
    Manages session state internally and returns the LLM's structured decision.
    """
    try:
        result = await run_copilot_turn(req.session_id, req.message)
        return result
    except Exception as exc:
        logger.exception("Copilot interaction failed")
        raise HTTPException(500, str(exc))
@app.delete("/api/workflows/{name}")
async def delete_workflow(name: str):
    """Delete a workflow."""
    wf_dir = WORKFLOWS_DIR / name
    if not wf_dir.exists():
        raise HTTPException(404, f"Workflow '{name}' not found")
    import shutil
    shutil.rmtree(wf_dir)
    return {"message": f"Workflow '{name}' deleted"}


# ===========================================================================
# Playground – Agent
# ===========================================================================
@app.post("/api/agents/{name}/run")
async def run_agent(name: str, body: dict):
    """Run a created agent in playground mode.

    Uses the agent's instructions as a system prompt and streams the LLM response
    via Server-Sent Events.
    """
    agent_dir = AGENTS_DIR / name
    yaml_path = agent_dir / "agent.yaml"
    if not yaml_path.exists():
        raise HTTPException(404, f"Agent '{name}' not found")

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    instructions = data.get("instructions", "You are a helpful assistant.")
    user_message = body.get("message", "")
    history: list[dict] = body.get("history", [])

    if not user_message:
        raise HTTPException(400, "message is required")

    async def generate() -> AsyncGenerator[str, None]:
        try:
            agent_tool_ids = data.get("tools", [])

            all_tools = CleanToolRegistry.get_all_llm_schemas()

            llm_tools = [
                tool
                for tool in all_tools
                if tool["function"]["name"] in agent_tool_ids
            ]
                        
            messages = [{"role": "system", "content": instructions}]
            if history:
                messages.extend(history[-10:])
            if user_message:
                messages.append({"role": "user", "content": user_message})

            # 1. الاستدعاء الأول باستخدام طريقة التدفق الجديدة
            response_stream = await chat_completion_stream(
                instructions, "", 
                temperature=data.get("temperature", 0.7),
                tools=llm_tools,
                messages_history=messages
            )

            full_content = ""
            tool_calls_dict = {}

            # 2. استهلاك أجزاء الرد قطعة قطعة (Streaming Iteration)
            async for chunk in response_stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                
                # أ- إرسال النصوص إلى المستخدم فور وصولها (حتى يراها وهي تُكتب)
                if delta.content:
                    full_content += delta.content
                    yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"
                
                # ب- تجميع أوامر استدعاء الأدوات (لأنها تدفق ولا تأتي كاملة)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_dict:
                            tool_calls_dict[idx] = {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name or "", "arguments": tc.function.arguments or ""}
                            }
                        else:
                            if tc.function.name:
                                tool_calls_dict[idx]["function"]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_dict[idx]["function"]["arguments"] += tc.function.arguments

            # 3. في حال قرر الذكاء الاصطناعي استخدام أدوات مساعدة
            if tool_calls_dict:
                tool_calls_list = list(tool_calls_dict.values())
                messages.append({
                    "role": "assistant",
                    "content": full_content,
                    "tool_calls": tool_calls_list
                })
                
                for tool_call in tool_calls_list:
                    tool_id = tool_call["function"]["name"]
                    args_str = tool_call["function"]["arguments"]
                    
                    try:
                        args = json.loads(args_str)
                    except:
                        args = {}
                    
                    yield f"data: {json.dumps({'type': 'token', 'content': f'\\n[جاري تشغيل: {tool_id}...]\\n'})}\n\n"
                    
                    tool_record = CleanToolRegistry.get_tool(tool_id)
                    if tool_record:
                        access_token = USER_TOKENS.get("test_user")
                        try:
                            result = await tool_record["executor"](
                                args,
                                context={"access_token": access_token},
                              )
                            # إرسال النتيجة إلى سجل المحادثة
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_id,
                                "content": json.dumps(result)
                            })
                        except Exception as e:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_id,
                                "content": str(e)
                            })
                
                # 4. الاستدعاء الثاني للحصول على النتيجة النهائية بعد تنفيذ الأداة مدعوماً بالتدفق
                second_stream = await chat_completion_stream(
                    instructions, "",
                    messages_history=messages,
                    tools=llm_tools
                )
                
                final_content = ""
                async for final_chunk in second_stream:
                    if not final_chunk.choices:
                        continue
                    final_delta = final_chunk.choices[0].delta
                    if final_delta.content:
                        final_content += final_delta.content
                        
                        yield f"data: {json.dumps({'type': 'token', 'content': final_delta.content})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done', 'content': final_content})}\n\n"
            else:
                # إذا لم تكن هناك أدوات، نُصدر أمر الانتهاء
                yield f"data: {json.dumps({'type': 'done', 'content': full_content})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ===========================================================================
# Condition evaluation helper
# ===========================================================================
async def _evaluate_conditions(
    node_output: str, conditional_edges: list[dict]
) -> set[str]:
    """Use LLM to decide which conditional edges match the node output.

    Returns a set of target executor names whose conditions are satisfied.
    """
    conditions_desc = "\n".join(
        f"- Edge to '{e['target']}': condition = \"{e['condition']}\""
        for e in conditional_edges
    )
    system = (
        "You are a workflow condition evaluator. Given the output of a node "
        "and a list of conditional edges, determine which edge(s) should be "
        "taken.\n\n"
        "Return a JSON object: {\"matched_targets\": [\"target_name\", ...]}\n"
        "Only include targets whose conditions are clearly satisfied by the output.\n"
        "If none match, return {\"matched_targets\": []}.\n"
        "Always return exactly ONE best match unless the output explicitly "
        "satisfies multiple conditions."
    )
    user_msg = (
        f"Node output:\n{node_output[:1000]}\n\n"
        f"Conditional edges:\n{conditions_desc}"
    )
    try:
        from llm_client import chat_completion_json
        result = await chat_completion_json(system, user_msg)
        targets = set(result.get("matched_targets", []))
        logger.info("Condition evaluation: matched %s", targets)
        return targets
    except Exception as exc:
        logger.exception("Condition evaluation failed, taking first edge")
        # Fallback: take first conditional edge
        return {conditional_edges[0]["target"]} if conditional_edges else set()


# ===========================================================================
# Playground – Workflow
# ===========================================================================
@app.post("/api/workflows/{name}/run")
async def run_workflow(name: str, body: dict):
    """Simulate running a workflow and stream step-by-step execution as SSE.

    Each SSE event describes which executor is currently active and its output,
    allowing the frontend to animate edge-by-edge data flow.
    """
    wf_dir = WORKFLOWS_DIR / name
    yaml_path = wf_dir / "workflow.yaml"
    if not yaml_path.exists():
        raise HTTPException(404, f"Workflow '{name}' not found")

    wf_data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    user_input = body.get("message", "Hello")
    executors = wf_data.get("executors", [])
    edges = wf_data.get("edges", [])
    start = wf_data.get("start", "")

    # Build adjacency for traversal
    adj: dict[str, list[dict]] = {}
    for ex in executors:
        adj[ex["name"]] = []
    for edge in edges:
        adj.setdefault(edge["source"], []).append(edge)

    # Pre-compute executor map
    exec_map = {ex["name"]: ex for ex in executors}

    async def simulate() -> AsyncGenerator[str, None]:
        """BFS-style execution through the workflow graph."""
        visited: set[str] = set()
        queue: list[tuple[str, str]] = [(start, user_input)]  # (executor_name, input_data)
        step_id = 0

        # Signal start
        yield f"data: {json.dumps({'type': 'start', 'workflow': name, 'input': user_input})}\n\n"
        await asyncio.sleep(0.3)

        while queue:
            current_name, current_input = queue.pop(0)
            if current_name in visited:
                continue
            visited.add(current_name)

            executor = exec_map.get(current_name)
            if not executor:
                continue

            step_id += 1

            # Signal: entering node
            yield f"data: {json.dumps({'type': 'node_enter', 'step': step_id, 'node': current_name, 'input': current_input[:2000]})}\n\n"
            await asyncio.sleep(0.5)

            # Actually process: use LLM for agent executors, simple transform for function executors
            if executor.get("type") == "agent":
                try:
                    output = await chat_completion(
                        executor.get("instructions", "Process the input."),
                        f"Input data: {current_input}",
                        temperature=0.5,
                    )
                except Exception as exc:
                    output = f"[Error: {exc}]"
            else:
                # Function executor – simulate transformation
                output = f"[{current_name}] processed: {current_input[:100]}"
                await asyncio.sleep(0.3)

            # Signal: node complete
            yield f"data: {json.dumps({'type': 'node_complete', 'step': step_id, 'node': current_name, 'output': output[:5000]})}\n\n"
            await asyncio.sleep(0.3)

            # Traverse outgoing edges — evaluate conditions
            outgoing = adj.get(current_name, [])
            conditional_edges = [e for e in outgoing if e.get("condition")]
            unconditional_edges = [e for e in outgoing if not e.get("condition")]

            if conditional_edges:
                # Use LLM to evaluate which condition(s) match the output
                matched_targets = await _evaluate_conditions(
                    output, conditional_edges
                )
                for edge in conditional_edges:
                    target = edge["target"]
                    if target in matched_targets and target not in visited:
                        yield f"data: {json.dumps({'type': 'edge_active', 'source': current_name, 'target': target, 'condition': edge.get('condition', ''), 'matched': True, 'data_preview': output[:100]})}\n\n"
                        await asyncio.sleep(0.5)
                        queue.append((target, output))
                    elif target not in visited:
                        yield f"data: {json.dumps({'type': 'edge_skipped', 'source': current_name, 'target': target, 'condition': edge.get('condition', ''), 'matched': False})}\n\n"

                # If no conditional edge matched, fall through to unconditional
                if not matched_targets:
                    for edge in unconditional_edges:
                        target = edge["target"]
                        if target not in visited:
                            yield f"data: {json.dumps({'type': 'edge_active', 'source': current_name, 'target': target, 'data_preview': output[:100]})}\n\n"
                            await asyncio.sleep(0.5)
                            queue.append((target, output))
            else:
                # No conditional edges — follow all (fan-out)
                for edge in outgoing:
                    target = edge["target"]
                    if target not in visited:
                        yield f"data: {json.dumps({'type': 'edge_active', 'source': current_name, 'target': target, 'data_preview': output[:100]})}\n\n"
                        await asyncio.sleep(0.5)
                        queue.append((target, output))

        # Signal: workflow complete
        yield f"data: {json.dumps({'type': 'done', 'steps': step_id})}\n\n"

    return StreamingResponse(simulate(), media_type="text/event-stream")
