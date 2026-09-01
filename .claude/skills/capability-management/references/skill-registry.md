# Skill Registry

## Purpose

The Skill Registry is the authoritative discovery and loading mechanism for Agent Skills.

It must preserve Progressive Disclosure.

The registry determines:

- which skills exist
- which skills are relevant
- how skills are discovered
- how skill metadata is loaded
- when full skill instructions are loaded

---

# 1. Skill Structure

A skill should normally have:

```text
skill-name/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Only required directories should exist.

---

# 2. SKILL.md

Every registered skill must have a SKILL.md.

The frontmatter should define:

- name
- description

The description must explain:

- what the skill does
- when it should be used

---

# 3. Progressive Disclosure

Do not load every skill into the model context.

Preferred flow:

Skill Registry
 ↓
Skill Metadata
 ↓
Relevant Skills
 ↓
SKILL.md
 ↓
Relevant References
 ↓
Scripts / Assets when required

The model should receive only relevant skill content.

---

# 4. Skill Metadata

Metadata should contain enough information for discovery without loading the full skill.

Example:

```yaml
name: code-generation

description: Generate agent projects from validated AgentSpec using architecture-specific templates.
```

---

# 5. Skill Selection

Skill selection should consider:

- task requirements
- architecture
- requested capabilities
- current pipeline stage
- available context
- skill dependencies

Do not select skills merely because their names match a keyword.

---

# 6. Skill Dependencies

A skill may declare dependencies on other skills.

Example:

```yaml
dependencies:
  - agent-spec
  - architecture-registry
```

Dependency loading must not create uncontrolled context expansion.

---

# 7. Skill Loading

When a skill is selected:

1. Load SKILL.md.
2. Determine whether references are needed.
3. Load only relevant references.
4. Execute scripts only when required and permitted.

---

# 8. Skill Isolation

A skill should have a clearly defined responsibility.

Avoid skills that attempt to contain the entire Agent Factory architecture.

Bad:

"Build and operate the complete Agent Factory."

Better:

"Validate AgentSpec."

---

# 9. Skill References

References should contain detailed domain knowledge that is not necessary for initial discovery.

Examples:

- architecture contracts
- validation rules
- examples
- schemas
- implementation guides

---

# 10. Skill Scripts

Scripts may be used for deterministic operations such as:

- validation
- parsing
- transformation
- inspection
- testing

Do not use an LLM prompt when deterministic code is sufficient.

---

# 11. Registry Requirements

The registry should support:

- filesystem discovery
- metadata loading
- lookup by name
- relevance filtering
- dependency resolution
- progressive loading
- validation

---

# 12. Skill Validation

Validate:

- skill directory exists
- SKILL.md exists
- frontmatter is valid
- name exists
- description exists
- name is unique
- references are resolvable
- dependencies exist

---

# 13. Skill and AgentSpec

AgentSpec references skills by canonical ID.

Example:

```yaml
skills:
  - research
  - report-writing
```

The generator must resolve these references through the Skill Registry.

---

# 14. Important Rule

Skills provide procedural knowledge.

Tools provide executable capabilities.

Never replace a tool with a skill merely because the skill describes how the tool should be used.
