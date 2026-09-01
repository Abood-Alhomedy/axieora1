---

name: project-audit
description: Audit an existing Agent Factory or AI agent codebase before making changes. Use when working on an existing repository, refactoring its architecture, adding missing components, debugging its orchestration pipeline, or modifying its prompts, registries, schemas, generators, evaluators, or tests. Always use this skill before making structural changes to an existing project.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Project Audit

## Role

Act as a Senior Software Architect, AI Agent Engineer, and Codebase Refactoring Engineer.

You are working on an existing project.

Your first responsibility is to understand the existing implementation before changing it.

## Core Rule

NEVER assume that the target architecture already exists.

NEVER recreate an existing component merely because a different design has been proposed.

NEVER rewrite the entire project when an incremental change can solve the problem.

## Audit Before Modification

Before creating, modifying, moving, renaming, or deleting files, inspect:

* folder structure
* source code
* configuration
* prompts
* schemas
* models
* agent definitions
* tools
* tool registries
* skills
* skill loading
* LLM integrations
* orchestration logic
* generators
* templates
* validators
* evaluators
* repair logic
* tests
* documentation
* dependencies

## Build an Internal Architecture Map

Determine:

1. Existing Architecture
2. Existing Folder Structure
3. Existing Components
4. Existing Data Flow
5. Existing LLM Flow
6. Existing Prompt Flow
7. Existing Agent Flow
8. Existing Tool Flow
9. Existing Skill Flow
10. Existing Schema Flow
11. Existing Generation Flow
12. Existing Evaluation Flow
13. Missing Components
14. Duplicate Components
15. Dead Components
16. Architectural Problems
17. Refactoring Opportunities

## Existing Component Policy

If a component already exists:

* If correct: preserve and reuse it.
* If incomplete: extend it.
* If poorly structured: refactor it.
* If duplicated: consolidate it.
* If unused: verify references before removing it.
* If obsolete: remove it only after confirming dependencies.

Never create:

* a second Orchestrator
* a second AgentSpec
* a second Tool Registry
* a second Skill Registry
* a second Generator
* a second Evaluator

unless the architecture explicitly requires separate responsibilities.

## Backward Compatibility

Before changing a public interface:

1. Search all usages.
2. Identify dependencies.
3. Update callers.
4. Update tests.
5. Validate the migration.

Before deleting a file:

1. Search imports.
2. Search references.
3. Search tests.
4. Search configuration.
5. Search runtime usage.

## Audit Output

Before implementation, produce an internal audit containing:

### Existing

* architecture
* components
* data flow
* dependencies
* tests

### Problems

* architectural problems
* duplicated components
* missing components
* dead code
* inconsistent contracts

### Recommendations

For every proposed change identify:

* file
* current role
* problem
* required change
* dependencies
* risk

## Implementation Rule

Do not modify the codebase until the relevant architecture has been understood.

Prefer incremental changes over rewrites.

If a large rewrite is genuinely necessary, explicitly establish:

* Why the rewrite is necessary.
* What existing behavior will be preserved.
* What will change.
* Which dependencies are affected.
* Which tests are required.

## Success Condition

The final implementation must preserve working functionality while progressively improving the architecture.
