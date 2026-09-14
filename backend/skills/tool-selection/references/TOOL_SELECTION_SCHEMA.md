---
name: tool-selection
description: >
  Schema defining the tools selected for an AI agent, their supported
  capabilities, necessity, constraints, and unresolved requirements.
license: MIT
compatibility: Used by the tool-selection skill
---

# Tool Selection Schema

This document defines the output contract for the `tool-selection` skill.

The purpose of this schema is to describe which tools an agent needs and how
those tools satisfy the capabilities and tasks defined by the `AgentSpec`.

---

# Schema

```json
{
  "selected_tools": [],
  "capability_mapping": [],
  "unresolved_requirements": []
}
Field Definitions
selected_tools

Type: array[object]

Contains the tools selected for the agent.

Each tool must include:

name
purpose
required
constraints

Example:

{
  "selected_tools": [
    {
      "name": "knowledge_base_search",
      "purpose": "Retrieve approved company information",
      "required": true,
      "constraints": [
        "Only search approved knowledge sources"
      ]
    }
  ]
}

If no tools are required:

{
  "selected_tools": []
}
capability_mapping

Type: array[object]

Maps required agent capabilities to the tools that provide them.

Example:

{
  "capability_mapping": [
    {
      "capability": "knowledge retrieval",
      "tools": [
        "knowledge_base_search"
      ]
    }
  ]
}

A capability that is handled directly by the model does not need a tool.

Example:

{
  "capability_mapping": [
    {
      "capability": "summarization",
      "tools": []
    }
  ]
}
unresolved_requirements

Type: array[string]

Contains tool-related requirements that cannot currently be resolved.

Examples:

{
  "unresolved_requirements": [
    "A CRM lookup tool is required but no CRM tool is available"
  ]
}

If all tool requirements are resolved:

{
  "unresolved_requirements": []
}
Tool Object

Each object in selected_tools must follow:

{
  "name": "string",
  "purpose": "string",
  "required": true,
  "constraints": [
    "string"
  ]
}
name

Type: string

The concrete name of the selected tool.

Do not invent a tool name.

purpose

Type: string

Describes why the agent needs the tool.

The purpose must directly correspond to an agent capability or task.

Example:

{
  "purpose": "Search the company knowledge base for approved product information"
}
required

Type: boolean

Indicates whether the tool is necessary.

Use:

true

when the agent cannot reliably perform an important required task without the
tool.

Use:

false

when the tool is useful but not essential.

constraints

Type: array[string]

Restrictions governing how the tool may be used.

Examples:

{
  "constraints": [
    "Read-only access",
    "Only access approved customer records"
  ]
}

If there are no known constraints:

{
  "constraints": []
}
Capability Mapping Object

Each object in capability_mapping must follow:

{
  "capability": "string",
  "tools": [
    "string"
  ]
}
capability

Type: string

The agent capability being mapped.

Example:

{
  "capability": "knowledge retrieval"
}
tools

Type: array[string]

Names of tools that provide the capability.

Example:

{
  "tools": [
    "knowledge_base_search"
  ]
}

Use an empty array when the capability is handled directly by the model:

{
  "tools": []
}
Validation Rules

The tool-selection result must satisfy:

selected_tools must be an array.
capability_mapping must be an array.
unresolved_requirements must be an array of strings.
Every selected tool must have a name.
Every selected tool must have a purpose.
Every selected tool must have a boolean required value.
Every selected tool must have a constraints array.
Every capability mapping must have a capability.
Every capability mapping must have a tools array.
Do not invent tools.
Do not invent APIs.
Do not add tools simply because they are commonly available.
Preserve explicit tool requirements.
Record unavailable required tools as unresolved requirements.
Do not add fields outside this schema.
Example
{
  "selected_tools": [
    {
      "name": "knowledge_base_search",
      "purpose": "Retrieve approved company information for customer responses",
      "required": true,
      "constraints": [
        "Only search approved knowledge sources"
      ]
    },
    {
      "name": "create_support_ticket",
      "purpose": "Create a support ticket when an issue requires human intervention",
      "required": false,
      "constraints": [
        "Do not create duplicate tickets"
      ]
    }
  ],
  "capability_mapping": [
    {
      "capability": "knowledge retrieval",
      "tools": [
        "knowledge_base_search"
      ]
    },
    {
      "capability": "customer support",
      "tools": []
    },
    {
      "capability": "ticket escalation",
      "tools": [
        "create_support_ticket"
      ]
    }
  ],
  "unresolved_requirements": []
}