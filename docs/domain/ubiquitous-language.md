# ReBot Ubiquitous Language

## Purpose and Usage

This document defines the canonical domain vocabulary for ReBot. Product documentation, BDD scenarios, tests, code, and user-facing text must use these terms consistently. The definitions describe the product domain rather than any implementation. Ordinary explanatory language remains acceptable when it does not replace or blur a canonical term.

## Core Actors and Participants

### Operator

The human actor who starts, observes, pauses, resumes, or cancels a Cleaning Mission through the Control Center and interprets its progress, incidents, and result.

### Robot

The simulated autonomous participant that moves within the Simulated Environment, consumes battery, handles Waste Items, and reports its state. A Robot is a system participant, not a human user.

### Simulated Environment

The complete two-dimensional, grid-based simulation space containing Positions, static Obstacles, Waste Items, Collection Points, and the Robot. The Simulated Environment is a system participant, not a human user.

### Control Center

The MVP web-based product interface through which the Operator controls Cleaning Missions and observes the Simulated Environment, Robot, mission progress, waste lifecycle, incidents, telemetry, and final result.

## Mission Concepts

### Cleaning Mission

The coordinated simulated effort in which one Robot classifies, routes to, collects, and deposits Waste Items that can proceed under agreed handling rules, while reporting progress and incidents.

### Cleaning Mission Identity

The stable, opaque identity of one Cleaning Mission. It remains the same throughout that Cleaning Mission's state transitions. Its representation and generation strategy are not domain-language concerns.

### Assigned Robot

The one Robot designated when a Cleaning Mission is created to participate in that Cleaning Mission. The Cleaning Mission records the Robot Identity of its Assigned Robot. An Active Mission cannot be reassigned, and a Terminal Mission cannot be modified.

### Mission State

The current stage of a Cleaning Mission: `pending`, `running`, `paused`, `completed`, `cancelled`, or `failed`.

### Active Mission

A Cleaning Mission whose Mission State is `pending`, `running`, or `paused`.

### Terminal Mission

A Cleaning Mission whose Mission State is `completed`, `cancelled`, or `failed`. A Terminal Mission cannot be modified.

### Mission Start Rejection

The neutral domain outcome when a confirmed start precondition is unsatisfied. A Mission Start Rejection leaves the Cleaning Mission's Mission State and its assigned Robot's Robot Operational State unchanged, does not identify a specific reason, and is neither an Incident nor a Mission State.

### Mission Assignment Rejection

The neutral domain outcome when creating or assigning a Cleaning Mission would violate a confirmed assignment rule. A Mission Assignment Rejection leaves existing Cleaning Mission and Robot state and assignment information unchanged, does not identify a specific reason, creates no Incident, and does not change a Cleaning Mission's Mission State to `failed`. It is distinct from a Mission Start Rejection.

### Mission Progress

Observable information about the advancement of a Cleaning Mission. It may reflect handled Waste Items and Incidents required by confirmed rules. Its exact calculation and presentation remain unresolved.

### Mission Result

The final observable outcome of a Cleaning Mission, including its terminal state and the resulting waste-handling outcomes and incident information. For a `completed` Mission, each Processable Waste Item for the current Mission has either been deposited at a Compatible Collection Point or marked `unreachable` with its corresponding Required Incident reported, and every Required Incident has been reported. Deposited and unreachable are distinct outcomes; an unreachable Waste Item remains Processable Waste and is not collected or deposited during the current Mission. Whether it is reconsidered in a future Mission is unspecified.

## Robot Concepts

### Robot Identity

The stable, opaque identity of one Robot. It remains the same throughout that Robot's operational-state transitions. Its representation and generation strategy are not domain-language concerns.

### Current Active Mission

The optional Cleaning Mission Identity recorded by a Robot for the one Active Mission with which it is currently associated. While that Cleaning Mission is active, its Assigned Robot identity and the Robot's Current Active Mission identity are reciprocal. A Robot records no Current Active Mission after the associated Cleaning Mission becomes terminal.

### Battery Level

