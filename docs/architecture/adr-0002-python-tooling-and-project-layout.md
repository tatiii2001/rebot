# ADR-0002: Python Tooling and Project Layout

## Status

Accepted

## Context

ADR-0001 establishes ReBot as a modular monolith with Hexagonal Architecture and Clean Architecture, implemented initially as one Python backend and simulator process plus a separately built React and TypeScript Control Center. It defines inward dependencies and architectural responsibilities but deliberately defers physical source paths, Python and testing tools, and package management.

ReBot now needs a consistent foundation for implementing vertical slices without weakening those boundaries. The foundation must support reproducible development, static typing, focused testing, executable acceptance specifications, and separate management of the Python and web applications. It must also avoid creating speculative packages or selecting runtime technologies before a concrete vertical slice justifies them.

## Decision

### Python Version

The Python backend and simulator will use CPython 3.14. Future project metadata will express support for the Python 3.14 minor series: Python 3.14 is the minimum, and Python 3.15 is not automatically included. No patch release is pinned by this decision.

This selects the current stable Python minor series while preventing accidental adoption of a future minor version without validation. This decision does not claim compatibility with Python 3.15.

### Repository Shape

ReBot remains one repository containing separately managed applications. The approved top-level application locations are:

- `backend/` for the Python backend, domain, application behavior, adapters, and simulator.
- `control-center/` for the future React and TypeScript web client.

Shared repository documentation and OpenCode configuration remain at the repository root. This physical separation does not turn the applications into microservices. ReBot retains the modular-monolith architecture and initial deployment direction established by ADR-0001.

### Python Source Layout

Python will use a `src` layout rooted at `backend/src/rebot/`. The initial package roles are:

- `rebot/domain/` owns domain behavior and invariants.
- `rebot/application/` coordinates application behavior and may depend on domain.
- `rebot/adapters/` contains driving and driven technical adapters.
- `rebot/bootstrap/` is the composition root and may know and wire concrete adapters.

The intended dependency direction is `bootstrap -> adapters -> application -> domain`:

- Domain depends on none of the other packages.
- Application may depend on domain.
- Driving adapters must invoke application use cases and must not access driven adapters or technical systems directly. Driven adapters implement application ports and may interact with the specific technical systems associated with those ports. Application code must depend on port abstractions rather than concrete driven adapters. Concrete adapter wiring remains restricted to `bootstrap`.
- Bootstrap owns composition and may depend on concrete adapters.

These are approved package roles, not authorization to create empty directories. Packages and subpackages will be created incrementally only when a real vertical slice requires them. This ADR does not define aggregates, entities, repositories, ports, DTOs, services, domain events, controllers, or use-case classes.

No generic `shared`, `common`, `utils`, or `helpers` package will be created. No separate `infrastructure` package is approved now; concrete technical implementations belong under the appropriate adapter role unless a later ADR demonstrates the need for a different boundary.

### Package and Environment Management

ReBot will use `uv` for Python version coordination, virtual-environment management, dependency declaration and resolution, dependency locking, and running project tools.

The future Python project will use `backend/pyproject.toml` as the authoritative Python project and tool configuration and will commit `backend/uv.lock` for reproducible application development. Its local virtual environment will not be committed.

This decision does not select runtime dependencies or an API framework. It also does not authorize creation of the project metadata, lockfile, virtual environment, or application directories as part of this ADR.

### Code Quality

ReBot will use Ruff for linting and formatting and Pyright for static type checking. A second formatter or overlapping general-purpose Python linter will not be added.

Static typing is required for production Python code. The intended direction is strict type checking for `backend/src/rebot`; any temporary exception must be explicit, narrow, and justified.

Concrete Ruff rules, formatter settings, exclusions, and Pyright configuration are future scaffold work and must be validated against the selected tool versions.

### Testing Tools

ReBot will use:

- pytest as the Python test runner.
- pytest-bdd for BDD scenarios integrated with pytest.
- pytest-cov for coverage measurement.

BDD scenarios remain acceptance specifications. They complement rather than replace focused unit, application, integration, contract, and end-to-end tests. No numerical coverage threshold is established; coverage is diagnostic evidence and must not incentivize low-value tests.

### Test Layout

The planned test locations and responsibilities are:

