# ReBot MVP

## MVP Objective

The MVP must demonstrate one complete cleaning mission in a two-dimensional grid-based simulation and a web control center for the operator. The operator starts and observes the mission as one robot classifies, routes to, collects, and deposits processable waste while avoiding static obstacles, consuming battery, and reporting relevant incidents and real-time telemetry.

## Primary Actor

The primary actor is the **Operator**, who starts, pauses, resumes, or cancels a mission and observes its progress, telemetry, final result, and incidents.

## Supporting System Participants

- **Robot:** The simulated autonomous participant that moves, consumes battery, handles waste, and reports its state.
- **Simulated environment:** The two-dimensional grid-based environment containing positions, static obstacles, waste items, and compatible collection points.

## Core End-to-End Journey

1. The operator starts a cleaning mission.
2. An available robot begins the mission.
3. The robot selects a detected waste item as a classification candidate.
4. The waste is classified deterministically as plastic, paper, metal, glass, organic, or `unknown`.
5. The system determines whether the item can proceed under the currently agreed handling rules.
6. Only an item that can proceed is targeted for collection.
7. A valid route to the targeted item is calculated while avoiding static obstacles.
8. The robot moves to the waste and consumes battery.
9. The robot collects the waste.
10. It calculates a route to a compatible collection point.
11. The robot transports the waste and deposits it at the collection point.
12. It continues with remaining waste that can proceed under the agreed handling rules.
13. Waste that is unreachable is reported as an incident without automatically crashing the mission.
14. The mission completion condition is evaluated after waste that can proceed has been deposited and required incidents have been reported, according to the agreed handling rules.

## Functional Scope

- One simulated robot.
- One two-dimensional grid-based environment.
- Static obstacles.
- Multiple waste items.
- Deterministic classification into the known categories plastic, paper, metal, glass, and organic, with `unknown` as an allowed classification outcome.
- Compatible collection points.
- Route calculation that avoids blocked positions.
- Movement and battery consumption.
- Collection and deposit of one waste item at a time.
- Mission start, pause, resume, and cancel.
- Mission progress and final result.
- A web control center through which the operator starts, pauses, resumes, and cancels missions and observes the simulated environment, robot position, battery, robot and mission states, mission progress, waste lifecycle changes, incidents, and the final mission result.
- Real-time telemetry supplying information to the MVP web control center.
- Incident reporting for unreachable waste and insufficient battery.

## Mission Controls

The operator can start a mission when the robot is available, pause a running mission, resume a paused mission, and cancel a non-terminal mission. A terminal mission cannot be modified.

## Waste Lifecycle

Waste progresses through these lifecycle states as applicable:

`detected` -> `classified` -> `targeted` -> `collected` -> `deposited`

Waste that cannot be reached is marked `unreachable` and generates an incident. Deposited or unreachable waste is not processed again.

The known waste categories are plastic, paper, metal, glass, and organic. `unknown` remains an allowed deterministic classification outcome. Normal collection and deposit behavior applies only when a compatible collection point exists under an agreed handling policy. This MVP does not define the handling policy for `unknown` waste.

## Robot Operational States

- `available`: ready to begin a mission.
- `executing mission`: actively carrying out mission work.
- `paused`: temporarily not progressing because the mission is paused.
- `charging`: an operational state whose transition and behavior remain intentionally deferred.
- `out of service`: unavailable for mission execution.

## Mission States

- `pending`: created but not running.
- `running`: actively executing.
- `paused`: temporarily suspended by the operator.
- `completed`: the agreed processable waste has been deposited and required incidents have been reported according to the agreed handling rules.
- `cancelled`: stopped by the operator before completion.
- `failed`: unable to continue because of an unrecoverable mission condition.

## Business Rules Included in the MVP

- Only an available robot can start a mission.
- A robot cannot have two active missions.
- A robot can carry only one waste item.
- A robot cannot move through blocked positions.
- Movement consumes battery.
- A robot cannot perform an action without sufficient battery.
- Waste can only be collected from the robot's current position.
- Waste can only be deposited at the robot's current position.
- A collection point must accept the waste category before normal deposit can occur under the agreed handling rules.
- Deposited waste cannot be collected again.
- A terminal mission cannot be modified.
- Unreachable waste creates an incident.
- One unreachable item does not automatically stop all remaining work.
- Relevant state changes produce telemetry.

## Observable Telemetry

The MVP web control center displays the simulated environment and lets the operator start, pause, resume, and cancel missions. Real-time telemetry supplies the robot's position, battery, operational state, mission state, mission progress, waste lifecycle changes, incidents, and final mission result, including relevant state changes such as unreachable waste and insufficient battery conditions.

## Success Criteria

- The operator can start a mission with an available robot in a defined grid-based environment.
- The robot can complete collection and compatible deposit for reachable waste while avoiding static obstacles.
- Movement visibly affects the robot's battery state.
- The operator can pause, resume, and cancel missions within the stated mission-state rules.
- Unreachable waste is reported as an incident and does not automatically prevent remaining reachable work from continuing.
- Insufficient battery is reported as an incident rather than being silently ignored.
- The operator can observe the simulated environment, position, battery, operational state, mission state, mission progress, waste lifecycle, incidents, and final result through the MVP web control center and its telemetry.

## Out of Scope

- Physical hardware.
- ROS 2 integration.
- Real sensors or cameras.
- Computer vision.
- Machine-learning classification.
- Multiple robots.
- Moving obstacles.
- Geographic maps.
- User accounts, authentication, or roles.
- Mobile applications.
- Advanced UI functionality beyond the MVP web control center.
- Advanced autonomous charging.
- Multi-robot or global route optimization.
- Production deployment and physical-safety certification.

## Known Decisions Intentionally Deferred

- Exact battery-consumption values.
- Minimum safe battery thresholds.
- Charging behavior.
- Collection-point capacity.
- Waste-classification confidence.
- Handling policy for `unknown` waste.
- Exact route-planning algorithm.
- Detailed control-center visual design.
- Physical robot integration.
- Exact persistence and deployment decisions.

No deferred decision is assigned a value by this MVP definition.

## MVP Completion Definition

The MVP is complete when one demonstrable end-to-end scenario using known waste categories can be run from mission start through completion in the web control center: the robot handles reachable waste, deposits it at compatible collection points, reports position, battery, state, progress, and final result through real-time telemetry, and handles at least one unreachable-waste incident without automatically crashing the mission. The scenario must also demonstrate the applicable mission controls and battery consumption without relying on physical hardware, unresolved `unknown`-waste handling, or other future capabilities.
