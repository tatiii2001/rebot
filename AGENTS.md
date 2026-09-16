# ReBot Project Rules

ReBot is a public portfolio project for progressively building an autonomous waste-collection robot simulator. Python will support the domain, application, backend API, and simulation; React and TypeScript will support the future control center.

## Language

- Use English throughout the repository, including documentation, code, tests, names, comments, commit messages, and user-facing text unless a requirement explicitly calls for another language.

## Architecture

- Follow Hexagonal Architecture, Clean Architecture, Domain-Driven Design, SOLID principles, and the dependency direction `infrastructure/adapters -> application -> domain`.
- Domain code must not depend on frameworks, HTTP, databases, ORM models, transport DTOs, Pydantic, FastAPI, or SQLAlchemy.
- Put business rules in domain entities, value objects, domain services, or domain policies.
- Keep architectural boundaries explicit and dependencies directed inward.
- Do not create speculative abstractions, placeholder files, or empty architecture folders.
- Record significant architectural decisions in Architecture Decision Records (ADRs).
- Update relevant documentation whenever behavior or architecture changes.

## Delivery

- Define clear acceptance criteria before implementation begins.
- Use TDD with the `Red -> Green -> Refactor` cycle.
- Write BDD scenarios for externally observable behaviors.
- Make changes small, sustainable, reviewable, and limited to the agreed scope.
- Before considering a task complete, run relevant tests, linting, and type checking once those tools exist.
- Report every changed file and every validation executed, including failures or validations that could not run.

## Safety And Scope

- Never overwrite or remove existing user changes without explicit authorization.
- Do not run Git commit, push, pull, fetch, merge, rebase, reset, clean, checkout, restore, switch, branch deletion, tag creation or deletion, remote modification, or any other remote Git operation.
- Stop and ask for clarification when a requested change would modify the agreed product scope, domain language, or architectural boundaries.
