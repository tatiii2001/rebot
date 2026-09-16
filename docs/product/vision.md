# ReBot Product Vision

## Product Summary

ReBot is a software-first simulator for an autonomous waste-collection robot. It models a robot exploring a two-dimensional environment, detecting and classifying waste, planning valid routes around static obstacles, collecting one item at a time, and depositing each item at a compatible collection point. In the MVP, an operator observes and controls missions through a web control center.

## Problem and Opportunity

Autonomous waste collection combines navigation, resource constraints, object handling, and operational decisions in one observable system. ReBot provides a credible, bounded setting in which these behaviors can be explored and demonstrated without requiring physical hardware. The opportunity is to make autonomous behavior understandable to the person supervising a mission, rather than presenting it as an opaque result.

## Product Purpose

The product exists to demonstrate a coherent end-to-end waste-collection mission in simulation. It should show how the robot and its environment participate in system behavior, how the mission responds to constraints and incidents, and what is happening at each significant step.

## Primary User

The primary user is the operator using the control center to start, observe, pause, resume, or cancel a mission and to understand its progress and incidents. The robot and the simulated environment participate in system behavior, but they are not human users.

## Core Value

ReBot gives an operator a transparent view of autonomous waste collection: what the robot is doing, why its mission progresses or encounters an incident, and whether waste has been handled correctly. The initial goal is a credible, demonstrable simulation, not a claim of production-ready physical robotics.

## Product Principles

- **Observable autonomy:** Robot movement, position, state changes, progress, and incidents should be understandable through the product.
- **Simulation first:** The initial product focuses on useful simulated behavior before considering physical integration.
- **Deterministic behavior:** The same defined situation should support repeatable observation and explanation.
- **Honest scope:** Current commitments must remain distinct from long-term possibilities and must not imply unsupported environmental impact.
- **Sustainable engineering:** The project should demonstrate maintainable, testable software and professional practices, including Hexagonal Architecture, Clean Architecture, Domain-Driven Design, TDD, BDD, and SOLID principles.

## Long-term Direction

ReBot may eventually support replaceable adapters for capabilities such as real sensors, hardware, ROS 2, computer vision, or machine-learning classification. These are future possibilities, not current product commitments. The product direction is to preserve the observable mission model while allowing such possibilities to be considered separately from the simulator.

## Portfolio and Learning Goals

ReBot is intended to be a public portfolio project that demonstrates disciplined product development across Python and TypeScript. Learning Python is part of the project goal, alongside practicing clear domain modeling, maintainable design, and testable delivery. ReBot is not presented as a tutorial project.

## Product Success Indicators

- A visitor to the public repository can understand the product's purpose and current boundaries.
- An operator can observe a complete simulated cleaning mission and its meaningful state changes.
- The operator can observe robot movement, position, battery, operational and mission states, progress, waste lifecycle changes, incidents, and the final mission result.
- The simulator demonstrates a coherent mission without overstating readiness for physical deployment.
- The project provides credible evidence of sustainable, maintainable, and testable software-engineering practice.

## Explicit Non-Goals for the Current Stage

- Building or operating a physical robot.
- Integrating ROS 2, real sensors, cameras, computer vision, or machine-learning models.
- Claiming production readiness, physical-safety certification, or measured environmental impact.
- Supporting multiple robots, moving obstacles, geographic maps, or advanced autonomous charging.
- Defining user accounts, authentication, roles, mobile applications, advanced control-center functionality, or production deployment.
