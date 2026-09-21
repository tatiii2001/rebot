# ReBot Domain Rules

## Purpose

This document records the latest approved domain invariants and behaviors for the ReBot MVP, separately from application coordination, product acceptance constraints, specification safeguards, telemetry delivery requirements, and intentionally deferred product decisions. The product vision and MVP definition remain authoritative for product scope.

## Rule-Status Convention

- **Confirmed invariant:** A condition that must always hold in the domain.
- **Confirmed behavior:** An agreed state change or outcome caused by a domain action or condition.
- **Deferred decision:** A product decision intentionally left unspecified and not treated as a confirmed rule.
- **Open question:** A neutral question that requires a future product decision.

Stable identifiers are assigned only to atomic confirmed domain invariants and confirmed domain behaviors. They are sequential within each rule category. Product acceptance constraints, product and application telemetry requirements, specification safeguards, application coordination, and deferred decisions do not receive domain-rule identifiers.

## Mission Rules

| ID | Status | Rule |
| --- | --- | --- |
| `MISSION-001` | Confirmed invariant | A new Cleaning Mission has Mission State `pending`. |
| `MISSION-002` | Confirmed invariant | A Cleaning Mission can start only when its Mission State is `pending`, its assigned Robot has Robot Operational State `available`, and the Cleaning Mission's Assigned Robot identity and the Robot's Current Active Mission identity are reciprocal. |
| `MISSION-003` | Confirmed behavior | After all start preconditions and reciprocal identities are validated before either entity is changed, a successful start uses one coordinated mutable domain operation to atomically change the Cleaning Mission from `pending` to `running` and its assigned Robot from `available` to `executing mission`; both identities remain unchanged. |
| `MISSION-004` | Confirmed invariant | A Robot cannot have more than one Active Mission. |
| `MISSION-005` | Confirmed invariant | The Active Mission states are exactly `pending`, `running`, and `paused`. |
| `MISSION-006` | Confirmed invariant | The Terminal Mission states are exactly `completed`, `cancelled`, and `failed`. |
| `MISSION-007` | Confirmed invariant | A Terminal Mission cannot be modified. |
| `MISSION-008` | Confirmed behavior | When every Processable Waste Item for the current Cleaning Mission has either been deposited at a Compatible Collection Point or been marked `unreachable` with its corresponding Required Incident reported, and every Required Incident has been reported, successful completion atomically changes a running Cleaning Mission to `completed`, changes its assigned Robot from `executing mission` to `available`, and clears that Robot's Current Active Mission identity. The terminal Cleaning Mission retains its Assigned Robot identity. A running Cleaning Mission cannot become `completed` otherwise. |
| `MISSION-009` | Confirmed behavior | When any start precondition in `MISSION-002` is unsatisfied, all start preconditions are evaluated before any state mutation and the start produces one neutral Mission Start Rejection. Neither state transition in `MISSION-003` occurs: the Cleaning Mission retains its previous Mission State and the assigned Robot retains its previous Robot Operational State. A Mission Start Rejection does not identify a specific reason, is not an Incident, and does not change the Mission State to `failed`. |
| `MISSION-010` | Confirmed invariant | A Cleaning Mission has one stable, opaque Cleaning Mission Identity that does not change during its state transitions. |
| `MISSION-011` | Confirmed invariant | Every Cleaning Mission has exactly one Assigned Robot identity from creation; an unassigned Cleaning Mission is not permitted in the MVP. |
| `MISSION-012` | Confirmed invariant | While a Cleaning Mission is active, its Assigned Robot identity and that Robot's Current Active Mission identity are reciprocal. |
| `MISSION-013` | Confirmed invariant | An Active Mission cannot be reassigned to another Robot. |
| `MISSION-014` | Confirmed behavior | When creating or assigning a Cleaning Mission would violate an assignment rule, the attempt produces one neutral Mission Assignment Rejection. Existing Cleaning Mission and Robot state and assignment information remain unchanged. A Mission Assignment Rejection does not identify a specific reason, creates no Incident, does not change a Cleaning Mission's Mission State to `failed`, and is distinct from a Mission Start Rejection. |
| `MISSION-015` | Confirmed invariant | A Robot cannot record a Terminal Mission as its Current Active Mission. |
| `MISSION-016` | Confirmed behavior | As part of any transition that makes a Cleaning Mission terminal, its assigned Robot's Current Active Mission identity is cleared while the terminal Cleaning Mission retains its Assigned Robot identity. |

