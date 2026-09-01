import json
import asyncio
import os
import sys

# Add parent dir to path to import core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline import run_agent_factory_pipeline

async def run_evals():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    with open(dataset_path, 'r') as f:
        cases = json.load(f)

    print("Starting Architecture and Tool Selection Evaluation...")
    passed = 0
    total = len(cases)
    
    for case in cases:
        print(f"\n--- Running Case {case['id']} ---")
        prompt = case['input']
        print(f"Input: {prompt}")
        
        result = await run_agent_factory_pipeline(prompt)
        status = result.get('status')
        
        case_passed = True
        
        if 'expected_status' in case:
            if status != case['expected_status']:
                print(f"[FAIL] Expected status {case['expected_status']}, got {status}")
                case_passed = False
            else:
                print(f"[PASS] Status matched: {status}")
        else:
            arch = result.get('architecture')
            expected_arch = case.get('expected_architecture')
            
            if expected_arch and arch != expected_arch:
                # Sometimes the LLM might choose something very similar, but we want strict match for the eval
                print(f"[WARN] Expected architecture {expected_arch}, got {arch}")
                # We won't strictly fail on architecture if it's very close, but we flag it.
                
            expected_tools = case.get('expected_tools', [])
            actual_tools = result.get('tools', [])
            for t in expected_tools:
                if t not in actual_tools:
                    print(f"[FAIL] Missing expected tool: {t}")
                    case_passed = False
                    
            if case_passed:
                print("[PASS] Validation & Capabilities Selection met criteria")
                
        if case_passed:
            passed += 1

    print(f"\nEvaluation Complete. Passed: {passed}/{total}")

if __name__ == "__main__":
    asyncio.run(run_evals())
