---

name: prompt-engineering
description: Design, review, and improve prompts and context construction for an Agent Factory using Claude or other LLMs. Use when creating stage-specific prompts, reducing monolithic prompts, improving context selection, or designing reliable structured-output instructions.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Prompt Engineering

## Core Principle

Do not create one giant prompt containing the entire Agent Factory architecture.

Use composable instructions.

## Stage Separation

Prefer separate instructions for:

* task analysis
* architecture selection
* capability selection
* agent design
* generation
* evaluation
* repair

## Context Construction

Each stage should receive only the context required for that stage.

Prefer:

System Instructions
+
Stage Instructions
+
Task Context
+
Relevant Knowledge
+
Relevant Examples
+
Policies
+
Schema
+
User Request

Do not automatically include:

* all skills
* all tools
* all architectures
* all examples
* all documentation

## Structured Output

When a stage produces machine-consumed data:

1. Define the expected schema.
2. Instruct the model to produce the schema.
3. Validate the result.
4. Do not trust malformed output.

## Grounding

The model must distinguish between:

* known registry data
* retrieved project information
* user requirements
* model inference

Never present an inferred tool or architecture as an available capability.

## Prompt Responsibilities

Each prompt should have one clear responsibility.

Bad:

"Analyze the task, select architecture, choose tools, design the agent, generate code, test it, and repair it."

Better:

Task Analyzer:
→ TaskSpec

Architecture Planner:
→ ArchitecturePlan

Capability Selector:
→ CapabilityPlan

Agent Designer:
→ AgentSpec

Generator:
→ generated files

Evaluator:
→ evaluation result

Repair:
→ corrected artifact

## Model Behavior

Prefer instructions that define:

* objective
* available information
* constraints
* allowed decisions
* prohibited behavior
* expected output
* failure behavior

Avoid vague instructions such as:

"Use your best judgment."

when deterministic constraints are available.

## Claude-Specific Skill Principle

Keep the main SKILL.md concise enough to act as an operational guide.

Move large reference material into references/.

Load detailed references only when needed.

## Success Condition

The model should make fewer architectural assumptions because the system provides the correct context at each stage.
