# ReBot MVP

## MVP Objective

The MVP must demonstrate one complete cleaning mission in a two-dimensional grid-based simulation and a web control center for the operator. The operator starts and observes the mission as one robot classifies, routes to, collects, and deposits reachable Processable Waste or marks Processable Waste `unreachable` while avoiding static obstacles, consuming battery, and reporting relevant incidents and real-time telemetry.

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
5. The system determines whether the item is Processable Waste under the currently agreed handling rules.
6. The system determines whether a valid route to the Processable Waste Item exists while avoiding static obstacles.
7. If a Route exists, the Processable Waste Item becomes targeted for collection.
8. If no Route exists, the Processable Waste Item becomes `unreachable` and its corresponding Required Incident is reported; it does not become targeted during the current Mission.
9. For a targeted item, the robot moves to the waste and consumes battery.
10. The robot collects the waste.
11. It calculates a route to a compatible collection point.
12. The robot transports the waste and deposits it at the collection point.
13. It continues with remaining Processable Waste Items, resolving each as deposited or unreachable.
14. When every Processable Waste Item for the current Mission is deposited or unreachable with its corresponding Required Incident reported, and every Required Incident has been reported, the Mission becomes `completed`.

## Functional Scope

- One simulated robot.
- One two-dimensional grid-based environment.
- Static obstacles.
- Multiple waste items.
- Deterministic classification into the MVP Processable Waste Categories plastic, paper, metal, glass, and organic, with `unknown` as an allowed classification outcome that is currently non-processable.
- Compatible collection points.
- Route calculation that avoids blocked positions.
- Movement along an already validated Route, with each valid orthogonal step consuming exactly one Battery Level percentage point.
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

Waste that cannot be reached is marked `unreachable` and generates a Required Incident. It remains Processable Waste and is not targeted, collected, or deposited during the current Mission. Whether it is reconsidered in a future Mission remains unspecified.

The MVP Processable Waste Categories are plastic, paper, metal, glass, and organic. `unknown` remains an allowed deterministic classification outcome but is currently non-processable under the MVP policy. Normal collection and deposit behavior applies only when a compatible collection point exists under an agreed handling policy. Future Unknown Waste handling remains deferred.

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
- `completed`: every Processable Waste Item for the current Mission has either been deposited at a Compatible Collection Point or marked `unreachable` with its corresponding Required Incident reported, and every Required Incident has been reported.
- `cancelled`: stopped by the operator before completion.
- `failed`: unable to continue because of an unrecoverable mission condition.

## Business Rules Included in the MVP

- Only an available robot can start a mission.
- A robot cannot have two active missions.
- A robot can carry only one waste item.
- A robot cannot move through blocked positions.
- One valid orthogonal movement step requires at least `1%` Battery Level and atomically changes the Robot's Position to the next Route Position while consuming exactly one percentage point.
- Collection requires at least `1%` Battery Level and consumes no Battery Level in the current MVP.
- At `0%` Battery Level, an attempted movement step does not begin and leaves Robot Position and Battery Level unchanged; an attempted collection does not begin and leaves the participating Robot and Waste Item unchanged. Either attempt creates a Required Incident with the canonical concern `insufficient battery`.
- A robot cannot perform an action without sufficient Battery Level for that action; concrete sufficiency and consumption for actions other than movement and collection remain deferred.
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
- Each Processable Waste Item finishes the current Mission as either deposited at a Compatible Collection Point or `unreachable`; every unreachable item has its corresponding Required Incident reported, after which the Mission can become `completed`.
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

- Battery Level sufficiency and consumption for actions other than movement and collection, including deposit.
- Battery degradation, health, voltage, capacity units, and time-based consumption.
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

The MVP is complete when one demonstrable end-to-end scenario using known waste categories can be run from mission start through completion in the web control center: each Processable Waste Item finishes the current Mission as either deposited at a Compatible Collection Point or `unreachable`, every unreachable item has its corresponding Required Incident reported, and the Mission becomes `completed` with the assigned Robot becoming `available`. The robot reports position, battery, state, progress, and final result through real-time telemetry, and the scenario demonstrates at least one unreachable-waste incident without automatically crashing the mission. It does not rely on physical hardware, future Unknown Waste handling, or other future capabilities.
