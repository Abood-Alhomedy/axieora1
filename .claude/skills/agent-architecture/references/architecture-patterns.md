# Architecture Patterns

## Purpose

This document defines when to use each supported architecture and when NOT to use it.

---

## 1. single-agent

### When to Use
- The task is self-contained and focused
- One LLM with the right tools can complete it
- No meaningful delegation or specialization is needed
- The workflow is a single pass

### When NOT to Use
- The task has clearly distinct subtasks that benefit from specialization
- The task requires independent parallel execution
- The output quality requires iterative critique

### Inputs
- User request
- Available tools
- Instructions

### Outputs
- Task result

### Typical Workflow

User → Agent → Result


### Failure Modes
- Overloading the agent with too many responsibilities
- Giving it tools it does not need

### Examples
- "Summarize this document"
- "Answer this question using web search"
- "Write a SQL query for this schema"

---

## 2. sequential

### When to Use
- The task has stages with a fixed order
- Each stage depends on the output of the previous one
- The workflow is deterministic

### When NOT to Use
- Stages are independent (use parallel instead)
- The orchestration is dynamic (use orchestrator-workers instead)

### Inputs
- User request
- Ordered workflow definition

### Outputs
- Final result after all stages complete

### Typical Workflow

Stage 1 → Stage 2 → Stage 3 → Result


### Failure Modes
- Missing stage outputs that block downstream stages
- Stages that are not truly dependent being forced into order

### Examples
- "Research a topic, analyze the findings, then write a report"
- "Read data, transform it, then visualize it"

---

## 3. parallel

### When to Use
- Subtasks are independent of each other
- Subtasks can execute concurrently
- Results are aggregated at the end

### When NOT to Use
- Subtasks depend on each other's outputs
- Only one agent is needed

### Inputs
- Task decomposed into independent subtasks
- Worker definitions

### Outputs
- Aggregated results from all workers

### Typical Workflow

┌── Worker A ──┐
Task ────┼── Worker B ──┼── Aggregator → Result └── Worker C ──┘


### Failure Modes
- Workers that are not truly independent causing ordering issues
- Aggregation logic that does not handle partial failures

### Examples
- "Analyze price, features, and reviews independently"
- "Search three different sources simultaneously"

---

## 4. router

### When to Use
- Requests belong to clearly distinct categories
- A classifier can determine the correct specialist
- Each category has a dedicated handler

### When NOT to Use
- All requests need the same handling
- Categories are ambiguous or overlapping

### Inputs
- User request
- Route definitions mapping categories to agents

### Outputs
- Result from the selected route

### Typical Workflow

Request → Classifier → Route → Specialist → Result


### Failure Modes
- Misclassification sending requests to the wrong route
- Missing fallback when no route matches

### Examples
- "Route coding questions to a coder, writing questions to a writer"
- "Dispatch technical vs. business requests differently"

---

## 5. supervisor

### When to Use
- Multiple specialized workers exist
- A coordinator must decide which worker acts next
- Delegation is dynamic based on context

### When NOT to Use
- Workers are independent (use parallel instead)
- The workflow is predictable (use sequential instead)

### Inputs
- Task
- Worker pool

### Outputs
- Coordinated result from one or more workers

### Typical Workflow


Supervisor → Selects Worker → Worker Acts → Supervisor Reviews → Done or Continue


### Failure Modes
- Supervisor loops indefinitely without reaching termination
- Workers that overlap in responsibility causing confusion

### Examples
- "Coordinate a research team with a supervisor managing researcher, analyst, and writer"

---

## 6. orchestrator-workers

### When to Use
- The task can be decomposed dynamically
- Workers perform specialized subtasks
- A central orchestrator coordinates and aggregates

### When NOT to Use
- The task is simple enough for a single agent
- The workflow is fixed and ordered (use sequential instead)

### Inputs
- User request
- Worker definitions with specialized roles

### Outputs
- Synthesized result from all workers

### Typical Workflow

Orchestrator ├── delegates to Worker A ├── delegates to Worker B └── aggregates → Result


### Failure Modes
- Workers not registered in AgentSpec but expected by orchestrator
- Orchestrator reinventing architecture decisions at runtime

### Examples
- "Research competitors, analyze prices and features, then write a report"

---

## 7. evaluator-optimizer

### When to Use
- Output quality requires iterative improvement
- An evaluator can identify weaknesses in output
- The system can regenerate based on critique

### When NOT to Use
- The output quality can be verified deterministically
- Iteration does not improve results meaningfully

### Inputs
- Initial generator
- Evaluator criteria
- Max iterations

### Outputs
- Optimized result after evaluation loop

### Typical Workflow

Generator → Output → Evaluator → Pass → Done → Fail → Improvement → Generator


### Failure Modes
- Infinite loops without a max_iterations guard
- Evaluator criteria that are too vague to produce actionable feedback

### Examples
- "Generate a report and refine it until it meets quality criteria"
- "Write code, test it, and fix until tests pass"

---

## 8. handoff

### When to Use
- Responsibility must transfer completely to a specialist
- The receiving agent takes full ownership
- The original agent is done after the handoff

### When NOT to Use
- Shared coordination is needed (use supervisor instead)
- The task should be completed by one agent (use single-agent)

### Inputs
- User request
- Handoff target definition
- Handoff rules

### Outputs
- Result from the receiving agent

### Typical Workflow

Agent A → Handoff Decision → Agent B → Result


### Failure Modes
- Circular handoff without a termination condition
- Target agent not found in the registry

### Examples
- "Transfer a technical request from a general assistant to a coding specialist"