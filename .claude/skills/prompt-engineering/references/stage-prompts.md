# Stage Prompts

## Purpose

Define the responsibilities and prompt contracts for every LLM-driven stage in the Agent Factory.

Each stage must have one primary responsibility.

Do not combine unrelated intelligence tasks into a single prompt.

---

# 1. Task Analyzer

## Responsibility

Convert natural language into TaskSpec.

## Input

- user request
- relevant project context
- available constraints

## Output

TaskSpec

## Must Do

- identify objective
- identify inputs
- identify expected outputs
- identify constraints
- identify required capabilities
- identify complexity
- identify ambiguity

## Must Not Do

- generate code
- invent tools
- generate final AgentSpec
- choose an unsupported architecture

---

# 2. Architecture Planner

## Responsibility

Select the most appropriate registered architecture.

## Input

- TaskSpec
- Architecture Registry
- architecture patterns
- relevant constraints

## Output

ArchitecturePlan

## Must Do

- select one supported architecture
- explain the structural reason
- identify required components

## Must Not Do

- invent architectures
- generate code
- select nonexistent tools
- bypass architecture contracts

---

# 3. Capability Selector

## Responsibility

Select registered tools and skills required to implement the plan.

## Input

- TaskSpec
- ArchitecturePlan
- Tool Registry
- Skill Registry

## Output

CapabilityPlan

## Must Do

- select only registered capabilities
- identify missing capabilities
- avoid unnecessary capabilities

## Must Not Do

- invent tools
- invent skills
- generate code
- redesign architecture

---

# 4. Agent Designer

## Responsibility

Convert:

TaskSpec
+
ArchitecturePlan
+
CapabilityPlan

into AgentSpec.

## Must Do

- satisfy architecture contract
- reference canonical capabilities
- preserve user intent
- produce complete structured specification

## Must Not Do

- generate implementation code
- invent capabilities
- bypass validation

---

# 5. Generator

## Responsibility

Convert validated AgentSpec into generated files.

## Input

- AgentSpec
- Architecture Definition
- Template
- selected capabilities

## Output

Generated project

## Must Do

- render the correct template
- preserve AgentSpec semantics
- generate required files

## Must Not Do

- redesign the agent
- select a different architecture
- invent tools
- invent skills

---

# 6. Evaluator

## Responsibility

Determine whether the generated agent satisfies the task.

## Input

- original task
- AgentSpec
- generated project
- test results

## Output

EvaluationResult

## Must Do

- identify failures
- distinguish structural from behavioral failures
- produce actionable feedback

## Must Not Do

- silently modify the generated agent
- hide failures

---

# 7. Repair

## Responsibility

Repair the artifact responsible for the failure.

## Input

- original task
- artifact
- validation errors
- evaluation feedback

## Output

Repaired artifact

## Must Do

- preserve user intent
- make minimal changes
- revalidate

## Must Not Do

- rewrite unrelated components
- invent unsupported capabilities
- change architecture without justification

---

# 8. Structured Output Rule

Every LLM stage that feeds another software component should produce structured output.

Preferred:

JSON / typed schema / validated model

Avoid:

free-form prose when the output is machine-consumed.

---

# 9. Prompt Composition

Prefer:

System Instructions
+
Stage Instructions
+
Task Input
+
Relevant Registry Information
+
Relevant References
+
Output Schema

Do not include unrelated project information.

---

# 10. Failure Behavior

Every stage must define what happens when:

- output is malformed
- required field is missing
- confidence is insufficient
- capability is unavailable
- architecture is unsupported

Failures must remain explicit.

---

# 11. Prompt Stability

Prompts should not contain duplicated architecture definitions that already exist in registries or references.

Prefer referencing authoritative sources.

The registry and schema should provide machine-enforced constraints.

The prompt should explain the decision responsibility.
