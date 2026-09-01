# Validation Rules

## Purpose

Define deterministic validation rules for AgentSpec and generated agent projects.

Validation must occur before generation and after generation.

---

# 1. Validation Layers

The system validates:

1. TaskSpec
2. ArchitecturePlan
3. CapabilityPlan
4. AgentSpec
5. Generated Project
6. Runtime Behavior
7. Evaluation Result

---

# 2. TaskSpec Validation

Verify:

- task exists
- objective is present
- required outputs are identifiable
- constraints are valid
- ambiguity is represented when relevant

---

# 3. ArchitecturePlan Validation

Verify:

- architecture is registered
- architecture is supported
- architecture rationale exists
- required components can be represented

---

# 4. CapabilityPlan Validation

Verify:

- every selected tool exists
- every selected skill exists
- no duplicate capability identifiers
- architecture compatibility
- required permissions

---

# 5. AgentSpec Validation

Verify:

- name exists
- purpose exists
- architecture exists
- architecture is registered
- required fields exist
- tools are registered
- skills are registered
- workflow is valid
- workers are valid
- routes are valid

---

# 6. Architecture Validation

Apply architecture-specific contract rules.

Example:

orchestrator-workers requires:

```
workers != empty
```

router requires:

```
routes != empty
```

sequential requires:

```
workflow != empty
```

---

# 7. Reference Validation

Every reference must resolve.

Examples:

- worker ID
- tool ID
- skill ID
- route target
- template ID

Unknown references cause validation failure.

---

# 8. Duplicate Validation

Reject or normalize:

- duplicate tool IDs
- duplicate skill IDs
- duplicate worker IDs
- duplicate route identifiers
- duplicate output names

---

# 9. Generated File Validation

Verify:

- required files exist
- forbidden files are not unexpectedly generated
- file paths are safe
- generated structure matches architecture

---

# 10. Python Validation

Verify:

- syntax
- imports
- module references
- generated entry point

Use deterministic tooling whenever possible.

Do not ask an LLM to determine whether Python syntax is valid when a parser can do it.

---

# 11. YAML Validation

Verify:

- valid syntax
- required keys
- expected types
- no unsupported configuration

---

# 12. Tool Validation

Every generated tool reference must:

- exist
- be active
- satisfy permissions
- satisfy runtime requirements

---

# 13. Skill Validation

Every generated skill reference must:

- exist
- be loadable
- have valid metadata

---

# 14. Architecture Structure Validation

Examples:

Sequential:

workflow exists and is ordered.

Parallel:

workers exist and are independently defined.

Router:

routes exist and targets resolve.

Orchestrator Workers:

workers exist and are generated.

---

# 15. Error Classification

Use explicit error classes:

- TaskValidationError
- ArchitectureError
- CapabilityError
- AgentSpecValidationError
- GenerationError
- GeneratedCodeValidationError
- EvaluationError

---

# 16. Validation Result

Prefer structured results:

```json
{
  "status": "fail",
  "errors": [
    {
      "code": "MISSING_WORKER",
      "field": "workers",
      "message": "Worker 'writer' is referenced but not defined."
    }
  ]
}
```

---

# 17. Fail Fast

When a blocking structural error exists:

Do not continue to generation.

Repair or report the issue first.

---

# 18. Validation Must Be Deterministic

Use code for deterministic checks.

LLMs may assist with semantic evaluation.

Do not replace deterministic validation with subjective model judgment.

---

# 19. Completion

Validation passes only when all blocking rules pass.

Warnings may be reported separately.

Warnings must never hide blocking failures.
