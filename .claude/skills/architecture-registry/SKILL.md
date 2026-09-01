---

name: architecture-registry
description: Design and maintain the Architecture Registry and architecture contracts of an Agent Factory. Use when adding, modifying, validating, or resolving agent architectures and their required fields, runtime behavior, templates, and validation rules.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Architecture Registry

## Purpose

The Architecture Registry is the authoritative definition of supported agent architectures.

It prevents architecture-specific logic from being scattered across the codebase.

## Architecture Definition

Each architecture definition should describe:

* id
* name
* description
* required fields
* optional fields
* workflow requirements
* runtime behavior
* validation rules
* template
* supported capabilities

## Supported Architectures

Initially support:

* single-agent
* sequential
* parallel
* router
* supervisor
* orchestrator-workers
* evaluator-optimizer
* handoff

Only register an architecture when its implementation actually exists.

## Resolution

Use:

architecture id
→ ArchitectureRegistry
→ ArchitectureDefinition
→ TemplateResolver
→ Generator

## No Scattered Conditionals

Avoid architecture-specific conditionals distributed across:

* planner
* validator
* generator
* evaluator
* templates

Centralize architecture knowledge in the registry.

## Architecture Contract

The contract must define what a valid AgentSpec looks like for that architecture.

Example:

orchestrator-workers:

Required:

* workers

Optional:

* shared_tools
* max_iterations

Generation:

* orchestrator_workers template

## Adding an Architecture

Before adding a new architecture verify:

1. Planning support
2. AgentSpec support
3. Registry definition
4. Validation rules
5. Template
6. Generation
7. Generated-code validation
8. Evaluation tests

Do not register an architecture that cannot be generated and validated.

## Principle

"Supported" means end-to-end implemented, not merely recognized by the planner.
