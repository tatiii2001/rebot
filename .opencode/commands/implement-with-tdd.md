---
description: Implement one approved ReBot behavior through a controlled Red-Green-Refactor cycle.
agent: tdd-developer
subtask: true
---

Implement this exact approved scope:

$ARGUMENTS

Before editing, inspect `AGENTS.md`, the relevant acceptance criteria, BDD scenarios, domain documentation, ADRs, existing tests, implementation, and current worktree state. Preserve unrelated user changes.

If the scope is empty, vague, excessively broad, or inconsistent with documentation, ask one concise clarification question and stop without editing. Also stop without editing and report the prerequisite when acceptance criteria are missing, a domain or architecture decision remains unresolved, or required test tooling is unavailable or unconfigured. A prior plan is not proof that missing criteria or decisions were approved.

Implement only one small vertical slice through exactly one evidence-based `Red -> Green -> Refactor` cycle: establish one focused test that fails for the expected reason before changing production behavior, add only the minimum implementation needed for Green, and refactor only after Green. Then run focused and relevant broader verification supported by the repository.

Do not alter requirements to fit the code; weaken, skip, or delete tests to obtain Green; perform unrelated cleanup; add speculative abstractions; install dependencies; stage changes; commit; push; or modify Git history. Use only the existing `tdd-developer` permissions.

Return the complete TDD evidence and changed-file report required by the `tdd-developer` agent, including Red, Green, refactoring, broader validation, remaining risks, and Git safety confirmation.