- `backend/tests/unit/domain/` verifies domain invariants and state transitions without frameworks or I/O.
- `backend/tests/unit/application/` verifies application behavior using test doubles at port boundaries.
- `backend/tests/integration/adapters/` verifies concrete adapters.
- `backend/tests/architecture/` protects dependency direction.
- `backend/tests/contract/` protects published API contracts.
- `backend/tests/acceptance/features/` contains pytest-bdd acceptance scenarios.
- `backend/tests/acceptance/steps/` contains pytest-bdd step definitions.
- `backend/tests/e2e/` is reserved for a small number of critical journeys.

Each directory will be created only when the first real test of that category exists. This ADR does not authorize creating empty test directories.

### TDD Workflow

Implementation will follow this workflow:

1. Define or confirm acceptance criteria.
2. Add one focused failing test.
3. Confirm Red for the expected reason.
4. Implement the minimum behavior for Green.
5. Refactor only while Green.
6. Run focused and relevant broader verification.

## Consequences

### Positive

- CPython support is explicit and requires deliberate validation before adopting another minor series.
- Separately managed application roots make Python and TypeScript ownership and tooling clear while preserving one repository.
- The `src` layout prevents accidental imports from the repository working directory and makes installed-package behavior more representative.
- Physical package roles reinforce the inward dependency direction established by ADR-0001.
- `uv` provides one workflow for Python versions, environments, dependency resolution, locking, and tool execution.
- Ruff and Pyright provide non-overlapping formatting, linting, and static-type responsibilities.
- The test layout aligns tests with architectural boundaries and keeps BDD acceptance specifications within the pytest ecosystem.
- Incremental directory creation prevents empty architecture scaffolding from being mistaken for implemented design.

### Negative or Trade-offs

- Contributors must install and learn `uv`, Ruff, Pyright, pytest, pytest-bdd, and pytest-cov.
- Restricting support to the Python 3.14 minor series requires explicit validation and metadata changes before Python 3.15 can be supported.
- A `src` layout requires the project to be installed in its environment before package imports behave as intended.
- Strict typing and architecture checks add implementation and maintenance effort.
- Separately managed applications require coordination at their published contract boundary.
- Deferring exact configuration means the future scaffold must still validate and record version-specific settings and commands.

## Alternatives Considered

### Python 3.15 Pre-release

Not selected because the project foundation should use the current stable minor series. Python 3.15 can be evaluated after release and explicit compatibility validation.

### Python 3.12 or Older Security-only Releases

Not selected because they would begin the project on older language series, with some already limited to security maintenance, rather than the approved current stable series.

### pip with Manually Managed Virtual Environments

Not selected because it would require separate conventions and tools for Python coordination, environment management, dependency resolution, locking, and command execution. `uv` supplies one consistent workflow for these responsibilities.

### Poetry

Not selected because `uv` satisfies the approved environment, project, locking, and tool-running needs with no requirement for Poetry-specific project management features.

### Black with Additional Overlapping Lint Tools

Not selected because Ruff provides the required formatter and linter while avoiding overlapping general-purpose tools and duplicate configuration.

### mypy

Not selected because Pyright is the approved static type checker and supports the intended strict-typing direction. This choice avoids maintaining two type-checking configurations.

### Behave

Not selected because pytest-bdd keeps acceptance scenarios integrated with the selected pytest runner and its fixtures and plugins.

### Flat Layout without `src`

Not selected because a flat layout can allow imports to succeed from the repository working directory without exercising the installed package. The `src` layout makes that distinction explicit.

### Creating Every Architectural Directory in Advance

Not selected because empty directories and placeholder packages would imply unsupported design detail. Directories will appear only with the vertical slice or test that requires them.

### One Undifferentiated Application Directory for Python and TypeScript

Not selected because the backend and Control Center have distinct build and dependency ecosystems. Separate application roots preserve those boundaries without creating distributed services or separate repositories.

## Deferred Decisions

- Exact dependency versions and lock resolution.
- API framework.
- Persistence technology.
- Serialization and validation framework.
- Frontend tooling and package manager.
- Ruff rule selection and formatter details.
- Exact Pyright configuration.
- Numerical coverage threshold.
- CI platform and commands.
- Containerization.
- Deployment infrastructure.
- Concrete architecture-test implementation.
- Exact API contract mechanism.
- Domain model and port interfaces for the first vertical slice.

## References

- `AGENTS.md`
- `opencode.json`
- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/domain-rules.md`
- `docs/architecture/overview.md`
- `docs/architecture/adr-0001-modular-monolith-and-hexagonal-architecture.md`
