from typing import Callable, Dict, Any, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ToolConfig(BaseModel):
    id: str
    name: str
    description: str
    parameters: Dict[str, Any]

class CleanToolRegistry:
    """
    A modernized Tool Registry for the Agent Factory.
    Centralizes the management of tools available across the system.
    """
    _tools: Dict[str, dict] = {}

    @classmethod
    def register(cls, config: ToolConfig, executor: Callable):
        cls._tools[config.id] = {"config": config, "executor": executor}
        logger.debug(f"Registered tool: {config.id}")

    @classmethod
    def get_tool(cls, tool_id: str):
        return cls._tools.get(tool_id)

    @classmethod
    def list_all_tool_ids(cls) -> List[str]:
        return list(cls._tools.keys())

    @classmethod
    def get_all_llm_schemas(cls) -> List[Dict]:
        schemas = []
        for tool in cls._tools.values():
            config = tool["config"]
            schemas.append({
                "type": "function",
                "function": {
                    "name": config.id,
                    "description": config.description,
                    "parameters": config.parameters
                }
            })
        return schemas

# =======================================================
# Example of how to structure individual tools cleanly:
# =======================================================

async def mock_write_file_executor(args: dict, context: dict = None):
    file_path = args.get("file_path", "unknown.txt")
    content = args.get("content", "")
    return {"success": True, "output": f"Mock: Wrote {len(content)} chars to {file_path}"}

CleanToolRegistry.register(
    ToolConfig(
        id="write-file",
        name="Write File",
        description="Writes content to the local filesystem.",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["file_path", "content"]
        }
    ),
    mock_write_file_executor
)

# (Removed mock_web_search_executor to use the real one in Tools/web_search.py)
