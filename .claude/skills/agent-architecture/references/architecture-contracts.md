# Architecture Contracts

## Purpose

This document defines the structural contracts for every supported Agent Factory architecture.

Architecture patterns explain when an architecture should be used.

Architecture contracts define what a valid implementation of that architecture must contain.

The Architecture Contract is authoritative for:

- AgentSpec validation
- architecture validation
- template resolution
- generation
- generated-project validation
- architecture-specific evaluation

---

# 1. General Contract Rules

Every architecture definition must specify:

- architecture id
- required fields
- optional fields
- forbidden fields
- workflow structure
- runtime behavior
- template
- validation rules

An architecture is not considered supported merely because the planner can select its name.

It is supported only when:

Planning
+
AgentSpec
+
Validation
+
Generation
+
Generated Code Validation
+
Evaluation

all work successfully.

---

# 2. Single Agent

## ID

single-agent

## Required Fields

- name
- purpose
- instructions
- architecture

## Optional Fields

- tools
- skills
- inputs
- outputs
- constraints
- memory
- metadata

## Forbidden Fields

The following are normally not required:

- workers
- routes
- supervisor
- orchestrator
- handoff_targets

## Workflow

A single execution path:

User Input
    ↓
Agent
    ↓
Output

## Runtime Behavior

One agent is responsible for the complete task.

No delegation is required.

## Template

single_agent/agent.py.j2

## Validation

Validate:

- architecture == single-agent
- required fields exist
- tools are registered
- skills are registered
- no invalid worker configuration exists

---

# 3. Sequential

## ID

sequential

## Required Fields

- name
- architecture
- workflow

## Workflow Requirements

workflow must:

- exist
- contain at least one step
- preserve execution order
- reference valid agents or stages

Example:

workflow:
  - researcher
  - analyst
  - writer

## Optional Fields

- shared_tools
- shared_skills
- inputs
- outputs
- constraints
- max_retries

## Forbidden Fields

Do not require:

- routes
- parallel_workers

unless explicitly supported by the runtime.

## Runtime Behavior

Execution must follow the defined order.

Step N may depend on the output of Step N-1.

## Template

sequential/agent.py.j2

## Validation

Verify:

- workflow exists
- workflow is ordered
- referenced components exist
- identifiers are unique
- required dependencies are available

---

# 4. Parallel

## ID

parallel

## Required Fields

- name
- architecture
- workers

## Worker Requirements

workers must:

- exist
- contain at least one worker
- have unique identifiers
- be independently executable

Example:

workers:
  - researcher
  - price_analyzer
  - feature_analyzer

## Optional Fields

- shared_tools
- shared_skills
- aggregation_strategy
- timeout
- concurrency_limit

## Forbidden Fields

Do not require sequential workflow semantics.

## Runtime Behavior

Independent workers may execute concurrently.

Their outputs are collected and optionally aggregated.

## Template

parallel/agent.py.j2

## Validation

Verify:

- workers exist
- worker IDs are unique
- worker dependencies do not create invalid sequential requirements
- tools are registered
- skills are registered

---

# 5. Router

## ID

router

## Required Fields

- name
- architecture
- routes

## Route Requirements

routes must map:

condition/category → target agent

Example:

routes:
  research: researcher
  analysis: analyst
  writing: writer

## Optional Fields

- fallback
- classifier
- shared_tools
- shared_skills
- routing_instructions

## Runtime Behavior

The router determines the appropriate target.

The request is then delegated to the selected target.

## Template

router/agent.py.j2

## Validation

Verify:

- routes exist
- route identifiers are unique
- every route target exists
- fallback target exists when configured

---

# 6. Supervisor

## ID

supervisor

## Required Fields

- name
- architecture
- workers

## Optional Fields

- shared_tools
- shared_skills
- delegation_policy
- max_iterations
- termination_condition

## Runtime Behavior

A supervisor coordinates specialized workers.

The supervisor may:

- inspect the task
- select a worker
- delegate work
- inspect results
- delegate additional work
- terminate the workflow

## Template

supervisor/agent.py.j2

## Validation

Verify:

- workers exist
- worker identifiers are unique
- delegation configuration is valid
- tools and skills are registered

---

# 7. Orchestrator Workers

## ID

orchestrator-workers

## Required Fields

- name
- architecture
- workers

## Optional Fields

- shared_tools
- shared_skills
- max_iterations
- aggregation_strategy
- termination_condition

## Worker Requirements

Every worker must define:

- id
- purpose
- instructions

Optional:

- tools
- skills
- inputs
- outputs

## Runtime Behavior

The orchestrator:

1. receives the task
2. decomposes the task
3. selects workers
4. delegates subtasks
5. collects results
6. combines results
7. produces the final result

## Template

orchestrator_workers/agent.py.j2

Worker template:

orchestrator_workers/worker.py.j2

## Validation

Verify:

- workers exist
- worker IDs are unique
- workers have valid specifications
- referenced tools exist
- referenced skills exist
- aggregation strategy is valid

---

# 8. Evaluator Optimizer

## ID

evaluator-optimizer

## Required Fields

- name
- architecture
- generator
- evaluator

## Optional Fields

- max_iterations
- acceptance_threshold
- stopping_condition
- shared_tools
- shared_skills

## Runtime Behavior

The system follows:

Input
 ↓
Generator
 ↓
Output
 ↓
Evaluator
 ↓
Pass → Final Output
 ↓
Fail
 ↓
Improvement
 ↓
Generator

## Template

evaluator_optimizer/agent.py.j2

## Validation

Verify:

- generator exists
- evaluator exists
- iteration configuration is valid
- termination condition exists or has a safe default

---

# 9. Handoff

## ID

handoff

## Required Fields

- name
- architecture
- agents

## Optional Fields

- handoff_rules
- fallback
- shared_tools
- shared_skills
- termination_condition

## Runtime Behavior

One agent transfers responsibility to another agent.

The receiving agent becomes responsible for continuing or completing the task.

## Template

handoff/agent.py.j2

## Validation

Verify:

- target agents exist
- handoff rules reference valid agents
- circular handoff is prevented unless explicitly supported
- termination is possible

---

# 10. Contract Enforcement

Architecture contracts must be enforced before generation.

Flow:

ArchitecturePlan
    ↓
AgentSpec
    ↓
Architecture Contract
    ↓
Validation
    ↓
Template Resolver
    ↓
Generation

Do not allow the generator to compensate for invalid architecture data.

---

# 11. Contract Evolution

When adding a new architecture:

1. Define the architecture ID.
2. Define required fields.
3. Define optional fields.
4. Define forbidden fields.
5. Define workflow semantics.
6. Define runtime behavior.
7. Define template.
8. Define validation rules.
9. Add generation tests.
10. Add evaluation tests.

Do not mark an architecture as supported before all required stages work.

---

# 12. Important Rule

Architecture contracts are authoritative.

If another component contradicts this document or the registered architecture definition, the implementation must be reviewed rather than silently accepting inconsistent behavior.