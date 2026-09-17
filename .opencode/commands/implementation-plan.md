---
description: Propose a read-only implementation plan for one small, agreed ReBot change.
agent: implementation-planner
subtask: false
---

Prepare an implementation plan for this requested behavior or technical change:

$ARGUMENTS

Treat the request as planning scope, not authorization to implement. If it is empty, ambiguous, excessively broad, or conflicts with documented decisions, ask concise clarification questions and stop.

Read `AGENTS.md` and only the relevant product, domain, architecture, ADR, BDD, test, and implementation artifacts needed to understand the scope. Do not invent requirements, domain rules, paths, or architectural decisions. Identify any ADR or domain decision required before implementation. Preserve Hexagonal Architecture, Clean Architecture, Domain-Driven Design, TDD, and BDD while proposing one small, reviewable vertical slice.

Return the proposal in this order:

1. **Goal**
2. **Confirmed requirements and acceptance criteria**
3. **Open questions or blockers**
4. **Relevant existing artifacts inspected**
5. **Proposed domain and application impact**
6. **Expected files to create or modify**, marking uncertain paths as candidates
7. **TDD sequence**: first failing test, minimum implementation, refactoring boundary, and broader verification
8. **Architecture and domain risks**
9. **Explicit exclusions**
10. **Completion criteria**
11. **Final readiness verdict**: exactly `ready for TDD`, `ready after clarification`, or `blocked`

The result is a proposal requiring human review. Remain completely read-only: do not create or edit files, execute implementation, install dependencies, stage changes, commit, push, or modify Git history. End the command immediately after returning the readiness verdict. Do not hand the plan back to another agent for continuation and do not begin implementation in the current session.
