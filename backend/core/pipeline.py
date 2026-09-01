from models import TaskSpec, ArchitecturePlan, AgentSpec, ValidationResult
from core.task_analyzer import analyze_task
from core.architecture_planner import plan_architecture
from core.capability_selector import select_capabilities, build_agent_spec
from core.generator import generate_agent_prompt, generate_agent_files
from core.evaluator import evaluate_agent
from core.spec_validator import validate_agent_spec
from Tools.clean_registry import CleanToolRegistry
from core.skill_registry import CleanSkillRegistry
import logging
import re

logger = logging.getLogger(__name__)

async def run_agent_factory_pipeline(user_request: str) -> dict:
    # Single Source of Truth — load from registries dynamically
    available_tools = CleanToolRegistry.list_all_tool_ids()
    CleanSkillRegistry.load_all_metadata()
    available_skills = CleanSkillRegistry.list_all_skill_ids()
    # Fallback: if no skills found via filesystem, use defaults
    if not available_skills:
        available_skills = ["data-analysis", "report-writing", "code-review", "agent-creator"]
    
    try:
        # Step 1: Task Analysis 
        task_spec: TaskSpec = await analyze_task(user_request)
        
        # Step 2: Architecture Planning 
        arch_plan: ArchitecturePlan = await plan_architecture(task_spec)
        
        # Step 3: Capability Selection
        cap_results = await select_capabilities(task_spec, arch_plan, available_skills, available_tools)
        
        if cap_results.get("missing_capabilities"):
            return {
                "status": "missing_capability",
                "missing": cap_results["missing_capabilities"],
                "message": "Cannot proceed because required tools or skills are missing from the registry."
            }
        
        agent_name = "auto_" + re.sub(r'[^a-z0-9_]', '', task_spec.goal.lower().replace(" ", "_")[:20])
        
        # استبدل السطر القديم بهذين السطرين هنا:
        agent_spec: AgentSpec = build_agent_spec(agent_name, task_spec, arch_plan, cap_results)
        agent_spec.workers = arch_plan.workers
        
        # Step 4: Early Structural Validation (Pre-Generation)
        early_val = validate_agent_spec(agent_spec, available_skills, available_tools)
        if not early_val.valid:
            return {
                "status": "error",
                "message": f"Pre-generation structural validation failed: {early_val.errors}"
            }
        
        # Step 5: Generation
        prompts = await generate_agent_prompt(agent_spec)
        agent_spec.instructions = prompts["instructions"]
        agent_spec.instructions = prompts.get("instructions", {})
        
        agent_dir = await generate_agent_files(agent_spec)
        
        # Step 6: Post-Generation Evaluation
        eval_result = evaluate_agent(agent_spec, agent_dir)
        
        if not eval_result.valid:
            logger.warning("Validation failed. Attempting repair (Max 1 attempt)...")
            agent_spec.instructions += f"\n\n[REPAIR NOTE: Please handle these issues: {', '.join(eval_result.errors)}]"
            agent_dir = await generate_agent_files(agent_spec)
            eval_result = evaluate_agent(agent_spec, agent_dir)
            
        with open(f"{agent_dir}/agent.py", "r", encoding="utf-8") as f:
            final_code = f.read()

        return {
            "status": "success" if eval_result.valid else "failed_evaluation",
            "name": agent_spec.name,
            "description": agent_spec.purpose,
            "instructions": agent_spec.instructions,
            "architecture": arch_plan.architecture_type,
            "tools": agent_spec.tools,
            "skills": agent_spec.skills,
            "code": final_code,
            "validation": eval_result.model_dump()
        }
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return {"status": "error", "message": str(e)}