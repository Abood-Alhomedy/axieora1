# Jinja2 Generation Guide

## Purpose

Define how Jinja2 templates are used to generate agent projects from validated AgentSpec.

Jinja2 is a rendering mechanism.

It is not an intelligence layer.

---

# 1. Generation Pipeline

Use:

AgentSpec
    ↓
Architecture Resolver
    ↓
Template Resolver
    ↓
Jinja2
    ↓
Generated Files

---

# 2. Source of Truth

The template receives validated data.

Primary source:

AgentSpec

Supporting sources:

- Architecture Definition
- Tool metadata
- Skill metadata
- Runtime configuration

---

# 3. Templates Must Not Make Architecture Decisions

Avoid:

```jinja2
{% if architecture == "router" %}
...
{% elif architecture == "parallel" %}
...
{% endif %}
```

when this condition determines the architecture.

Architecture resolution must happen before template rendering.

Prefer:

```text
Architecture
    ↓
Architecture Registry
    ↓
Template Resolver
    ↓
Selected Template
```

---

# 4. Template Responsibilities

Templates may:

- render fields
- render lists
- render configuration
- render imports
- render instructions
- generate files
- conditionally render optional fields

Templates should not:

- select architecture
- select tools
- select skills
- redesign workflows
- infer missing workers
- invent configuration

---

# 5. Template Organization

Recommended:

```text
templates/
├── single_agent/
│   ├── agent.py.j2
│   ├── config.yaml.j2
│   └── README.md.j2
│
├── sequential/
│   ├── agent.py.j2
│   └── config.yaml.j2
│
├── parallel/
│   ├── agent.py.j2
│   └── config.yaml.j2
│
├── router/
│   ├── agent.py.j2
│   └── config.yaml.j2
│
├── supervisor/
│   └── agent.py.j2
│
├── orchestrator_workers/
│   ├── agent.py.j2
│   ├── worker.py.j2
│   └── config.yaml.j2
│
├── evaluator_optimizer/
│   └── agent.py.j2
│
└── handoff/
    └── agent.py.j2
```

---

# 6. Template Inputs

Templates should receive a well-defined context.

Example:

```python
context = {
    "agent": agent_spec,
    "architecture": architecture_definition,
    "tools": selected_tools,
    "skills": selected_skills
}
```

Avoid passing arbitrary project state.

---

# 7. Determinism

Given the same:

- AgentSpec
- architecture definition
- template version
- capability metadata

generation should produce equivalent output.

Avoid nondeterministic generation logic inside templates.

---

# 8. Escaping and Safety

Generated values must be safely escaped for the target format.

Examples:

- Python
- YAML
- Markdown
- JSON

Do not assume a string is safe merely because it came from AgentSpec.

---

# 9. Template Versioning

Templates should be versioned when breaking changes occur.

A generated project should be traceable to:

- AgentSpec version
- template version
- architecture version

---

# 10. Missing Data

If a required field is missing:

Do not silently invent it.

Generation should fail with a clear validation or generation error.

---

# 11. Testing

Every template should have:

- rendering test
- syntax test
- required-file test
- representative AgentSpec fixture

---

# 12. Principle

Python determines WHAT should be generated.

Jinja2 determines HOW the selected structure is rendered.
