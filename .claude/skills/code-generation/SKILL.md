---

name: code-generation
description: Generate agent projects from validated AgentSpec using architecture-specific templates. Use when implementing or modifying the Agent Factory generator, Jinja2 templates, generated project structure, or runtime-specific agent files.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Code Generation

## Core Principle

AgentSpec is the source of truth.

Generation must be deterministic relative to:

* AgentSpec
* architecture definition
* selected tools
* selected skills
* selected template
* runtime configuration

## Generation Pipeline

Use:

AgentSpec
→ Architecture Resolver
→ Template Resolver
→ Jinja2
→ Generated Files

## Jinja2 Rule

Templates are presentation and code-generation artifacts.

Do not put complex architectural intelligence inside templates.

Do not allow templates to independently choose architectures.

Do not use templates to compensate for invalid AgentSpec.

## Template Structure

Prefer:

templates/
├── single_agent/
├── sequential/
├── parallel/
├── router/
├── supervisor/
├── orchestrator_workers/
├── evaluator_optimizer/
└── handoff/

Each architecture may contain:

* agent.py.j2
* config.yaml.j2
* instructions.md.j2
* README.md.j2
* worker.py.j2 when required

## Template Resolution

Resolve the template using the Architecture Registry.

Do not scatter architecture conditionals across the codebase.

Prefer:

ArchitectureRegistry
→ ArchitectureDefinition
→ TemplateResolver
→ Jinja2 Template

## Generated Project Contract

A generated project should have a predictable structure.

Example:

agent/
├── agent.py
├── config.yaml
├── instructions.md
├── requirements.txt
├── README.md
└── tests/

Architecture-specific files may be added when required.

## Generation Validation

After generation verify:

* required files exist
* Python syntax is valid
* imports are valid
* YAML is valid
* AgentSpec references are preserved
* tools are valid
* skills are valid
* architecture structure is correct
* workers exist when required
* routes exist when required

## Important

File creation does not equal successful generation.

Generation succeeds only after generated artifacts pass validation.
