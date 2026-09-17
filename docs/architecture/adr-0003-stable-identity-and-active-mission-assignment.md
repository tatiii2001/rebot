# ADR-0003: Stable Identity and Active Mission Assignment

## Status

Accepted

## Context

The ReBot domain rules require a Cleaning Mission to start only when it is `pending` and its assigned Robot is `available` (`MISSION-002`), and successful start must change the Cleaning Mission to `running` and the Robot to `executing mission` as one coordinated domain outcome (`MISSION-003`). A Robot cannot have more than one Active Mission (`MISSION-004`), and `pending`, `running`, and `paused` are all Active Mission states (`MISSION-005`). Invalid start must produce one neutral Mission Start Rejection without changing either participant (`MISSION-009`).

Mission State and Robot Operational State alone cannot guarantee these rules. In particular, an `available` Robot could already be assigned to a different `pending` Cleaning Mission. Independent state-transition operations could also expose a half-started combination in which only the Cleaning Mission or only the Robot has changed.

The model therefore needs stable domain identity, a locally enforceable representation of the active association, and one coordinated start operation. It must provide these without introducing repository access, persistence concerns, a global Mission registry, or an aggregate ownership decision into the domain.

## Decision

### Identity-Bearing Domain Entities

Robot and Cleaning Mission are identity-bearing domain entities. Each Robot has one stable, opaque Robot Identity, and each Cleaning Mission has one stable, opaque Cleaning Mission Identity. These identities remain unchanged across domain state transitions.

Opaque identity means that domain behavior does not derive business meaning from the identity's representation. This decision does not select an identifier format, generation strategy, library, serialization, or persistence representation.

### Assignment at Creation

Every Cleaning Mission in the MVP is created in Mission State `pending` with exactly one Assigned Robot. An unassigned pending Cleaning Mission is not permitted.

The Cleaning Mission records its Assigned Robot identity. The Robot records at most one Current Active Mission identity. While the Cleaning Mission is active, these identities must be reciprocal. Because `pending` is an Active Mission state, a Robot already associated with an Active Mission cannot be assigned another Cleaning Mission at creation or later.

An Active Mission cannot be reassigned. Terminal Missions remain unmodifiable under `MISSION-007`.

An invalid or duplicate assignment produces one neutral Mission Assignment Rejection. It contains no reason taxonomy, creates no Incident, does not change a Cleaning Mission to `failed`, and leaves existing state and assignment information unchanged. Mission Assignment Rejection is distinct from Mission Start Rejection, which remains specific to starting a Cleaning Mission.

### Local Enforcement

The reciprocal identities provide the information needed to enforce `MISSION-004` when a Cleaning Mission is created or assigned. The Robot can determine locally whether it already records a Current Active Mission, and the focused domain operation can verify that the proposed Cleaning Mission and Robot identify each other.

No repository, persistence mechanism, registry, or global scan of Cleaning Missions is needed to evaluate this invariant. A design in which the Robot did not record its Current Active Mission would require authoritative knowledge of every Active Mission to exclude another assignment and would move a confirmed invariant outside the locally sufficient domain model.

### Coordinated Mutable Start

Starting a Cleaning Mission uses coordinated mutable domain entities. One focused domain operation evaluates every start precondition and verifies reciprocal identities before changing either entity. On success, it changes the same Cleaning Mission from `pending` to `running` and its Assigned Robot from `available` to `executing mission`, while preserving both identities.

Only this coordinated operation belongs to the normal public domain API for start. Independent operations capable of applying either half of the successful start transition are not public domain operations. This encapsulation is an API and architecture boundary; it is not a security mechanism against deliberate Python reflection or direct private-member access.

Coordinated mutation was selected over returning independently adoptable immutable replacements. Separate replacements would allow a caller to retain only one updated entity and expose the half-start states that `MISSION-003` prohibits. A wrapper containing both replacements would still require an additional adoption boundary. Coordinated mutation supplies the required all-or-neither domain outcome directly for the current MVP.

### Terminal Association

