# ADR-0001: Modular Monolith and Hexagonal Architecture

## Status

Accepted

## Context

ReBot must demonstrate a coherent, deterministic Cleaning Mission in a two-dimensional grid-based Simulated Environment while keeping domain behavior understandable, testable, and independent of delivery technology. The MVP combines confirmed Mission, Robot, Waste Item, Route, Battery Level, collection, deposit, Required Incident, and completion rules with application coordination, simulation mechanisms, a backend API boundary, telemetry delivery, and a React and TypeScript Control Center.

The project needs clear boundaries without the operational and design overhead of distributed services. It must also avoid coupling confirmed domain rules to a web framework, transport model, persistence mechanism, rendering library, or other technical edge. At the same time, a single undifferentiated script would obscure responsibility, make inward dependency rules unenforceable, and make focused testing difficult.

## Decision

ReBot will begin as a modular monolith using Hexagonal Architecture and Clean Architecture with explicit inward dependency direction.

The conceptual Python core contains domain behavior, application use cases, simulation orchestration, and the backend API boundary within one modular system. Responsibilities remain logically separated:

- Infrastructure and adapters may depend on application and domain.
- Application may depend on domain.
- Domain depends on neither application nor infrastructure.
- Frameworks and delivery mechanisms remain at the edges.
- The React and TypeScript Control Center is an external driving adapter that communicates through published API contracts and never imports Python domain or application code.
- One composition and bootstrap boundary wires concrete adapters to application ports.

The domain owns confirmed business behavior and invariants. The application coordinates use cases, invokes domain behavior, and defines ports required by those use cases. Driving and driven adapters perform technical translation and integration. The deterministic simulation is coordinated through these boundaries; technical timing, loops, rendering, transport, and framework integration are not domain responsibilities.

The initial deployment direction may use one Python backend and simulator process plus one separately built React and TypeScript web client. This deployment boundary does not divide the domain into distributed services.

This decision establishes architectural roles only. It does not approve concrete port interfaces, physical package paths, aggregate boundaries, repositories, domain events, or specific framework, persistence, messaging, package-management, or transport technology.

## Consequences

### Positive

- Confirmed domain rules can evolve and be tested without framework or infrastructure dependencies.
- Explicit ports and adapters make delivery and technical mechanisms replaceable when a justified requirement appears.
- A modular monolith keeps MVP development, local execution, debugging, and consistency simpler than a distributed system.
- The Control Center and Python core have a clear contract boundary without sharing internal models.
- Focused domain, application, adapter, contract, frontend, architecture, and end-to-end testing can align with responsibility boundaries.
- One composition boundary makes concrete dependency wiring visible and keeps construction concerns out of domain and application behavior.

### Negative or Trade-offs

- Boundary discipline must be maintained within one process because deployment boundaries do not enforce modularity.
- Explicit application ports and adapter mappings add structure compared with direct framework calls.
- The modular monolith may require later internal reorganization as justified responsibilities become clearer.
- A separately built Control Center requires API contract coordination even though the Python core is not distributed internally.
- Deferred technical choices limit implementation detail now and require later decisions before affected capabilities can be built.

## Alternatives Considered

### Microservices

Rejected for the MVP. ReBot has one bounded MVP journey, one Robot, and no established need for independently deployable services, separate scaling, or distributed ownership. Microservices would introduce network failure modes, distributed consistency, deployment coordination, observability overhead, and premature service boundaries without corresponding product value. The separate web client does not justify splitting the Python domain into services.

### Framework-Centric Architecture

Rejected. Organizing the system around a selected web, persistence, validation, or simulation framework would direct dependencies toward technical mechanisms and risk placing domain invariants in handlers, transport models, or infrastructure objects. Frameworks must remain replaceable edge details and no specific framework is selected by this decision.

### Single Undifferentiated Script

Rejected. Combining domain rules, orchestration, simulation execution, transport, and presentation concerns in one script would obscure ownership, encourage coupling, impede focused tests, and make future adapter replacement costly. A modular monolith retains simple deployment while preserving explicit logical boundaries.

## Deferred Decisions

- Physical source paths, package layout, module names, classes, and concrete port interfaces.
- Aggregate boundaries, repositories, domain events, entities, value objects, and domain services not yet justified by implementation evidence.
- Simulation loop, clock abstraction, rendering mechanism, and exact Route-planning algorithm.
- Backend API framework, serialization design, telemetry delivery, and real-time transport.
- Persistence requirements and technology, ORM, messaging, and external service integrations.
- Frontend state and component libraries and detailed Control Center design.
- Python and Node versions, package managers, containers, cloud infrastructure, and production deployment topology.
- Testing libraries, BDD tooling, coverage thresholds, and CI tooling.
- Product and domain questions explicitly deferred by the MVP and domain documentation.

## References

- `AGENTS.md`
- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/domain-rules.md`
- `docs/architecture/overview.md`
