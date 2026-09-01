---

name: validation-repair
description: Validate AgentSpec, generated agent projects, architecture contracts, tools, skills, schemas, and generated code, then repair the correct layer when validation fails. Use when debugging pipeline failures, invalid agent specifications, generation errors, or repair loops.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Validation and Repair

## Core Principle

Always repair the layer where the defect originates.

Do not repair generated code when the real problem is AgentSpec.

Do not repair AgentSpec when the real problem is a template implementation bug.

## Validation Layers

### Layer 1 — Task Validation

Verify that the task was understood.

### Layer 2 — AgentSpec Validation

Verify:

* architecture
* required fields
* tools
* skills
* workers
* routes
* workflow
* constraints

### Layer 3 — Generation Validation

Verify:

* required files
* syntax
* imports
* YAML
* references
* architecture structure

### Layer 4 — Runtime/Evaluation Validation

Verify:

* functional behavior
* requirements coverage
* tool correctness
* output quality
* architecture behavior

## Design Repair

When AgentSpec fails:

AgentSpec
→ Validation
→ Errors
→ Repair AgentSpec
→ Validation

Only after PASS should generation continue.

## Code Repair

When generated code fails:

Generated Code
→ Code Validation
→ Errors
→ Repair/Regenerate
→ Code Validation

## Repair Rules

Every repair must:

1. Preserve the original user intent.
2. Change the minimum necessary artifact.
3. Avoid introducing unsupported tools.
4. Avoid inventing architectures.
5. Revalidate after repair.
6. Respect the maximum repair attempts.

## Error Classification

Prefer explicit errors:

* LLMError
* ValidationError
* RegistryError
* ArchitectureError
* GenerationError
* EvaluationError

Never reduce a meaningful failure to vague output such as:

architecture = None

## Logging

For each stage capture:

* stage
* input metadata
* output metadata
* status
* error
* duration

Never log:

* API keys
* secrets
* credentials
* private tokens

## Success

A repair is successful only when the repaired artifact passes the appropriate validation layer.