The conditions and transition policy for Mission State `failed` remain deferred.

`MISSION-004` is enforced when a Cleaning Mission is created: `MISSION-001` makes the new Cleaning Mission `pending`, `MISSION-011` requires one Assigned Robot, `MISSION-012` requires reciprocal assignment while that Cleaning Mission is active, and `ROBOT-009` prevents the Robot from recording another Current Active Mission. Successful creation must leave the participating entities in that consistent state; a partially assigned Active Mission is invalid. No repository, registry, or global scan of Cleaning Missions is required to evaluate this local invariant.

Because `MISSION-003` spans a Cleaning Mission and its assigned Robot, its coordinated mutable domain operation is the normal public domain operation for start. Independent transitions that could expose a half-started state are not public domain operations. This encapsulation is an API and architecture boundary, not a security mechanism against deliberate language reflection or direct private-member access. The coordination does not declare an aggregate root, establish aggregate ownership, state that the Cleaning Mission owns the Robot lifecycle, or authorize application-layer business rules.

## Robot Rules

| ID | Status | Rule |
| --- | --- | --- |
| `ROBOT-001` | Confirmed invariant | A Robot in Robot Operational State `executing mission` is assigned to that Cleaning Mission. |
| `ROBOT-002` | Confirmed invariant | A Robot carries at most one Waste Item. |
| `ROBOT-003` | Confirmed invariant | A Robot in Robot Operational State `paused` cannot move. |
| `ROBOT-004` | Confirmed invariant | A Robot in Robot Operational State `paused` cannot collect a Waste Item. |
| `ROBOT-005` | Confirmed invariant | A Robot in Robot Operational State `paused` cannot deposit a Waste Item. |
| `ROBOT-006` | Confirmed invariant | A Robot in Robot Operational State `out of service` cannot start a Cleaning Mission. |
| `ROBOT-007` | Confirmed invariant | A Robot in Robot Operational State `out of service` cannot execute a Cleaning Mission. |
| `ROBOT-008` | Confirmed invariant | A Robot has one stable, opaque Robot Identity that does not change during its operational-state transitions. |
| `ROBOT-009` | Confirmed invariant | A Robot records at most one Current Active Mission identity. A Robot already associated with an Active Mission cannot be assigned another Active Mission. |

Transitions into or out of `charging` and behavior while charging are deferred decisions.

## Movement and Navigation Rules

| ID | Status | Rule |
| --- | --- | --- |
| `NAV-001` | Confirmed invariant | A Robot occupies exactly one Position at a time. |
| `NAV-002` | Confirmed invariant | A Position belongs to the finite grid of one Simulated Environment. |
| `NAV-003` | Confirmed invariant | A Route is a non-empty ordered sequence of Positions. |
| `NAV-004` | Confirmed invariant | The first Position in a Route is its origin. |
| `NAV-005` | Confirmed invariant | The last Position in a Route is its destination. |
| `NAV-006` | Confirmed invariant | Every Position in a Route is inside the Simulated Environment boundaries. |
| `NAV-007` | Confirmed invariant | A Route cannot include a Position occupied by a static Obstacle. |
| `NAV-008` | Confirmed invariant | Consecutive Positions in a Route are orthogonally adjacent by one horizontal or vertical grid step; diagonal movement is not allowed in the MVP. |
| `NAV-009` | Confirmed behavior | A Robot following an already validated Route attempts movement steps from its current Position to each next Position in order. Each successful step advances under `BATTERY-002`. |

Robot movement consumes Battery Level under `BATTERY-002`. The exact Route-planning algorithm, route selection, route cost, tie-breaking, and dynamic-Obstacle behavior remain deferred.

## Waste Classification and Lifecycle Rules

