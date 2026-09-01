---

name: agent-evaluation
description: Evaluate Agent Factory planning, capability selection, AgentSpec validity, generation quality, architecture behavior, and end-to-end agent creation. Use when creating eval datasets, test matrices, regression tests, or measuring whether an architecture is truly supported.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Agent Evaluation

## Core Principle

A successful demo is not sufficient evidence that the Agent Factory works.

Evaluate across multiple representative tasks.

## Evaluation Dimensions

Measure:

* task understanding
* architecture selection
* tool selection
* skill selection
* AgentSpec validity
* generation correctness
* generated code validity
* requirements coverage
* end-to-end behavior

## Architecture Matrix

Test at minimum:

* single-agent
* sequential
* parallel
* router
* supervisor
* orchestrator-workers
* evaluator-optimizer
* handoff

Each architecture must pass:

Planning
+
AgentSpec
+
Generation
+
Validation

## Capability Tests

Verify that the system:

* selects existing tools
* avoids unnecessary tools
* never invents tools
* identifies missing capabilities
* selects appropriate skills

## Negative Tests

Include requests containing:

* nonexistent tools
* unsupported architecture
* invalid workflow
* duplicate workers
* invalid routes
* missing required fields

## Regression Testing

Existing tests must continue to pass.

New functionality must not reduce previous coverage.

## End-to-End Test

Example:

User:
"Create an agent that researches competitors, analyzes prices and features, and writes a report."

Expected pipeline:

Natural Language
→ TaskSpec
→ ArchitecturePlan
→ CapabilityPlan
→ AgentSpec
→ Validation
→ Generation
→ Code Validation
→ Evaluation

## Metrics

Track at minimum:

* architecture accuracy
* tool accuracy
* skill accuracy
* schema validity
* generation success
* end-to-end success
* repair success

## Completion Rule

Do not declare an architecture supported merely because planning succeeds.

It is supported only when:

Planning
+
AgentSpec
+
Generation
+
Validation

all succeed.
