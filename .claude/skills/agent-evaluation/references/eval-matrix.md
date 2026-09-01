# Evaluation Matrix

## Purpose

Define the evaluation matrix for determining whether the Agent Factory genuinely supports an architecture.

---

# 1. Architecture Matrix

| Architecture | Planning | AgentSpec | Validation | Generation | Code Validation | Evaluation |
|---|---|---|---|---|---|---|
| single-agent | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| sequential | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| parallel | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| router | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| supervisor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| orchestrator-workers | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| evaluator-optimizer | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| handoff | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

An architecture is not supported unless every required stage passes.

---

# 2. Planning Evaluation

Measure:

- architecture correctness
- task decomposition
- required capabilities
- constraints

---

# 3. AgentSpec Evaluation

Measure:

- schema validity
- architecture consistency
- tool references
- skill references
- worker references
- route references
- workflow correctness

---

# 4. Generation Evaluation

Measure:

- required files
- correct template
- architecture structure
- capability integration
- configuration
- instructions

---

# 5. Code Validation

Measure:

- Python syntax
- imports
- configuration syntax
- generated tests
- runtime initialization

---

# 6. Behavioral Evaluation

Measure:

- requirement coverage
- expected outputs
- tool usage
- workflow behavior
- failure handling

---

# 7. Negative Evaluation

Every architecture should include invalid requests.

Examples:

- unsupported architecture
- missing worker
- unknown tool
- unknown skill
- invalid route
- invalid workflow

Expected behavior:

Controlled failure.

Never silent generation.

---

# 8. Regression Matrix

Every change should run:

Existing Tests
+
Architecture Tests
+
AgentSpec Tests
+
Registry Tests
+
Generation Tests
+
End-to-End Tests

---

# 9. Metrics

Track:

## Architecture Accuracy

Correct architecture selections / total cases

## AgentSpec Validity

Valid AgentSpecs / total AgentSpecs

## Generation Success

Successfully generated projects / valid AgentSpecs

## Code Validation Success

Valid generated projects / generated projects

## End-to-End Success

Successful complete tasks / total tasks

## Repair Success

Successfully repaired failures / repair attempts

---

# 10. Evaluation Categories

Use:

- deterministic tests
- schema tests
- structural tests
- integration tests
- behavioral tests
- LLM-as-judge only where deterministic validation is insufficient

---

# 11. Baseline

Maintain a baseline before major changes.

New changes must not cause regression in:

- existing tests
- generation success
- architecture accuracy
- validation success

---

# 12. Failure Analysis

Every failed evaluation should identify:

- stage
- input
- expected
- actual
- root cause
- repairability

---

# 13. Completion Rule

An architecture is officially supported only if it passes the complete evaluation matrix.
