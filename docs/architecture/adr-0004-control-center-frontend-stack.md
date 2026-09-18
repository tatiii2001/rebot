# ADR-0004: Control Center Frontend Stack

## Status

Accepted

## Context

ReBot needs a minimal visual Control Center that makes the simulated system understandable to the Operator before backend integration is available. The product vision and MVP require a web interface that can eventually control and observe a Cleaning Mission, while ADR-0001 establishes the Control Center as a separately built external driving adapter within one repository and one modular-monolith product direction. ADR-0002 reserves `control-center/` as the frontend application root.

The first visual proof of concept must validate that the approved mission and environment information can be presented coherently without prematurely selecting an API contract, telemetry transport, large frontend framework, or detailed visual design. It also must not duplicate the Python domain as a second source of business truth. A small, deterministic local source of display state allows this visual model to be exercised before the future backend boundary is defined.

The frontend needs a focused toolchain that supports typed implementation, component and interaction tests, and code-quality checks while keeping the first slice small and replaceable.

## Decision

### Frontend Foundation

The Control Center will use React and TypeScript. Vite will provide development and production build tooling. npm will be the initial frontend package manager. The frontend application root will be `control-center/`.

ReBot remains one repository with separately managed Python and frontend applications. This frontend boundary does not create a microservice or change the modular-monolith product direction established by ADR-0001 and ADR-0002.

The initial frontend quality toolchain will use:

- Vitest for frontend tests.
- React Testing Library for component and Operator-interaction tests.
- ESLint for frontend linting.
- TypeScript strict mode for static type checking.

No exact dependency versions are selected by this ADR.

### Styling and State

The initial user interface will use plain CSS. Styles should prefer CSS custom properties for intentionally shared visual values and semantic class names that describe interface roles rather than implementation details.

Component and state boundaries will remain small enough to test independently. No UI component framework, CSS framework, external state-management library, or other broad abstraction will be introduced without a demonstrated need.

The frontend will follow a small feature-oriented structure. Files and folders will be introduced only when required by an implemented vertical slice; speculative layers, a complete directory hierarchy, placeholder files, and empty folders are not approved.

## Architectural Boundaries

The Control Center is a driving adapter through which the Operator initiates actions and observes information. It is not the authoritative owner of ReBot domain behavior and must not contain authoritative domain rules. It will not import Python domain or application code or share internal Python models.

Presentation components will depend on an application-facing frontend boundary rather than directly on a local data source or future transport mechanism. The concrete shape of that boundary is deferred. This separation will allow the first local adapter to be replaced later by an HTTP or real-time adapter without redesigning presentation components.

The Python backend remains the future authoritative source of domain behavior. When backend integration is introduced, published contracts and adapter mappings will preserve the boundary established by ADR-0001. This ADR does not define those contracts, mappings, ports, DTOs, events, or transport protocols and does not change Python architecture or domain behavior.

## Deterministic Local-Adapter Strategy

The first visual proof of concept will use an in-memory local adapter that supplies a fixed, repeatable scenario through the application-facing frontend boundary. It will not connect to the Python backend.

The local adapter may support the first visual slice's deterministic transition from Mission State `pending` and Robot Operational State `available` to Mission State `running` and Robot Operational State `executing mission` when the Operator uses Start Mission. This behavior exists only to exercise the visual interaction and presentation states approved for the proof of concept.

The local behavior is a visual simulation adapter, not a second authoritative implementation of the Python domain. It must not grow into an independent domain model or become the source of business invariants. The future backend remains responsible for authoritative precondition evaluation and coordinated domain behavior, including the start behavior documented by ADR-0003.

The local adapter does not select simulation timing, a Route-planning algorithm, Battery Level values, grid dimensions, or any other deferred product or domain behavior.

## First Visual Slice

The initial interface will show:

- A bounded environment grid.
- One Robot.
- Waste Items.
- Static Obstacles.
- One Compatible Collection Point.
- Mission State.
- Robot Operational State.
- Battery Level.
- A Start Mission action.

This inventory defines the minimum visible proof of concept, not a detailed visual design or a complete MVP Control Center. The slice does not add domain rules, define environment dimensions or contents, or imply that later mission controls and telemetry requirements are removed from the MVP.

