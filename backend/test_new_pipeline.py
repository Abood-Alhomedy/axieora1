import asyncio
import logging
from pipeline import run_agent_factory_pipeline

# Setup basic logging to see the pipeline progress
logging.basicConfig(level=logging.INFO)

async def test_factory():
    user_request = "I want a specialized agent that searches the web for pricing data and writes it into a CSV file."
    
    print("="*60)
    print(f"🚀 Starting Agent Factory Pipeline Test")
    print(f"🗣 User Request: {user_request}")
    print("="*60)
    
    result = await run_agent_factory_pipeline(user_request)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED")
    print("="*60)
    print(f"Status:       {result.get('status')}")
    print(f"Agent Name:   {result.get('name')}")
    print(f"Architecture: {result.get('architecture')}")
    print(f"Tools Added:  {result.get('tools')}")
    print(f"Skills Added: {result.get('skills')}")
    print("-" * 60)
    print("Validation Result:")
    print(result.get('validation'))
    print("-" * 60)
    print("Generated Code:")
    print(result.get('code'))
    
if __name__ == "__main__":
    asyncio.run(test_factory())
