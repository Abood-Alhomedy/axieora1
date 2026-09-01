# Tool Registry

## Purpose

The Tool Registry is the authoritative source of executable capabilities available to generated agents.

The registry prevents the LLM from inventing tools that do not exist.

---

# 1. Single Source of Truth

Only the Tool Registry defines available tools.

The following components must not maintain independent hardcoded tool lists:

- Task Analyzer
- Architecture Planner
- Capability Selector
- AgentSpec Validator
- Generator
- Evaluator

They must resolve tools through the registry.

---

# 2. Tool Definition

Each registered tool should define, where applicable:

- id
- name
- description
- category
- input schema
- output schema
- implementation reference
- permissions
- runtime requirements
- supported architectures
- status

Example:

```yaml
id: web_search

name: Web Search

description: Search the public web for information.

category: research

input_schema:
  type: object
  properties:
    query:
      type: string
  required:
    - query

permissions:
  - network

status: active
```

---

# 3. Tool IDs

Tool IDs must:

- be unique
- be stable
- be canonical
- be safe to reference from AgentSpec

Do not use display names as identifiers when a stable ID exists.

---

# 4. Tool Selection

Capability selection should:

1. Understand the task.
2. Identify required capabilities.
3. Query the Tool Registry.
4. Select only registered tools.
5. Validate compatibility.
6. Add canonical tool IDs to AgentSpec.

---

# 5. Unknown Tools

If the user requests a capability that does not exist:

Do not invent a tool.

Return a structured missing capability result.

Example:

```json
{
  "status": "missing_capability",
  "missing_tools": [
    "requested_tool"
  ]
}
```

The orchestrator may then:

- ask for clarification
- continue without the capability
- suggest an available alternative
- stop generation

The selector must not silently fabricate an implementation.

---

# 6. Tool Compatibility

A tool may have restrictions such as:

- supported runtime
- supported architecture
- permissions
- required dependencies
- required environment variables

Capability selection must consider these restrictions.

---

# 7. Permissions

Tools requiring privileged operations must declare their permission requirements.

Examples:

- network
- filesystem
- database
- process execution
- external API

The agent must not receive a tool if required permissions cannot be satisfied.

---

# 8. Tool Validation

Validate:

- tool exists
- tool is active
- tool schema is valid
- tool is compatible
- required dependencies exist
- required permissions are available

---

# 9. Tool References

AgentSpec should reference tools by canonical ID.

Example:

```yaml
tools:
  - web_search
  - database_query
```

Never embed arbitrary implementation code inside AgentSpec merely to execute a tool.

---

# 10. Registry Consumers

The same registry must be used by:

Tool Selector
 ↓
AgentSpec Validator
 ↓
Generator
 ↓
Evaluator

This prevents capability drift.

---

# 11. Tool Lifecycle

Tools may have states such as:

- active
- deprecated
- disabled

Deprecated tools should not be selected for new agents unless explicitly allowed.

Disabled tools must fail validation.

---

# 12. Tool Registry Tests

Test:

- registration
- discovery
- duplicate detection
- lookup
- missing tool handling
- schema validation
- permission validation
- architecture compatibility
- disabled tool handling

---

# 13. Important Rule

Never solve a missing-tool problem by hallucinating a tool.

Missing capabilities must remain explicit.