| ID | Status | Rule |
| --- | --- | --- |
| `WASTE-001` | Confirmed behavior | Selecting a detected Waste Item for classification makes it the Classification Candidate. This selection does not assign a Waste Category or establish processability. |
| `WASTE-002` | Confirmed behavior | Deterministic classification atomically assigns a Classification Candidate exactly one result (`plastic`, `paper`, `metal`, `glass`, `organic`, or `unknown`) and changes it from `detected` to `classified`. |
| `WASTE-003` | Confirmed behavior | Processability is evaluated after classification. |
| `WASTE-004` | Confirmed invariant | A Waste Item deterministically classified as `plastic`, `paper`, `metal`, `glass`, or `organic` is Processable Waste under the current MVP handling rule. |
| `WASTE-005` | Confirmed invariant | A Waste Item classified as `unknown` is not Processable Waste under the current MVP handling rule. |
| `WASTE-006` | Confirmed behavior | Targeting changes a Processable Waste Item from `classified` to `targeted`. |
| `WASTE-007` | Confirmed invariant | Along the documented normal progression `detected` -> `classified` -> `targeted` -> `collected` -> `deposited`, a Waste Item cannot transition to an earlier state. `unreachable` is an alternative to `targeted` after processability is established. |
| `WASTE-008` | Confirmed invariant | Deposited Waste cannot be collected again. |
| `WASTE-009` | Confirmed behavior | When no Route satisfying `NAV-003` through `NAV-008` exists from the Robot's current Position to a Processable Waste Item's Position, that Waste Item changes from `classified` to `unreachable`. |
| `WASTE-010` | Confirmed invariant | Unreachable Waste cannot be targeted, collected, or deposited during the current Cleaning Mission. |
| `WASTE-011` | Confirmed behavior | After a Processable Waste Item becomes `unreachable`, the Cleaning Mission continues by evaluating other remaining Processable Waste Items. |

The future handling policy for `unknown`, including whether a future policy makes it Processable Waste and how that would affect completion, remains deferred. No classification-confidence threshold is defined. Any future reconsideration policy for Unreachable Waste remains deferred. These processability rules are MVP handling rules, not universal real-world claims about waste.

## Collection and Deposit Rules

| ID | Status | Rule |
| --- | --- | --- |
| `WASTE-012` | Confirmed invariant | A Waste Item can be collected only when the Robot occupies the Waste Item's Position. |
| `WASTE-013` | Confirmed invariant | A Robot carrying a Waste Item cannot collect another Waste Item. |
| `WASTE-014` | Confirmed behavior | Subject to the collection Battery Level rules in `BATTERY-007` through `BATTERY-009`, successful collection atomically changes a Waste Item from `targeted` to `collected` and makes it the Waste Item carried by the Robot. |
| `WASTE-015` | Confirmed invariant | A Waste Item can be deposited only when the Robot occupies the Collection Point's Position. |
| `WASTE-016` | Confirmed invariant | A Waste Item can be deposited only at a Compatible Collection Point. |
| `WASTE-017` | Confirmed behavior | Successful deposit atomically changes the carried Waste Item from `collected` to `deposited` and removes it from the Robot. |

## Battery Rules

| ID | Status | Rule |
| --- | --- | --- |
| `BATTERY-001` | Confirmed invariant | Battery Level is an integer percentage from zero through one hundred, inclusive, and never becomes negative. A Battery Level of `0%` means that no energy is available for an action requiring positive Battery Level. |
| `BATTERY-002` | Confirmed behavior | One successful valid orthogonal movement step along an already validated Route atomically changes the Robot's current Position to the next Position in that Route and decreases Battery Level by exactly one percentage point. |
| `BATTERY-003` | Confirmed invariant | An action cannot begin when the Robot's Battery Level is insufficient for that action. Concrete sufficiency is defined for movement and collection only; sufficiency for other actions remains deferred. |
| `BATTERY-004` | Confirmed behavior | Insufficient Battery Level for an attempted action creates a Required Incident with the canonical concern `insufficient battery`. The Incident occurrence remains available for application reporting under `INCIDENT-002`. |
| `BATTERY-005` | Confirmed invariant | A movement step may begin only when the Robot's Battery Level is at least `1%`. |
| `BATTERY-006` | Confirmed behavior | When movement is attempted at `0%` Battery Level, the movement step does not begin, the Robot's Position and Battery Level remain unchanged, and the Required Incident is created under `BATTERY-004`. |
| `BATTERY-007` | Confirmed invariant | Collection may begin only when the Robot's Battery Level is at least `1%`. |
| `BATTERY-008` | Confirmed behavior | Successful collection consumes no Battery Level in the current MVP. |
| `BATTERY-009` | Confirmed behavior | When collection is attempted at `0%` Battery Level, collection does not begin, the Robot and Waste Item remain unchanged, and the Required Incident is created under `BATTERY-004`. |

