---

name: implementation-workflow
description: Execute structured changes in an existing Agent Factory repository from audit through implementation, testing, evaluation, and documentation. Use when Claude is asked to implement, refactor, upgrade, or complete a project feature while preserving existing functionality.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Implementation Workflow

## Required Workflow

Follow this sequence unless the project audit proves another sequence is safer.

### Phase A — Audit

Understand:

* current architecture
* current components
* dependencies
* data flow
* LLM flow
* prompt flow
* registries
* AgentSpec
* generator
* evaluator
* tests

Do not modify files during the initial audit.

### Phase B — Plan

For every change define:

* file
* current role
* problem
* required change
* dependencies
* risk
* validation strategy

### Phase C — Implementation

Implement incrementally.

Preferred priorities:

1. architecture
2. component integration
3. schemas
4. orchestration
5. context management
6. prompt management
7. validation
8. generation
9. evaluation
10. repair
11. tests
12. documentation

Change the order when the actual dependency graph requires it.

## Existing Code

Preserve working components.

Do not rewrite the project merely to match a preferred architecture.

## Before Deletion

Search:

* imports
* references
* tests
* configuration
* runtime usage

Only then remove obsolete components.

## After Each Major Change

Run the relevant tests.

Do not wait until the end to discover that an earlier change broke the system.

## Final Verification

Run:

* existing tests
* new registry tests
* architecture tests
* AgentSpec tests
* generation tests
* syntax tests
* end-to-end tests

Existing test performance must not regress.

## Final Report

Report:

* what worked
* what was wrong
* what changed
* files modified
* files added
* files removed
* final architecture
* data flow
* registry architecture
* AgentSpec architecture
* validation flow
* evaluation results
* remaining risks
