---

name: capability-management
description: Select, validate, and manage registered tools and skills for an Agent Factory. Use when choosing capabilities for an agent, working with Tool Registry or Skill Registry, preventing hallucinated tools, loading skills progressively, or validating capability references.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Capability Management

## Core Distinction

A Tool defines:

WHAT THE AGENT CAN EXECUTE.

A Skill defines:

HOW THE AGENT SHOULD PERFORM A CAPABILITY.

Never treat them as interchangeable.

## Tool Registry

The Tool Registry is the authoritative source for available tools.

Never invent tools.

Never assume a tool exists because its name sounds plausible.

Before assigning a tool:

1. Query the Tool Registry.
2. Confirm the tool exists.
3. Confirm the tool is compatible with the task.
4. Reference its canonical identifier.

If a requested tool does not exist:

Return a missing capability result.

Do not silently substitute a fabricated tool.

## Missing Capability

Use a structured result such as:

{
"status": "missing_capability",
"missing_tools": ["requested-tool"]
}

The orchestrator decides what happens next.

## Skill Registry

Skills must be discoverable from the filesystem or the project's authoritative registry.

Prefer metadata discovery before loading full skill content.

## Progressive Disclosure

Use:

Skill Registry
→ Skill Metadata
→ Relevant Skills
→ SKILL.md
→ Additional References Only When Needed

Do not load every skill into every request.

## Capability Selection

Capability selection should consider:

* task requirements
* architecture requirements
* input/output requirements
* available tools
* available skills
* runtime constraints

## Single Source of Truth

Do not maintain separate hardcoded lists of tools or skills across:

* selector
* validator
* generator
* evaluator

All must resolve capabilities from the authoritative registry.

## Validation

Reject:

* unknown tools
* unknown skills
* duplicate capabilities
* incompatible capabilities
* unavailable architecture-specific capabilities

## Principle

The LLM may select from known capabilities.

The LLM must not create capabilities that do not exist.