These rules define concrete Battery Level sufficiency and consumption only for movement and collection. Battery Level sufficiency and consumption for deposit, classification, targeting, Mission control, charging, and other actions remain deferred. Battery degradation, health, voltage, capacity units, and time-based consumption are not defined. The Mission State after insufficient Battery Level prevents an action is also deferred. No autonomous charging behavior is assumed.

## Pause, Resume and Cancellation Rules

| ID | Status | Rule |
| --- | --- | --- |
| `CONTROL-001` | Confirmed behavior | Pausing a Cleaning Mission whose Mission State is `running` changes its Mission State to `paused`. |
| `CONTROL-002` | Confirmed behavior | Pausing a Cleaning Mission whose Mission State is `running` changes the Robot Operational State to `paused`. |
| `CONTROL-003` | Confirmed behavior | Resuming a Cleaning Mission whose Mission State is `paused` changes its Mission State to `running`. |
| `CONTROL-004` | Confirmed behavior | Resuming a Cleaning Mission whose Mission State is `paused` changes the Robot Operational State to `executing mission`. |
| `CONTROL-005` | Confirmed behavior | Cancelling a non-terminal Cleaning Mission atomically changes its Mission State to `cancelled` and clears its assigned Robot's Current Active Mission identity. The cancelled Cleaning Mission retains its Assigned Robot identity. This rule does not determine the Robot Operational State after cancellation. |
| `CONTROL-006` | Confirmed behavior | Cancelling a non-terminal Cleaning Mission stops further mission execution. |

Handling of Collected Waste after cancellation and the Robot Operational State after cancellation are deferred decisions.

## Incident Rules

| ID | Status | Rule |
| --- | --- | --- |
| `INCIDENT-001` | Confirmed behavior | A Processable Waste Item changing to `unreachable` under `WASTE-009` creates the corresponding Required Incident. |
| `INCIDENT-002` | Confirmed behavior | Every Required Incident created under `INCIDENT-001` or `BATTERY-004` is reported to the Operator after its occurrence has been recorded and made available for application reporting. |
| `INCIDENT-003` | Confirmed invariant | A Cleaning Mission cannot become `failed` solely because a Processable Waste Item is `unreachable`. |

Insufficient Battery Level creates a Required Incident under `BATTERY-004`; this section does not define that behavior again. Incident creation and reporting are distinct: `BATTERY-004` owns creation and availability of the occurrence, while `INCIDENT-002` requires its later reporting. The technical reporting mechanism remains deferred. The `failed` Mission State remains documented, but its conditions and exact transition policy are deferred. No Incident lifecycle is defined. Completion effects of future Incident types that are not Required Incidents under current rules remain deferred.

## Mission Completion Rules

The authoritative completion condition and its atomic Mission and Robot transitions are defined by `MISSION-008`. Under `WASTE-005`, Unknown Waste is not Processable Waste for the current MVP; its future handling policy must not be inferred from the completion rule.

## Observability Inventory

This is a product and application visibility inventory. It does not introduce domain events, invariants, lifecycle states, or delivery guarantees. Each observable change below originates from the cited authoritative numbered domain rule:

- Mission start and the assigned Robot's transition are observable under `MISSION-003`.
- Mission completion and the assigned Robot's release are observable under `MISSION-008`.
- Mission pause, resume, and cancellation changes are observable under `CONTROL-001` through `CONTROL-006`.
- Robot Position changes while following a Route are observable under `NAV-009`.
- Battery Level changes caused by movement are observable under `BATTERY-002`.
- Waste selection, classification, processability, and targeting changes are observable under `WASTE-001` through `WASTE-006`.
- Waste lifecycle changes for unreachable, collected, and deposited Waste Items are observable under `WASTE-009`, `WASTE-014`, and `WASTE-017`.
- Required Incident creation is observable under `INCIDENT-001` and `BATTERY-004`, and Required Incident reporting is observable under `INCIDENT-002`.

