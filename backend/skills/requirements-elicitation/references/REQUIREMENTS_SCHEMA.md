---
name: requirements-elicitation
description: >
  Schema defining the structured requirements extracted from a natural-language
  request for creating an AI agent.
license: MIT
compatibility: Used by the requirements-elicitation skill
---

# Requirements Schema

This document defines the output contract for the
`requirements-elicitation` skill.

The purpose of this schema is to convert an unstructured user request into
structured requirements that can be consumed by later stages of the
agent-creation pipeline.

---

# Schema

```json
{
  "goal": "string",
  "target_users": [
    "string"
  ],
  "responsibilities": [
    "string"
  ],
  "tasks": [
    "string"
  ],
  "behavior": [
    "string"
  ],
  "constraints": [
    "string"
  ],
  "required_capabilities": [
    "string"
  ],
  "required_tools": [
    "string"
  ],
  "model_requirements": {
    "model": "string"
  },
  "missing_information": [
    "string"
  ]
}
Field Definitions
goal

Type: string

The primary objective of the requested agent.

The goal should describe what the agent exists to accomplish.

Example:

{
  "goal": "Provide customer support and answer product questions"
}
target_users

Type: array[string]

Identifies the people or systems that will interact with the agent.

Example:

{
  "target_users": [
    "customers",
    "support staff"
  ]
}

If the target users are unknown:

{
  "target_users": []
}
responsibilities

Type: array[string]

High-level responsibilities assigned to the agent.

Example:

{
  "responsibilities": [
    "Answer customer questions",
    "Provide product information",
    "Escalate complex issues"
  ]
}
tasks

Type: array[string]

Concrete operations the agent should perform.

Example:

{
  "tasks": [
    "Search the knowledge base",
    "Answer customer questions",
    "Summarize support requests"
  ]
}
behavior

Type: array[string]

Behavioral characteristics or interaction rules.

Example:

{
  "behavior": [
    "Be professional",
    "Be concise",
    "Ask clarifying questions when necessary"
  ]
}

Behavior should not contain capabilities or implementation details.

constraints

Type: array[string]

Restrictions or rules that the agent must follow.

Example:

{
  "constraints": [
    "Do not invent product information",
    "Only use approved knowledge sources"
  ]
}

If no constraints are known:

{
  "constraints": []
}
required_capabilities

Type: array[string]

Capabilities required for the agent to accomplish its goal.

Examples:

{
  "required_capabilities": [
    "Natural language understanding",
    "Knowledge retrieval",
    "Customer support"
  ]
}

Capabilities describe what the agent needs to be able to do, not the
specific implementation used to do it.

required_tools

Type: array[string]

Tools explicitly requested by the user or clearly required to accomplish the
agent's tasks.

Example:

{
  "required_tools": [
    "knowledge_base_search"
  ]
}

Do not invent tool names.

If no tools are required:

{
  "required_tools": []
}
model_requirements

Type: object

Contains model requirements explicitly provided by the user.

Example:

{
  "model_requirements": {
    "model": "gpt-4o"
  }
}

If no model was specified:

{
  "model_requirements": {}
}

Never invent a model deployment name.

missing_information

Type: array[string]

Information that is necessary to reliably create the agent but was not
provided by the user.

Example:

{
  "missing_information": [
    "Model deployment name",
    "Knowledge base source"
  ]
}

If all required information is available:

{
  "missing_information": []
}
Validation Rules

The requirements object must satisfy the following rules:

goal must be a string.
target_users must be an array of strings.
responsibilities must be an array of strings.
tasks must be an array of strings.
behavior must be an array of strings.
constraints must be an array of strings.
required_capabilities must be an array of strings.
required_tools must be an array of strings.
model_requirements must be an object.
missing_information must be an array of strings.
Do not add fields that are not defined by this schema.
Do not invent information that was not provided or reasonably inferred.
Missing optional information should use an empty array or empty object
rather than fabricated values.
Example
{
  "goal": "Provide customer support",
  "target_users": [
    "customers"
  ],
  "responsibilities": [
    "Answer customer questions",
    "Help resolve common issues"
  ],
  "tasks": [
    "Search the knowledge base",
    "Answer questions",
    "Escalate unresolved issues"
  ],
  "behavior": [
    "Be professional",
    "Be concise",
    "Do not claim certainty when information is unavailable"
  ],
  "constraints": [
    "Do not invent information"
  ],
  "required_capabilities": [
    "Customer support",
    "Knowledge retrieval"
  ],
  "required_tools": [
    "knowledge_base_search"
  ],
  "model_requirements": {},
  "missing_information": []
}