Successful completion clears the Robot's Current Active Mission identity as part of the coordinated completion outcome while the terminal Cleaning Mission retains its Assigned Robot identity (`MISSION-008`). Any other transition to a Terminal Mission must clear that association as part of the same domain outcome, so no Robot remains associated with that non-active Mission (`MISSION-016`). Cancellation therefore changes the Mission State and clears the association atomically without deciding the Robot's resulting Robot Operational State (`CONTROL-005`).

This association-clearing requirement does not decide the Robot Operational State after cancellation, handling of Collected Waste after cancellation, conditions for failure, the Robot Operational State following failure, or other deferred terminal-transition behavior.

### Domain Coordination Without Aggregate Ownership

The focused domain operation coordinates invariants and paired transitions involving a Cleaning Mission and Robot. This decision does not declare either entity an aggregate root, does not establish an aggregate boundary, does not state that Cleaning Mission owns Robot, and does not assign ownership of the Robot lifecycle to Cleaning Mission.

This decision also does not introduce a repository, persistence model, transaction mechanism, registry, domain event, framework, API, transport contract, DTO, or package layout.

## Consequences

### Positive

- Stable identities preserve domain continuity across state transitions.
- Reciprocal assignment makes `MISSION-004` locally enforceable from the participating domain entities, including while a Cleaning Mission is `pending`.
- The coordinated start operation prevents normal callers from producing invalid half-start states.
- Assignment rejection and start rejection remain neutral, distinct outcomes without reason taxonomies or Incident semantics.
- Completion and other terminal transitions cannot leave a Robot associated with a non-active Cleaning Mission.
- Domain enforcement remains independent of repositories, persistence, frameworks, and transport concerns.

### Negative or Trade-offs

- Robot and Cleaning Mission must maintain reciprocal association information while the Cleaning Mission is active.
- Coordinated mutable behavior requires careful precondition evaluation before mutation begins.
- Encapsulation prevents invalid use through the normal domain API but does not make Python private members a security boundary.
- Future persistence or concurrency requirements may require an application operation or transaction boundary, but none is selected by this decision.

## Rejected Alternatives

### Coordinator Without Robot-Side Active Mission Identity

Rejected because a coordinator receiving only one Cleaning Mission and Robot cannot prove that the Robot is not assigned to another pending Active Mission. It would require a complete global Mission collection, repository query, or registry, and a caller-supplied collection could be incomplete.

### Dedicated Active Assignment Domain Object

Rejected for the current MVP because a standalone assignment object would not prevent duplicate assignment objects unless it also became the exclusive consistency authority. That would add a new lifecycle and imply an aggregate-like boundary beyond what the current rules require.

### Domain-Wide Mission Registry or Roster

Rejected because it would introduce global domain knowledge and a broad consistency boundary solely to enforce an invariant that reciprocal local identity can enforce more directly.

### Boolean Active-Mission Marker on Robot

Rejected because a Boolean could block some duplicate assignments but could not identify the associated Cleaning Mission or verify reciprocal consistency.

### Independently Adoptable Immutable Replacements

Rejected because a caller could adopt only the changed Cleaning Mission or only the changed Robot, exposing a half-transition. Stable identity remains required, but immutable replacement is not required for the MVP.

## Deferred Decisions

- Identifier representation, format, generation strategy, and libraries.
- Persistence, repositories, storage mappings, and transaction mechanisms.
- Concrete classes, result types, exception types, method signatures, and package layout.
- Robot Operational State after cancellation.
- Handling of Collected Waste after cancellation.
- Conditions and exact transition policy for Mission State `failed`.
- Robot Operational State and other lifecycle behavior after failure.
- Other terminal-transition lifecycle details beyond clearing the Current Active Mission association and retaining the Cleaning Mission's Assigned Robot identity.
- All product, domain, architecture, telemetry, and implementation decisions already deferred by the referenced documents and not resolved here.

## References

- `AGENTS.md`
- `docs/product/vision.md`
- `docs/product/mvp.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/domain-rules.md`
- `docs/architecture/overview.md`
- `docs/architecture/adr-0001-modular-monolith-and-hexagonal-architecture.md`
- `docs/architecture/adr-0002-python-tooling-and-project-layout.md`
- `backend/tests/acceptance/features/start_cleaning_mission.feature`
