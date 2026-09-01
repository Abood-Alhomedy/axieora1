# Context Engineering

## Purpose

Define how context is selected, assembled, prioritized, and removed during Agent Factory execution.

The goal is to provide the model with the minimum sufficient context required for reliable reasoning.

---

# 1. Core Principle

More context does not automatically produce better reasoning.

Context must be:

- relevant
- authoritative
- current
- scoped
- structured
- minimal enough to remain useful

---

# 2. Context Layers

Use the following conceptual layers:

## Layer 1 — System Instructions

Global behavioral rules.

## Layer 2 — Stage Instructions

Instructions specific to the current pipeline stage.

## Layer 3 — User Task

The original user request.

## Layer 4 — Structured State

Examples:

- TaskSpec
- ArchitecturePlan
- CapabilityPlan
- AgentSpec

## Layer 5 — Registry Context

Only relevant:

- tools
- skills
- architectures

## Layer 6 — Reference Knowledge

Only relevant reference files.

## Layer 7 — Examples

Only examples relevant to the current decision.

## Layer 8 — Validation Feedback

Only when repairing or re-evaluating.

---

# 3. Context by Stage

## Task Analyzer

Load:

- user request
- global task-analysis rules
- relevant constraints

Do not load:

- all tools
- all templates
- generated code

---

## Architecture Planner

Load:

- TaskSpec
- Architecture Registry
- architecture patterns
- relevant architecture constraints

Do not load:

- every tool implementation
- generated code
- unrelated skills

---

## Capability Selector

Load:

- TaskSpec
- ArchitecturePlan
- Tool Registry
- Skill Registry

Only load full skill content when necessary.

---

## Agent Designer

Load:

- TaskSpec
- ArchitecturePlan
- CapabilityPlan
- AgentSpec schema
- architecture contract

---

## Generator

Load:

- validated AgentSpec
- Architecture Definition
- selected template
- selected capability metadata
- required runtime information

Do not load unrelated architecture definitions.

---

## Evaluator

Load:

- original task
- AgentSpec
- generated project
- test results
- evaluation criteria

---

## Repair

Load:

- original task
- failing artifact
- exact error
- relevant contract
- relevant reference

Do not automatically reload the entire project.

---

# 4. Authority Order

When information conflicts, prefer:

1. system policy
2. runtime constraints
3. authoritative registry
4. validated schema
5. AgentSpec
6. stage instructions
7. retrieved reference material
8. examples
9. model inference

Do not override authoritative registry information with assumptions.

---

# 5. Progressive Disclosure

Use:

Metadata
    ↓
Relevant Resource
    ↓
Detailed Reference
    ↓
Specific Section

Avoid loading complete documentation when only one section is required.

---

# 6. Context Isolation

Each pipeline stage should have a scoped context.

Do not allow context from one stage to automatically become authoritative for another stage.

Example:

ArchitecturePlanner output is a proposal until validated.

AgentSpec becomes authoritative only after validation.

---

# 7. State Passing

Prefer structured state over repeated natural-language summaries.

Example:

TaskSpec
→ ArchitecturePlan
→ CapabilityPlan
→ AgentSpec

Do not repeatedly ask the model to reinterpret the original user request when structured state already contains the validated interpretation.

---

# 8. Context Compression

When context becomes large:

1. preserve structured state
2. preserve constraints
3. preserve authoritative references
4. remove redundant explanations
5. remove irrelevant examples
6. remove duplicated source material

Never compress away:

- requirements
- constraints
- errors
- schema information
- capability identifiers

---

# 9. Repair Context

A repair request should contain:

- original requirement
- failing artifact
- exact failure
- relevant contract
- previous repair attempts when relevant

Avoid sending the entire pipeline unless required.

---

# 10. Context Security

Never expose to the model unnecessary:

- API keys
- secrets
- credentials
- private tokens

Never include secrets in logs or evaluation prompts.

---

# 11. Context Relevance Rule

Before adding a resource ask:

"Can this resource change the decision being made at this stage?"

If not, do not load it.

---

# 12. Final Principle

The orchestrator decides what context the model needs.

The model should not receive the entire Agent Factory by default.
