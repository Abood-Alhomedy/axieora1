# AgentSpec Contract

## Purpose

AgentSpec is the canonical representation of an agent after planning and capability selection.

AgentSpec is the contract between:

Intelligence Layer
and
Generation Layer.

The generator must consume AgentSpec.

The generator must not redesign the agent.

---

# 1. AgentSpec Pipeline

The intended pipeline is:

Natural Language
    ↓
TaskSpec
    ↓
ArchitecturePlan
    ↓
CapabilityPlan
    ↓
AgentSpec
    ↓
Schema Validation
    ↓
Registry Validation
    ↓
Template Selection
    ↓
Generation

---

# 2. Core AgentSpec

A conceptual AgentSpec may contain:

```yaml
name:
purpose:
architecture:

instructions:

skills:
  []

tools:
  []

inputs:
  []

outputs:
  []

workflow:

workers:
  []

routes:
  {}

constraints:

metadata:
```

Only fields required by the selected architecture should be populated.

Do not add fields merely because they are available.

---

# 3. Identity

## name

The agent name must:

* be present
* be unique within the generated project
* use a valid identifier
* not contain unsafe filesystem characters

## purpose

Purpose describes what the agent is responsible for.

It should be concise and operational.

---

# 4. Architecture

architecture must reference a registered architecture.

Examples:

* single-agent
* sequential
* parallel
* router
* supervisor
* orchestrator-workers
* evaluator-optimizer
* handoff

Never accept an architecture that is not registered.

---

# 5. Instructions

Instructions define the agent's behavioral contract.

They should describe:

* objective
* responsibilities
* constraints
* expected behavior
* output requirements

Instructions must not contradict the architecture.

---

# 6. Tools

tools contains references to registered tools.

Example:

```yaml
tools:
  - web_search
  - filesystem
```

Rules:

* every tool must exist in Tool Registry
* tool IDs must be canonical
* unknown tools must fail validation
* duplicate tools should be rejected or normalized

Never invent tools.

---

# 7. Skills

skills contains references to registered skills.

Example:

```yaml
skills:
  - research
  - report-writing
```

Rules:

* every skill must exist in Skill Registry
* skill references must use canonical identifiers
* unknown skills must fail validation

---

# 8. Inputs

Inputs describe information required by the agent.

Each input should define, where supported:

* name
* type
* required
* description
* default

Example:

```yaml
inputs:
  - name: topic
    type: string
    required: true
```

---

# 9. Outputs

Outputs describe what the agent produces.

Where supported define:

* name
* type
* description
* required

Example:

```yaml
outputs:
  - name: report
    type: markdown
    description: Final research report
```

---

# 10. Workflow

Workflow is architecture-dependent.

For sequential:

```yaml
workflow:
  - researcher
  - analyst
  - writer
```

For other architectures, use the structure defined by the architecture contract.

Do not use workflow fields merely because they exist.

---

# 11. Workers

workers are required for architectures such as:

* parallel
* supervisor
* orchestrator-workers

Each worker should have a stable identifier.

Example:

```yaml
workers:
  - id: researcher
    purpose: Research the requested topic
  - id: analyst
    purpose: Analyze research findings
```

Worker references must be internally consistent.

---

# 12. Routes

routes are required for router architectures.

Example:

```yaml
routes:
  research: researcher
  analysis: analyst
  writing: writer
```

Every route target must exist.

---

# 13. Constraints

Constraints describe restrictions that must be respected during generation or runtime.

Examples:

* maximum iterations
* timeout
* output format
* allowed capabilities
* execution limits

Constraints must not contradict system-level policies.

---

# 14. AgentSpec Invariants

A valid AgentSpec must satisfy:

1. architecture exists
2. architecture is registered
3. architecture contract is satisfied
4. required fields exist
5. tools are registered
6. skills are registered
7. references are valid
8. identifiers are unique
9. workflow is structurally valid
10. worker references are valid
11. route references are valid

---

# 15. AgentSpec and Generation

The generator receives a validated AgentSpec.

The generator must not:

* select a different architecture
* invent tools
* invent skills
* create missing workers silently
* change workflow semantics
* reinterpret user requirements

If AgentSpec is invalid:

Generation must stop.

---

# 16. AgentSpec Repair

When validation fails:

AgentSpec
↓
Validation Errors
↓
Repair
↓
Validation
↓
PASS

Repair must preserve the original user intent.

Do not modify unrelated fields.

---

# 17. Serialization

AgentSpec should have a deterministic serialization format.

Equivalent specifications should serialize consistently.

This enables:

* testing
* logging
* caching
* evaluation
* debugging
* reproducibility

---

# 18. Versioning

If AgentSpec evolves:

* maintain backward compatibility where possible
* version breaking schema changes
* migrate existing specifications explicitly
* update validators and tests

Never silently reinterpret old AgentSpecs.

---

# 19. Final Rule

AgentSpec is the source of truth for generation.

If the generated project differs from AgentSpec, generation validation must detect the discrepancy.
