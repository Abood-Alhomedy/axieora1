---
name: agent-specification
description: >
  Schema defining the implementation-ready specification of an AI agent
  produced from structured requirements.
license: MIT
compatibility: Used by the agent-specification skill
---

# Agent Specification Schema

This document defines the output contract for the
`agent-specification` skill.

The purpose of this schema is to transform extracted requirements into a
complete, implementation-ready specification that can be consumed by later
stages such as tool selection and instruction generation.

---

# Schema

```json
{
  "name": "string",
  "description": "string",
  "purpose": "string",
  "target_users": [],
  "responsibilities": [],
  "tasks": [],
  "behavioral_rules": [],
  "constraints": [],
  "capabilities": [],
  "tool_requirements": [],
  "knowledge_requirements": [],
  "input_requirements": [],
  "output_requirements": [],
  "escalation_requirements": [],
  "model_requirements": {},
  "unresolved_decisions": []
}
Field Definitions
name

Type: string

The proposed name of the agent.

The name should:

describe the agent's purpose
use snake_case
be concise
be suitable for the final Agent Definition

Example:

{
  "name": "customer_support_agent"
}

Do not use spaces or arbitrary identifiers.

description

Type: string

A concise description of what the agent does.

Example:

{
  "description": "Provides customer support using approved company knowledge"
}

The description should focus on the agent's purpose rather than its internal
implementation.

purpose

Type: string

A precise statement describing the primary purpose of the agent.

Example:

{
  "purpose": "Help customers resolve product and service questions"
}
target_users

Type: array[string]

The users or systems that interact with the agent.

Example:

{
  "target_users": [
    "customers",
    "support staff"
  ]
}

If unknown:

{
  "target_users": []
}
responsibilities

Type: array[string]

High-level responsibilities owned by the agent.

Example:

{
  "responsibilities": [
    "Answer customer questions",
    "Provide product information",
    "Escalate unresolved issues"
  ]
}
tasks

Type: array[string]

Concrete tasks that the agent must perform.

Example:

{
  "tasks": [
    "Search the knowledge base",
    "Analyze the customer's question",
    "Generate an appropriate response"
  ]
}
behavioral_rules

Type: array[string]

Rules describing how the agent should behave.

Example:

{
  "behavioral_rules": [
    "Be professional",
    "Be concise",
    "Ask for clarification when necessary",
    "Do not fabricate information"
  ]
}

These rules will later contribute to the generated system instructions.

constraints

Type: array[string]

Restrictions that the agent must follow.

Example:

{
  "constraints": [
    "Only use approved knowledge sources",
    "Do not disclose internal information"
  ]
}

Constraints should represent actual requirements rather than generic
assumptions.

capabilities

Type: array[string]

Capabilities required to accomplish the agent's purpose.

Examples:

{
  "capabilities": [
    "Natural language understanding",
    "Knowledge retrieval",
    "Question answering",
    "Summarization"
  ]
}

Capabilities describe what the agent can do.

They should not contain specific implementation details.

tool_requirements

Type: array[object]

Tools required by the agent.

Each tool requirement should describe:

tool name, when known
purpose
capability supported
whether it is required

Example:

{
  "tool_requirements": [
    {
      "name": "knowledge_base_search",
      "purpose": "Search approved company knowledge",
      "supports": "knowledge retrieval",
      "required": true
    }
  ]
}

If no tools are required:

{
  "tool_requirements": []
}

Do not invent concrete tools when the requirements only describe a capability.

knowledge_requirements

Type: array[object]

External knowledge or data sources required by the agent.

Example:

{
  "knowledge_requirements": [
    {
      "name": "company_knowledge_base",
      "purpose": "Provide approved product and service information"
    }
  ]
}

If no external knowledge is required:

{
  "knowledge_requirements": []
}
input_requirements

Type: array[object]

Information expected from users or upstream systems.

Example:

{
  "input_requirements": [
    {
      "name": "customer_question",
      "description": "The question or issue submitted by the customer",
      "required": true
    }
  ]
}
output_requirements

Type: array[object]

Information or results the agent should produce.

Example:

{
  "output_requirements": [
    {
      "name": "customer_response",
      "description": "A clear answer to the customer's question"
    }
  ]
}

Do not create a strict output schema unless the user requires one.

escalation_requirements

Type: array[string]

Conditions under which the agent should transfer work to a human or another
system.

Example:

{
  "escalation_requirements": [
    "Escalate issues that cannot be resolved using approved knowledge",
    "Escalate requests requiring human authorization"
  ]
}

If escalation is not required:

{
  "escalation_requirements": []
}
model_requirements

Type: object

Model-related requirements explicitly provided by the user or requirements
stage.

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

Never invent a deployment name.

unresolved_decisions

Type: array[string]

Important implementation decisions that remain unresolved.

Example:

{
  "unresolved_decisions": [
    "Exact model deployment has not been specified",
    "Knowledge base implementation has not been selected"
  ]
}

Only include decisions that materially affect the agent design.

Validation Rules

The AgentSpec must satisfy the following rules:

name must be a string.
description must be a string.
purpose must be a string.
target_users must be an array.
responsibilities must be an array.
tasks must be an array.
behavioral_rules must be an array.
constraints must be an array.
capabilities must be an array.
tool_requirements must be an array of objects.
knowledge_requirements must be an array of objects.
input_requirements must be an array of objects.
output_requirements must be an array of objects.
escalation_requirements must be an array.
model_requirements must be an object.
unresolved_decisions must be an array.
Do not add fields outside this schema.
Do not invent model deployment names.
Do not invent tools or external systems.
Preserve unresolved requirements instead of guessing.
Example
{
  "name": "customer_support_agent",
  "description": "Provides customer support using approved company knowledge",
  "purpose": "Help customers resolve product and service questions",
  "target_users": [
    "customers"
  ],
  "responsibilities": [
    "Answer customer questions",
    "Provide product information",
    "Escalate unresolved issues"
  ],
  "tasks": [
    "Search the knowledge base",
    "Analyze customer questions",
    "Generate accurate responses"
  ],
  "behavioral_rules": [
    "Be professional",
    "Be concise",
    "Ask for clarification when necessary",
    "Do not fabricate information"
  ],
  "constraints": [
    "Only use approved knowledge sources"
  ],
  "capabilities": [
    "Natural language understanding",
    "Knowledge retrieval",
    "Question answering"
  ],
  "tool_requirements": [
    {
      "name": "knowledge_base_search",
      "purpose": "Search approved company knowledge",
      "supports": "knowledge retrieval",
      "required": true
    }
  ],
  "knowledge_requirements": [
    {
      "name": "company_knowledge_base",
      "purpose": "Provide approved product information"
    }
  ],
  "input_requirements": [
    {
      "name": "customer_question",
      "description": "The customer's question or issue",
      "required": true
    }
  ],
  "output_requirements": [
    {
      "name": "customer_response",
      "description": "A clear and accurate response"
    }
  ],
  "escalation_requirements": [
    "Escalate unresolved issues to human support"
  ],
  "model_requirements": {},
  "unresolved_decisions": []
}