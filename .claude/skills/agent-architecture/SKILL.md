---

name: agent-architecture
description: Select and design the appropriate agent architecture for an Agent Factory request. Use when deciding between single-agent, sequential, parallel, router, supervisor, orchestrator-workers, evaluator-optimizer, or handoff patterns, or when defining architecture contracts for AgentSpec.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Agent Architecture

## Purpose

Convert the task requirements into an explicit agent architecture.

Architecture selection must be based on the task, not arbitrary model preference.

## Supported Architectures

Support:

* single-agent
* sequential
* parallel
* router
* supervisor
* orchestrator-workers
* evaluator-optimizer
* handoff

## Selection Principles

Use single-agent when:

* the task is simple
* one agent can complete it
* no meaningful delegation is required

Use sequential when:

* stages have a fixed order
* the output of one stage becomes input to another
* the workflow is deterministic

Use parallel when:

* subtasks are independent
* results can be produced concurrently
* no strong ordering dependency exists

Use router when:

* incoming requests belong to distinct categories
* one route should be selected
* specialized agents handle different categories

Use supervisor when:

* specialized agents exist
* a supervisor coordinates them
* delegation depends on task context

Use orchestrator-workers when:

* the task can be decomposed dynamically
* workers perform specialized subtasks
* a central orchestrator coordinates the workers

Use evaluator-optimizer when:

* an output requires iterative critique
* evaluation can identify weaknesses
* the system can regenerate or improve the output

Use handoff when:

* responsibility should be transferred to another specialist
* the receiving agent should take ownership of the task

## Architecture Decision

Never select an architecture solely from keywords.

Consider:

* task complexity
* dependency structure
* parallelism
* specialization
* routing requirements
* delegation requirements
* iteration requirements
* expected output
* available tools
* available skills

## Architecture Contract

Every architecture must define:

* required fields
* optional fields
* workflow structure
* runtime behavior
* supported capabilities
* generation template
* validation rules

## Important Rule

Architecture selection happens before generation.

The generator must not redesign the architecture.

The architecture selected in AgentSpec is authoritative.

## Output

Produce a structured ArchitecturePlan.

It must contain:

* architecture type
* reason
* required components
* required capabilities
* workflow requirements
* constraints

If no supported architecture fits the request, report the problem instead of inventing a new architecture.
