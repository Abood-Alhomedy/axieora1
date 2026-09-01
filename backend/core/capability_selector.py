from pydantic import BaseModel
from typing import List
from models import TaskSpec, ArchitecturePlan, AgentSpec
from llm_client import chat_completion_json
import logging

logger = logging.getLogger(__name__)

CAPABILITY_PROMPT = """
You are a Capability Selector for an AI Agent Factory.
The user's request may be written in any language (Arabic, English, etc.).
Your job is to analyze the required capabilities and map them to the EXACT IDs available in the registry.

CRITICAL RULES:
1. You MUST select ONLY from the IDs in the 'Available Skills' and 'Available Tools' lists provided.
2. The registry IDs are in English. Map the user's intent (regardless of language) to the closest matching registry ID.
3. Do NOT invent new tool or skill names. Do NOT return Arabic or non-English names as tools or skills.
4. Only add to "missing_capabilities" if the registry truly has NOTHING that can serve the required function AND it is not an inherent LLM capability.
5. A tool or skill does NOT need to be an exact name match — use semantic similarity to find the best fit from the registry.
6. NEVER add to "missing_capabilities" any capability that an LLM can perform by itself without external tools. These include:
   - Text analysis, text classification, summarization, reasoning, translation
   - Writing responses, generating text, composing messages
   - Decision making, planning, decomposing tasks
   - Any cognitive task that does not require external API access or file system access
7. "missing_capabilities" should ONLY contain things like: a specific API integration, a database connection, or a hardware interface that truly does not exist in the registry.

Examples of correct mapping:
- "البحث في الإنترنت" or "search the web" → map to "web-search" if available
- "إرسال إيميل" or "send email" → map to "gmail_send" if available
- "تحليل النصوص" or "text analysis" → NOT missing, LLM handles this natively — leave out of missing_capabilities
- "توليد ردود" or "generate replies" → NOT missing, LLM handles this natively — leave out of missing_capabilities
- "الوصول لخدمة إيميل" → check registry for gmail_* tools before marking missing

Your response MUST be a valid JSON object:
{
  "skills": ["exact skill IDs from the Available Skills list"],
  "tools": ["exact tool IDs from the Available Tools list"],
  "missing_capabilities": ["ONLY external integrations with truly NO registry match, NEVER cognitive/LLM tasks"]
}
"""

async def select_capabilities(
    task: TaskSpec, 
    plan: ArchitecturePlan, 
    available_skills: List[str], 
    available_tools: List[str]
) -> dict:
    logger.info("Selecting required capabilities based on strict registry...")
    user_context = (
        f"Task Goal: {task.goal}\n"
        f"Needed Capabilities: {', '.join(task.required_capabilities)}\n"
        f"Available Skills in Registry: {', '.join(available_skills)}\n"
        f"Available Tools in Registry: {', '.join(available_tools)}\n"
    )
    
    data = await chat_completion_json(
        system_prompt=CAPABILITY_PROMPT,
        user_message=user_context,
        temperature=0.1
    )
    return data

def build_agent_spec(name: str, task: TaskSpec, plan: ArchitecturePlan, capabilities: dict) -> AgentSpec:
    return AgentSpec(
        name=name,
        purpose=task.goal,
        architecture=plan.architecture_type,
        instructions="", 
        skills=capabilities.get("skills", []),
        tools=capabilities.get("tools", []),
        inputs=task.inputs,
        outputs=task.outputs
    )