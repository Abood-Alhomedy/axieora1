# Agent Factory Test Cases

## Purpose

Provide representative test cases for validating planning, AgentSpec generation, capability selection, generation, validation, and evaluation.

---

# 1. Single Agent

## Test

Create an agent that summarizes documents provided by the user.

## Expected Architecture

single-agent

## Expected Capabilities

Only capabilities actually available in the registry.

## Expected Result

One generated agent.

---

# 2. Sequential

## Test

Create an agent that:

1. researches a topic
2. analyzes the research
3. writes a final report

## Expected Architecture

sequential

## Expected Workflow

researcher → analyst → writer

## Validation

Verify all stages exist and preserve order.

---

# 3. Parallel

## Test

Create an agent that analyzes a product using:

- price analysis
- feature analysis
- competitor analysis

The analyses are independent.

## Expected Architecture

parallel

## Expected Workers

- price_analyzer
- feature_analyzer
- competitor_analyzer

---

# 4. Router

## Test

Create an agent that routes incoming requests to:

- researcher
- analyst
- writer

based on request type.

## Expected Architecture

router

## Expected Routes

- research → researcher
- analysis → analyst
- writing → writer

---

# 5. Supervisor

## Test

Create a supervisor that coordinates:

- researcher
- analyst
- writer

The supervisor decides which specialist should act.

## Expected Architecture

supervisor

---

# 6. Orchestrator Workers

## Test

Create an agent that researches competitors, analyzes prices and features, and writes a final report.

## Expected Architecture

orchestrator-workers

## Expected Workers

- researcher
- price_analyzer
- feature_analyzer
- writer

## Validation

Verify:

- workers exist
- orchestrator exists
- worker references are valid
- generated files exist
- generated Python compiles

---

# 7. Evaluator Optimizer

## Test

Create an agent that generates a report and iteratively improves it using an evaluator.

## Expected Architecture

evaluator-optimizer

## Expected Components

- generator
- evaluator

## Validation

Verify:

generator → evaluator → improvement

is represented correctly.

---

# 8. Handoff

## Test

Create an agent that transfers a technical request from a general assistant to a specialist.

## Expected Architecture

handoff

## Validation

Verify:

- receiving agent exists
- handoff rule exists
- target is valid
- termination is possible

---

# 9. Unknown Tool

## Test

Request an agent requiring a tool that does not exist.

## Expected Result

missing_capability

The system must not invent the tool.

---

# 10. Unknown Skill

## Test

Request a skill that does not exist.

## Expected Result

missing_capability

The system must not invent the skill.

---

# 11. Invalid Architecture

## Test

Request an architecture not registered in Architecture Registry.

## Expected Result

ArchitectureError

No generation should occur.

---

# 12. Missing Worker

## Test

AgentSpec references:

```yaml
workers:
  - researcher
  - analyst
  - writer
```

Generated project contains:

```text
researcher.py
analyst.py
```

but not `writer.py`.

## Expected Result

FAIL

Error: `MISSING_WORKER`

---

# 13. Invalid Route

## Test

Router contains:

```yaml
routes:
  research: researcher
  analysis: unknown_agent
```

## Expected Result

FAIL

Error: `INVALID_ROUTE_TARGET`

---

# 14. Invalid Sequential Workflow

## Test

Sequential AgentSpec contains an empty workflow.

## Expected Result

FAIL

Error: `MISSING_WORKFLOW`

---

# 15. Duplicate Worker

## Test

workers contains:

```yaml
- researcher
- researcher
```

## Expected Result

FAIL

Error: `DUPLICATE_WORKER_ID`

---

# 16. Invalid Tool Reference

## Test

AgentSpec references:

```yaml
tools:
  - nonexistent_tool
```

## Expected Result

FAIL

Error: `UNKNOWN_TOOL`

---

# 17. Invalid Skill Reference

## Test

AgentSpec references:

```yaml
skills:
  - nonexistent_skill
```

## Expected Result

FAIL

Error: `UNKNOWN_SKILL`

---

# 18. Generated Syntax Failure

## Test

A template produces invalid Python.

## Expected Result

Generated Code Validation fails.

The system should enter Code Repair or regenerate the affected artifact.

---

# 19. AgentSpec Repair

## Test

Create an AgentSpec with:

```yaml
architecture: orchestrator-workers
workers: []
```

## Expected Result

AgentSpec validation fails.

Repair should add or reconstruct workers only when supported by the available task information.

---

# 20. End-to-End Test

## Input

Create an agent that researches competitors, analyzes their pricing and features, and produces a final report.

## Expected Flow

```text
Natural Language
→ TaskSpec
→ ArchitecturePlan
→ CapabilityPlan
→ AgentSpec
→ Validation
→ Template Selection
→ Jinja2
→ Generated Agent
→ Generated Code Validation
→ Evaluation
```

## Success Criteria

- correct architecture
- valid AgentSpec
- valid capabilities
- correct generated structure
- valid Python
- tests pass
- final output satisfies the task

---

# 21. Regression Test

Every implementation change must execute the existing test suite.

The number of passing existing tests must not decrease.

---

# 22. Test Classification

Tests should be classified as:

- unit
- schema
- registry
- architecture
- generation
- integration
- end-to-end
- regression
- negative
- repair

---

# 23. Test Principle

A test should verify behavior, not merely file existence.

Weak:

"agent.py exists."

Strong:

"agent.py exists, compiles, imports successfully, contains the expected architecture behavior, and references only registered capabilities."
