# Generated Project Contract

## Purpose

Define the structure and requirements of every generated Agent project.

A generation operation is successful only when the generated project satisfies this contract.

---

# 1. Standard Structure

A basic generated agent should contain:

```text
generated/
└── agent-name/
    ├── agent.py
    ├── config.yaml
    ├── instructions.md
    ├── requirements.txt
    ├── README.md
    └── tests/
```

Architecture-specific projects may contain additional files.

---

# 2. agent.py

Must contain:

- the main agent implementation
- runtime initialization
- registered capability integration
- instruction loading
- required execution logic

It must be syntactically valid.

---

# 3. config.yaml

Contains configuration required by the generated runtime.

It must:

- be valid YAML
- contain only supported configuration
- not contain secrets
- correspond to AgentSpec

---

# 4. instructions.md

Contains the generated agent instructions.

Instructions should reflect the validated AgentSpec.

The generator must not introduce new behavioral requirements.

---

# 5. requirements.txt

Contains required dependencies.

Dependencies must correspond to the generated implementation.

Do not add unnecessary dependencies.

---

# 6. README.md

Should describe:

- agent purpose
- architecture
- capabilities
- setup
- configuration
- execution
- testing

Do not claim capabilities that were not generated.

---

# 7. tests/

Contains tests appropriate for the generated architecture.

At minimum, tests should verify:

- basic initialization
- required configuration
- architecture structure
- critical capabilities

---

# 8. Architecture-Specific Files

For orchestrator-workers:

```text
agent/
├── agent.py
├── workers/
│   ├── researcher.py
│   ├── analyst.py
│   └── writer.py
├── config.yaml
├── instructions.md
└── tests/
```

Worker files must correspond exactly to AgentSpec workers.

---

# 9. AgentSpec Consistency

The generated project must preserve:

- agent name
- architecture
- tools
- skills
- workers
- routes
- workflow
- constraints

No silent changes are allowed.

---

# 10. Tool Consistency

Every generated tool reference must exist in Tool Registry.

No generated file may reference a nonexistent tool.

---

# 11. Skill Consistency

Every generated skill reference must exist in Skill Registry.

---

# 12. File Completeness

Generation fails if required files are missing.

Example:

AgentSpec:

```yaml
workers:
  - researcher
  - analyst
  - writer
```

Generated:

```text
workers/
  researcher.py
  analyst.py
```

Result:

FAIL

because writer.py is missing.

---

# 13. Syntax Validation

Generated Python must compile successfully.

Generated YAML must parse successfully.

Generated JSON, when present, must parse successfully.

---

# 14. Runtime Validation

Where feasible, the generated project should pass a minimal initialization test.

Generation should not be considered successful merely because files exist.

---

# 15. Reproducibility

Generated projects should contain metadata sufficient to identify:

- AgentSpec version
- architecture version
- template version
- generator version

---

# 16. Security

Generated projects must not contain:

- API keys
- credentials
- secrets
- private tokens

Use environment variables or approved secret-management mechanisms.

---

# 17. Completion Definition

Generated Agent is complete only when:

Files Exist
+
Schemas Valid
+
Python Valid
+
References Valid
+
Architecture Valid
+
Tests Pass
