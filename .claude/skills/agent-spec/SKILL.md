---

name: agent-spec
description: Design, validate, and maintain the canonical AgentSpec representation for an Agent Factory. Use when converting TaskSpec and architecture decisions into a structured agent definition, modifying agent contracts, validating agent structure, or preparing an agent for generation.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# AgentSpec

## Purpose

AgentSpec is the canonical contract between the intelligence layer and the generation layer.

The generator must consume AgentSpec.

The generator must not independently redesign the agent.

## Required Conceptual Fields

AgentSpec should represent, when applicable:

* name
* purpose
* architecture
* instructions
* skills
* tools
* inputs
* outputs
* workflow
* workers
* routes
* constraints

Do not add fields merely because they exist in an example.

Only include fields required by the selected architecture or runtime.

## Pipeline

The intended flow is:

Natural Language
→ TaskSpec
→ ArchitecturePlan
→ CapabilityPlan
→ AgentSpec
→ Validation
→ Template Selection
→ Generation

## AgentSpec Rules

AgentSpec must:

1. Be deterministic enough to validate.
2. Reference only registered tools.
3. Reference only registered skills.
4. Use a supported architecture.
5. Match the architecture contract.
6. Contain enough information for generation.
7. Avoid hidden architecture decisions.
8. Avoid implementation-specific assumptions unless required by the runtime.

## Architecture Consistency

Examples:

single-agent:

* no workers required

sequential:

* ordered workflow required

parallel:

* independent workers required

router:

* routes required

orchestrator-workers:

* workers required

## Validation

Before generation verify:

* architecture exists
* required fields exist
* referenced tools exist
* referenced skills exist
* worker references are valid
* route references are valid
* workflow references are valid
* duplicate identifiers are rejected
* invalid combinations are rejected

## Repair

If AgentSpec validation fails:

1. Preserve the original task intent.
2. Identify the exact validation errors.
3. Repair AgentSpec.
4. Validate again.
5. Stop after the configured repair limit.

Do not jump directly to generated code repair when the actual problem is in AgentSpec.

## Generator Contract

The generator receives:

* validated AgentSpec
* architecture definition
* selected template
* selected skills
* selected tools

The generator does not make new architectural decisions.
