# Repair Loop

## Purpose

Define the controlled repair process for Agent Factory failures.

The repair system must repair the correct abstraction layer.

---

# 1. Core Principle

Repair the source of the failure.

If AgentSpec is wrong:

Repair AgentSpec.

If generated code is wrong:

Repair generated code or regenerate.

If the template is wrong:

Repair the template.

If the registry is wrong:

Repair the registry.

Do not blindly regenerate everything.

---

# 2. Design Repair

Design Repair operates on:

- TaskSpec
- ArchitecturePlan
- CapabilityPlan
- AgentSpec

Flow:

```text
Artifact
    ↓
Validation
    ↓
Failure
    ↓
Identify Root Cause
    ↓
Repair
    ↓
Validation
    ↓
PASS / FAIL
```

---

# 3. Code Repair

Code Repair operates on:

- generated source files
- configuration
- generated tests

Flow:

```text
Generated Project
    ↓
Code Validation
    ↓
Failure
    ↓
Identify Root Cause
    ↓
Repair / Regenerate
    ↓
Validation
    ↓
PASS / FAIL
```

---

# 4. Root Cause Classification

Classify failures as:

## Requirement Failure

The task was misunderstood.

Repair: TaskSpec.

---

## Architecture Failure

The wrong architecture was selected.

Repair: ArchitecturePlan.

Do not simply patch generated code.

---

## Capability Failure

Required tool or skill is missing or incorrectly selected.

Repair: CapabilityPlan.

---

## AgentSpec Failure

The architecture or agent structure violates its contract.

Repair: AgentSpec.

---

## Template Failure

AgentSpec is valid but generated structure is incorrect.

Repair: Template or generator.

---

## Generated Code Failure

Template is correct but implementation output is invalid.

Repair: Generated artifact or regenerate.

---

## Evaluation Failure

Generated agent is structurally valid but behavior does not satisfy requirements.

Repair: AgentSpec, instructions, template, or generated implementation depending on root cause.

---

# 5. Repair Input

A repair request should include:

- original task
- current artifact
- exact validation error
- relevant contract
- relevant registry information
- previous repair attempts when necessary

---

# 6. Minimal Change Principle

Every repair should make the smallest change capable of resolving the failure.

Do not:

- rewrite unrelated files
- change architecture unnecessarily
- replace working components
- introduce new dependencies without justification

---

# 7. Preserve User Intent

Repair must preserve the original task requirements.

Never "fix" an implementation by silently removing a user requirement.

---

# 8. Repair Attempts

Configure a maximum repair count.

Example:

```yaml
repair:
  max_attempts: 3
```

If the maximum is reached:

Return a structured failure.

Do not loop indefinitely.

---

# 9. Revalidation

Every repair must be followed by validation.

Never assume the repair succeeded.

---

# 10. Two-Level Repair

The system should distinguish:

### Design Repair

```text
AgentSpec
↓
Repair
↓
Validate
↓
Generate
```

### Code Repair

```text
Generated Code
↓
Repair
↓
Validate
```

---

# 11. Escalation

If repeated repairs fail:

1. stop the loop
2. preserve artifacts
3. report root cause
4. report attempted repairs
5. report remaining failure

Do not hide the failure.

---

# 12. Repair Logging

Record:

- attempt number
- artifact
- failure
- root cause
- change
- validation result
- duration

Do not record secrets.

---

# 13. Repair Success

Repair succeeds only when the appropriate validation layer passes.

For AgentSpec:

AgentSpec Validation = PASS

For generated code:

Code Validation = PASS

For end-to-end behavior:

Evaluation = PASS

---

# 14. Important Rule

A repair loop is not:

"Ask the LLM to try again."

A repair loop is:

```text
Failure
    ↓
Root Cause
    ↓
Targeted Repair
    ↓
Deterministic Validation
    ↓
Re-evaluation
```
