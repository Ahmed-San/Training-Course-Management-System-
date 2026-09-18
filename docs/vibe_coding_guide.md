# Vibe Coding Boundary

AI-generated code is allowed only after the architecture and contracts in this repository are understood.

## Good bounded tasks

- repetitive feature entity boilerplate after the entity contract is defined
- specialized repository query implementation
- CLI formatting
- test case generation
- seed/demo data
- small refactors that preserve behavior

## Human-owned decisions

- domain relationships
- business rules
- authorization scope
- enrollment lifecycle
- evaluation locking
- transaction boundaries
- architecture changes

## Review rule

Every AI-generated change must be read, tested, and committed by a team member. Do not paste whole-project generation into the repository.

## Prompt pattern

```text
Implement only <one bounded task>.
Respect the existing contracts.
Do not change unrelated files.
Do not add third-party runtime dependencies.
Do not invent business rules.
Return the complete changed file and explain assumptions.
```
