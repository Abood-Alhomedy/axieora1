from typing import Dict, Any
from .clean_registry import ToolConfig, CleanToolRegistry
from duckduckgo_search import DDGS
import logging
import asyncio

logger = logging.getLogger(__name__)

web_search_config = ToolConfig(
    id="web-search",
    name="Web Search",
    description="Searches the web for up-to-date information.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query to look up"}
        },
        "required": ["query"]
    }
)

async def execute_web_search(args: dict, context: dict = None) -> dict:
    query = args.get("query")
    if not query:
        return {"success": False, "error": "Query parameter is required"}
    
    logger.info(f"Executing real web search for: {query}")
    try:
        # Run synchronous DDGS in a thread to avoid blocking the event loop
        def do_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=5))
                
        results = await asyncio.to_thread(do_search)
            
        if not results:
            return {"success": True, "output": "No results found for the query."}
            
        formatted_results = "\n\n".join(
            [f"Title: {r.get('title', '')}\nLink: {r.get('href', '')}\nSnippet: {r.get('body', '')}" for r in results]
        )
        return {"success": True, "output": f"Search Results for '{query}':\n\n{formatted_results}"}
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {"success": False, "error": f"Search failed: {str(e)}"}

# Register the tool
CleanToolRegistry.register(web_search_config, execute_web_search)