## Product and Application Telemetry Requirements

The MVP Control Center receives observable telemetry. Observable information includes the Simulated Environment, Robot Position, Battery Level, Robot Operational State, Mission State, Mission Progress, waste lifecycle changes, Incident occurrence and reporting, and Mission Result. This does not require the entire Simulated Environment to be emitted on every telemetry event.

Telemetry formatting, filtering, emission frequency, transport, delivery, serialization, and persistence are application or infrastructure concerns. They remain deferred and are not numbered domain rules.

## MVP Demonstration Constraint

The demonstrable MVP completion scenario uses Known Waste Categories. This is a product acceptance and demonstration constraint, not a domain invariant.

## Application Coordination Versus Domain Behavior

Robot and Cleaning Mission are identity-bearing domain entities. Domain objects enforce domain invariants and state changes. Application use cases coordinate participating domain behavior and the delivery of observable information. Infrastructure performs technical interaction and persistence. The focused domain coordination required for assignment and paired state transitions does not establish aggregate ownership or declare an aggregate boundary. This distinction does not assign value objects, bounded contexts, concrete classes, frameworks, protocols, modules, or file paths.

## Intentionally Deferred Domain Decisions

- Future Unknown Waste handling policy and the effect of any future policy on completion. Under the current MVP rule, Unknown Waste is not Processable Waste.
- Battery Level sufficiency and consumption for actions other than movement and collection, including deposit, classification, targeting, Mission control, and charging.
- Battery degradation, health, voltage, capacity units, and time-based consumption.
- Mission State after insufficient Battery Level prevents an action.
- Charging transitions and behavior.
- Collection Point capacity.
- Classification confidence.
- Exact Route-planning algorithm.
- Route cost and tie-breaking policy.
- Dynamic Obstacle behavior.
- Behavior when a Collection Point cannot be reached.
- Handling of Collected Waste after cancellation.
- Robot Operational State after cancellation.
- Conditions and exact transition policy for Mission State `failed`.
- Robot Operational State, carried-Waste behavior, and other lifecycle effects of terminal transitions beyond the confirmed association clearing rule in `MISSION-016`.
- Future reconsideration policy for Unreachable Waste.
- Completion effects of future Incident types that are not Required Incidents under current rules.
- Incident identity, severity, lifecycle, persistence, transport, filtering, delivery, and the technical reporting mechanism.
- Exact Mission Progress calculation and presentation.
- Telemetry formatting, filtering, emission frequency, transport, delivery, serialization, and persistence.

The current-Mission behavior for Unreachable Waste is defined authoritatively by `WASTE-010` and `WASTE-011`; no future reconsideration policy is currently defined.

## Questions Requiring Future Product Decisions

- How should Unknown Waste be handled under a future policy, and how would that policy affect completion?
- What Battery Level sufficiency and consumption rules apply to actions other than movement and collection, including deposit?
- Should battery degradation, health, voltage, capacity units, or time-based consumption ever enter product scope?
- What Mission State follows when insufficient Battery Level prevents an action?
- Which transitions enter and leave `charging`, and what occurs while the Robot is charging?
- Does a Collection Point have a capacity, and what happens when that capacity is reached?
- Is classification confidence represented, and if so, how does it affect classification or processability?
- Which exact algorithm plans a Route?
- How are Route cost and tie-breaking determined?
- How would dynamic Obstacles affect Routes and movement if they enter product scope?
- What happens when a Collection Point cannot be reached?
- What happens to Collected Waste when the Operator cancels a Cleaning Mission?
- What Robot Operational State follows cancellation?
- Which conditions cause the Mission State to become `failed`?
- Can a future product decision allow Unreachable Waste to be reconsidered during the same Cleaning Mission, and under what conditions?
- How would future Incident types that are not Required Incidents under current rules affect completion?
- Does an Incident need identity, severity, lifecycle, persistence, filtering, or other currently deferred characteristics?
- How is Mission Progress calculated and presented?
- How is telemetry formatted and filtered, how frequently is it emitted, and how is it transported, delivered, serialized, and persisted?