The Robot's remaining battery expressed as an integer percentage from `0` through `100`, inclusive. A Battery Level of `0%` means that no energy is available for an action requiring positive Battery Level. One valid orthogonal movement step requires at least `1%` and consumes exactly one percentage point. Collection requires at least `1%` but does not consume Battery Level in the current MVP. Battery Level never becomes negative. Sufficiency and consumption for other actions remain unresolved.

### Robot Operational State

The Robot's current operational condition: `available`, `executing mission`, `paused`, `charging`, or `out of service`.

## Environment and Navigation Concepts

### Position

A single location belonging to the finite grid of one Simulated Environment. The Robot, Waste Items, Obstacles, and Collection Points occupy Positions relevant to movement and handling.

### Obstacle

A static feature that blocks its Position and through which the Robot cannot move.

### Route

A non-empty ordered sequence of Positions in the finite Simulated Environment grid used by the Robot to reach a destination. The first Position is the route origin, and the last Position is the route destination. Every Position is inside the Simulated Environment boundaries and is not occupied by a static Obstacle. Consecutive Positions are orthogonally adjacent by one horizontal or vertical grid step; diagonal movement is not allowed in the MVP. The Robot follows the sequence in order. The exact Route-planning algorithm remains unresolved.

## Waste-Management Concepts

### Classification Candidate

A detected Waste Item selected for classification, before its Waste Category and processability are known.

### Waste Item

A discrete item in the Simulated Environment that may progress through the waste lifecycle.

### Waste Category

The deterministic classification result assigned to a Waste Item: a Known Waste Category or `unknown`.

### Known Waste Category

One of the agreed categories: `plastic`, `paper`, `metal`, `glass`, or `organic`.

### Unknown Waste

A Waste Item whose classification result is `unknown`. It is not Processable Waste under the current MVP rule; its future handling policy remains unresolved.

### Processable Waste

A Waste Item deterministically classified as `plastic`, `paper`, `metal`, `glass`, or `organic` under the current MVP handling rule. This MVP-specific term identifies Waste Items that may be targeted, collected, and deposited, or may become unreachable when no Route exists; it is not a universal real-world claim about waste. Unknown Waste is not Processable Waste under the current MVP policy, and future Unknown Waste handling remains unspecified.

### Targeted Waste

Processable Waste selected as the Robot's current collection target.

### Collected Waste

A Waste Item whose lifecycle state changed from `targeted` to `collected` through successful collection and that is currently carried by the Robot. The Robot can carry at most one such item.

### Deposited Waste

A Waste Item successfully placed at a Compatible Collection Point and no longer carried by the Robot.

### Unreachable Waste

A Processable Waste Item for which no Route satisfying the minimum Route semantics exists from the Robot's current Position to the Waste Item's Position. It is marked `unreachable`, produces a Required Incident, is not targeted, collected, or deposited during the current Cleaning Mission, and does not prevent evaluation of other remaining Processable Waste Items.

### Collection Point

A designated Position where the Robot may deposit an accepted Waste Item.

### Compatible Collection Point

A Collection Point that accepts the applicable Waste Category under agreed handling rules.

## State Terminology

### Robot Operational States

- `available`: ready to begin a Cleaning Mission.
- `executing mission`: actively carrying out mission work.
- `paused`: temporarily not progressing because the Cleaning Mission is paused.
- `charging`: an operational state whose transitions and behavior remain unresolved.
- `out of service`: unavailable for mission execution.

### Mission States

- `pending`: created but not running.
- `running`: actively executing.
- `paused`: temporarily suspended by the Operator.
- `completed`: every Processable Waste Item for the current Mission has either been deposited at a Compatible Collection Point or marked `unreachable` with its corresponding Required Incident reported, and every Required Incident has been reported.
- `cancelled`: stopped by the Operator before completion.
- `failed`: unable to continue because of an unrecoverable mission condition.

The Active Mission states are `pending`, `running`, and `paused`. The Terminal Mission states are `completed`, `cancelled`, and `failed`. Terminal Missions cannot be modified.

