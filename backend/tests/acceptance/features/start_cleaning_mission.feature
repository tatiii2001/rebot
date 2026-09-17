Feature: Start a Cleaning Mission
  A successful start changes the Cleaning Mission and its Assigned Robot
  as one atomic outcome while preserving their identities and reciprocal assignment.

  # MISSION-002, MISSION-003, MISSION-010, MISSION-012, ROBOT-008
  Scenario: Start a pending Cleaning Mission with an available Assigned Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has exactly one Assigned Robot with Robot Operational State "available"
    And the Cleaning Mission records the Robot Identity of its Assigned Robot
    And the Assigned Robot records the Cleaning Mission Identity as its Current Active Mission
    And the Cleaning Mission and Assigned Robot have a reciprocal active assignment
    When the Operator requests to start the Cleaning Mission
    Then the Cleaning Mission has Mission State "running"
    And the Assigned Robot has Robot Operational State "executing mission"
    And the Cleaning Mission retains its Cleaning Mission Identity
    And the Assigned Robot retains its Robot Identity
    And the Cleaning Mission retains its Assigned Robot
    And the Cleaning Mission and Assigned Robot retain their reciprocal active assignment

  # MISSION-002, MISSION-003, MISSION-009, MISSION-010,
  # MISSION-012, ROBOT-008
  Scenario: Repeat a start after the Cleaning Mission has started successfully
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has exactly one Assigned Robot with Robot Operational State "available"
    And the Cleaning Mission records the Robot Identity of its Assigned Robot
    And the Assigned Robot records the Cleaning Mission Identity as its Current Active Mission
    And the Cleaning Mission and Assigned Robot have a reciprocal active assignment
    When the Operator requests to start the Cleaning Mission
    And the Operator requests to start the Cleaning Mission again
    Then the second start produces one neutral Mission Start Rejection
    And the Cleaning Mission has Mission State "running"
    And the Assigned Robot has Robot Operational State "executing mission"
    And the Cleaning Mission retains its Cleaning Mission Identity
    And the Assigned Robot retains its Robot Identity
    And the Cleaning Mission retains its Assigned Robot
    And the Cleaning Mission and Assigned Robot retain their reciprocal active assignment

  # MISSION-002, MISSION-009, MISSION-010, MISSION-012,
  # ROBOT-006, ROBOT-008
  Scenario: Start a pending Cleaning Mission with a non-available Assigned Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has exactly one Assigned Robot with Robot Operational State "out of service"
    And the Cleaning Mission records the Robot Identity of its Assigned Robot
    And the Assigned Robot records the Cleaning Mission Identity as its Current Active Mission
    And the Cleaning Mission and Assigned Robot have a reciprocal active assignment
    When the Operator requests to start the Cleaning Mission
    Then the start produces one neutral Mission Start Rejection
    And the Cleaning Mission has Mission State "pending"
    And the Assigned Robot has Robot Operational State "out of service"
    And the Cleaning Mission retains its Cleaning Mission Identity
    And the Assigned Robot retains its Robot Identity
    And the Cleaning Mission retains its Assigned Robot
    And the Cleaning Mission and Assigned Robot retain their reciprocal active assignment