## Testing Strategy

Implementation will follow the repository's `Red -> Green -> Refactor` workflow. Vitest and React Testing Library will verify observable component behavior and Operator interactions, including rendering the deterministic scenario and the local Start Mission transition. Tests should interact through visible behavior rather than depend on component internals.

TypeScript strict mode will check production and test code statically. ESLint will enforce the frontend linting rules selected during scaffolding. The exact configuration, test organization, accessibility-checking additions, CI commands, and coverage measurement remain deferred. No coverage threshold or end-to-end browser tool is selected.

These frontend tests verify the visual adapter and presentation boundary. They do not replace Python domain, application, architecture, acceptance, adapter integration, or future API contract tests.

## Consequences

### Positive

- React and TypeScript align the Control Center with the approved product and architecture direction.
- Vite and npm provide a focused initial development and build workflow without selecting broader application infrastructure.
- A deterministic local adapter enables repeatable visual validation before backend contracts and transport are approved.
- The application-facing frontend boundary keeps presentation components independent of the temporary local data source and future backend transport.
- Strict typing, focused component tests, and linting support small, reviewable frontend slices.
- Plain CSS and incremental feature-oriented structure avoid premature framework and folder commitments.

### Negative or Trade-offs

- The local adapter introduces temporary code that will later be replaced for authoritative behavior.
- The visual transition can drift from backend behavior if it is allowed to expand beyond its explicitly limited proof-of-concept purpose.
- Deferring backend integration postpones validation of published contracts, transport behavior, and cross-application operation.
- Plain CSS and local component state may require later reassessment if demonstrated UI complexity justifies additional tools.
- Separately managed frontend tooling adds another development ecosystem within the repository.

## Rejected Alternatives

### Rendering the UI from Python Templates

Rejected because the approved architecture defines a separately built React and TypeScript Control Center as an external driving adapter. Python templates would couple presentation delivery to the backend and would not validate the intended client boundary.

### Introducing a UI Framework Immediately

Rejected because the first slice requires only a small, specific interface. A component or CSS framework would impose visual conventions, dependencies, and abstractions before repeated needs are known. Plain CSS is sufficient for the initial proof of concept.

### Connecting to the Backend Before Validating the Visual Model

Rejected because no backend API contract or telemetry transport has been approved. Coupling the first visual work to an invented interface would silently decide deferred architecture and make presentation validation depend on unrelated backend delivery work.

### Introducing Global State Management Immediately

Rejected because the initial deterministic scenario and one visual transition do not demonstrate a need for Redux or another external state-management library. Small state boundaries should be tested first, and a broader solution may be considered only when concrete complexity justifies it.

## Deferred Decisions

- Exact dependency versions, lockfile contents, and detailed npm workflow.
- Node.js version and exact Vite, TypeScript, ESLint, Vitest, and React Testing Library configuration.
- Detailed Control Center visual design, layout, responsive behavior, and design tokens beyond the initial plain-CSS direction.
- Exact frontend file hierarchy, component boundaries, state representation, and the concrete application-facing frontend boundary.
- UI component frameworks, CSS frameworks, and external state-management libraries unless future evidence justifies them.
- Routing and any routing library.
- Backend API framework, published API contracts, ports, DTOs, events, serialization, and validation mechanisms.
- HTTP client selection and backend integration timing.
- Real-time telemetry transport, including WebSockets and Server-Sent Events.
- Authentication, authorization, persistence, containers, deployment, cloud services, and production topology.
- End-to-end browser tooling, coverage measurement, and coverage thresholds.
- Grid dimensions, scenario contents, Battery Level values, simulation timing, Route-planning behavior, and all other product or domain decisions already deferred by the referenced documents.

## References

- `AGENTS.md`
- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/domain-rules.md`
- `docs/architecture/overview.md`
- `docs/architecture/adr-0001-modular-monolith-and-hexagonal-architecture.md`
- `docs/architecture/adr-0002-python-tooling-and-project-layout.md`
- `docs/architecture/adr-0003-stable-identity-and-active-mission-assignment.md`
