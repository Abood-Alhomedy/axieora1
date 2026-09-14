---
name: instruction-generator
description: >
  Schema defining the generated system instructions for an AI agent,
  including identity, responsibilities, behavior, tool usage, constraints,
  uncertainty handling, escalation, and output behavior.
license: MIT
compatibility: Used by the instruction-generator skill
---

# Instructions Schema

This document defines the output contract for the
`instruction-generator` skill.

The purpose of this schema is to represent the generated system instructions
before they are inserted into the final Agent Definition.

---

# Schema

```json
{
  "identity": {
    "role": "string",
    "purpose": "string"
  },
  "responsibilities": [
    "string"
  ],
  "task_instructions": [
    "string"
  ],
  "behavioral_rules": [
    "string"
  ],
  "constraints": [
    "string"
  ],
  "tool_usage": [
    {
      "tool": "string",
      "when_to_use": "string",
      "purpose": "string",
      "restrictions": [
        "string"
      ]
    }
  ],
  "tool_selection_rules": [
    "string"
  ],
  "uncertainty_handling": [
    "string"
  ],
  "escalation_behavior": [
    "string"
  ],
  "input_handling": [
    "string"
  ],
  "output_behavior": [
    "string"
  ]
}
Field Definitions
identity

Type: object

Defines who the agent is and what its primary purpose is.

Structure:

{
  "role": "string",
  "purpose": "string"
}
role

The role the agent performs.

Example:

{
  "role": "Customer support assistant"
}
purpose

The primary objective of the agent.

Example:

{
  "purpose": "Help customers resolve product and service questions"
}
responsibilities

Type: array[string]

High-level responsibilities of the agent.

Example:

{
  "responsibilities": [
    "Answer customer questions",
    "Provide product information",
    "Escalate unresolved issues"
  ]
}
task_instructions

Type: array[string]

Instructions describing how the agent should perform its tasks.

Example:

{
  "task_instructions": [
    "Analyze the customer's question before responding",
    "Search the knowledge base when company-specific information is required",
    "Provide the most relevant information available"
  ]
}

Task instructions should be operational and directly connected to the
specified tasks.

behavioral_rules

Type: array[string]

Rules describing the expected behavior of the agent.

Example:

{
  "behavioral_rules": [
    "Be professional",
    "Be concise",
    "Ask clarifying questions when necessary"
  ]
}
constraints

Type: array[string]

Rules and restrictions that the agent must never violate.

Example:

{
  "constraints": [
    "Do not fabricate information",
    "Only use approved knowledge sources"
  ]
}

Constraints should preserve the requirements from the AgentSpec.

tool_usage

Type: array[object]

Defines how selected tools should be used.

Each object must contain:

{
  "tool": "string",
  "when_to_use": "string",
  "purpose": "string",
  "restrictions": [
    "string"
  ]
}
tool

The concrete tool name.

Example:

{
  "tool": "knowledge_base_search"
}

The tool must exist in the tool-selection result.

when_to_use

Describes the conditions under which the agent should call the tool.

Example:

{
  "when_to_use": "Use when company-specific information is required and is not available in the conversation"
}
purpose

Describes what the tool accomplishes.

Example:

{
  "purpose": "Retrieve approved company information"
}
restrictions

Type: array[string]

Tool-specific restrictions.

Example:

{
  "restrictions": [
    "Only search approved knowledge sources",
    "Do not use the tool unnecessarily"
  ]
}

If there are no specific restrictions:

{
  "restrictions": []
}
tool_selection_rules

Type: array[string]

General rules governing tool selection and invocation.

Example:

{
  "tool_selection_rules": [
    "Use a tool only when it is necessary for the task",
    "Use the most relevant available tool",
    "Respect all tool-specific restrictions"
  ]
}
uncertainty_handling

Type: array[string]

Instructions for handling uncertainty, missing information, and unsupported
claims.

Example:

{
  "uncertainty_handling": [
    "Do not guess when reliable information is unavailable",
    "Clearly state when information is uncertain",
    "Ask for clarification when required information is missing"
  ]
}
escalation_behavior

Type: array[string]

Instructions describing when the agent should escalate an issue.

Example:

{
  "escalation_behavior": [
    "Escalate issues that cannot be resolved using approved knowledge",
    "Escalate requests requiring human authorization"
  ]
}

If escalation is not required:

{
  "escalation_behavior": []
}
input_handling

Type: array[string]

Instructions for interpreting and handling agent inputs.

Example:

{
  "input_handling": [
    "Treat the customer's question as the primary input",
    "Request missing information when necessary"
  ]
}
output_behavior

Type: array[string]

Instructions describing how the agent should produce its responses.

Example:

{
  "output_behavior": [
    "Answer the user's question directly",
    "Keep responses concise and clear",
    "Do not present unsupported information as fact"
  ]
}
Validation Rules

The instructions object must satisfy:

identity must be an object.
identity.role must be a string.
identity.purpose must be a string.
responsibilities must be an array of strings.
task_instructions must be an array of strings.
behavioral_rules must be an array of strings.
constraints must be an array of strings.
tool_usage must be an array of objects.
Every tool-usage object must contain tool.
Every tool-usage object must contain when_to_use.
Every tool-usage object must contain purpose.
Every tool-usage object must contain restrictions.
tool_selection_rules must be an array of strings.
uncertainty_handling must be an array of strings.
escalation_behavior must be an array of strings.
input_handling must be an array of strings.
output_behavior must be an array of strings.
Do not reference tools that were not selected.
Do not invent requirements or policies.
Do not add fields outside this schema.
Do not include API credentials or secrets.
Do not include implementation details that are irrelevant to the agent.
Example
{
  "identity": {
    "role": "Customer support assistant",
    "purpose": "Help customers resolve product and service questions"
  },
  "responsibilities": [
    "Answer customer questions",
    "Provide approved product information",
    "Escalate unresolved issues"
  ],
  "task_instructions": [
    "Analyze the customer's question before responding",
    "Search the knowledge base when company-specific information is required",
    "Use retrieved information to formulate an accurate response"
  ],
  "behavioral_rules": [
    "Be professional",
    "Be concise",
    "Ask clarifying questions when necessary"
  ],
  "constraints": [
    "Do not fabricate information",
    "Only use approved knowledge sources"
  ],
  "tool_usage": [
    {
      "tool": "knowledge_base_search",
      "when_to_use": "Use when company-specific information is required",
      "purpose": "Retrieve approved company information",
      "restrictions": [
        "Only search approved knowledge sources"
      ]
    }
  ],
  "tool_selection_rules": [
    "Use tools only when necessary",
    "Use the most relevant available tool"
  ],
  "uncertainty_handling": [
    "Do not guess when reliable information is unavailable",
    "Ask for clarification when required information is missing"
  ],
  "escalation_behavior": [
    "Escalate unresolved issues to human support"
  ],
  "input_handling": [
    "Treat the customer's question as the primary input",
    "Request missing information when necessary"
  ],
  "output_behavior": [
    "Answer the customer's question directly",
    "Keep responses clear and concise",
    "Do not present unsupported information as fact"
  ]
}
Conversion to Final Instructions

The final agent instructions may be constructed from these sections in the
following logical order:

Identity
↓
Purpose
↓
Responsibilities
↓
Task Instructions
↓
Behavioral Rules
↓
Constraints
↓
Tool Usage
↓
Tool Selection Rules
↓
Uncertainty Handling
↓
Escalation Behavior
↓
Input Handling
↓
Output Behavior

This schema represents the instruction layer only.

The final Agent Definition is produced by the parent agent-creator
orchestration process and must still comply with:

agent-creator/references/AGENT_SCHEMA.md