### Waste Lifecycle States

- `detected`: identified as a Waste Item in the Simulated Environment.
- `classified`: assigned a Waste Category.
- `targeted`: selected for collection after processability is established.
- `collected`: picked up while the Robot occupies the Waste Item's Position and carried by the Robot.
- `deposited`: placed at a Compatible Collection Point.
- `unreachable`: no Route satisfying the minimum Route semantics exists from the Robot's current Position to the Processable Waste Item's Position, so the item is not targeted, collected, or deposited during the current Cleaning Mission.

The documented normal progression is `detected` to `classified` to `targeted` to `collected` to `deposited`. After classification establishes that an item is Processable Waste, `unreachable` is an alternative to `targeted` when no Route to that item exists. No additional lifecycle state is implied.

## Telemetry and Incident Concepts

### Telemetry

Observable information supplied to the MVP Control Center. It includes the Simulated Environment, Robot Position, Battery Level, Robot Operational State, Mission State, Mission Progress, waste lifecycle changes, Incident occurrence and reporting, and Mission Result. Telemetry formatting, filtering, emission frequency, transport, delivery, serialization, and persistence are application or infrastructure concerns.

### Incident

A condition relevant to mission execution whose occurrence is recorded and reported to the Operator. Unreachable Waste and insufficient Battery Level for an attempted action are currently confirmed conditions that produce Incidents. The canonical concern for an Incident caused by insufficient Battery Level is `insufficient battery`. Recording an Incident occurrence and later reporting it are distinct requirements; neither defines Incident lifecycle states.

### Required Incident

An Incident that a confirmed rule requires to be created and that must be reported to the Operator when its documented triggering condition occurs. Currently confirmed triggering conditions are Unreachable Waste and insufficient Battery Level for an attempted action. A created Required Incident remains available for the application to report; the technical reporting mechanism is not a domain-language concern. A Required Incident has no lifecycle states.

## Preferred and Discouraged Terminology

The preferred terms below are canonical. Alternatives may appear in ordinary explanations when their meaning is clear, but they must not be used interchangeably as domain names.

| Prefer | Discourage as a canonical term | Guidance |
| --- | --- | --- |
| Waste Item | trash, garbage, rubbish, object | Use Waste Item for an item handled through the waste lifecycle. |
| Collection Point | bin, container | Use Collection Point for the designated deposit destination. |
| Cleaning Mission | job, task | Use Cleaning Mission for the end-to-end mission. |
| Operator | user, administrator, driver | Use Operator for the primary human actor. |
| Control Center | dashboard, panel, console | Use Control Center for the MVP web interface. |
| Simulated Environment | map, world | Use Simulated Environment for the complete simulation space. |

## Intentionally Unresolved Terms or Policies

The vocabulary does not resolve the following matters:

- The future handling policy for Unknown Waste and how a future policy could affect completion. Under the current MVP rule, Unknown Waste is not Processable Waste.
- Battery Level sufficiency and consumption for actions other than movement and collection, including deposit.
- Battery degradation, health, voltage, capacity units, and time-based consumption.
- The Mission State after insufficient Battery Level prevents an action.
- Transitions into or out of `charging` and behavior while charging.
- Collection Point capacity.
- Classification confidence.
- The exact Route-planning algorithm and dynamic-Obstacle behavior.
- What happens when a Collection Point cannot be reached, including whether the Unreachable Waste concept applies.
- Completion effects of any future Incident types that are not Required Incidents under current rules.
- Incident identity, severity, lifecycle, persistence, transport, filtering, delivery, and the technical reporting mechanism.
- The exact calculation and presentation of Mission Progress.
- Telemetry formatting, filtering, emission frequency, transport, delivery, serialization, and persistence.
- Handling of Collected Waste after cancellation.
- The Robot Operational State after cancellation.
- Which conditions cause the Mission State to become `failed`.

The current MVP rule is that Unreachable Waste is not reconsidered during the same Cleaning Mission. A later product decision could change that rule; no such change is currently defined.
