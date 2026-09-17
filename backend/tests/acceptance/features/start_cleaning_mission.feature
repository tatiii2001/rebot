Feature: Start a Cleaning Mission
  A successful start changes the Cleaning Mission and its assigned Robot
  as one atomic outcome.

  # MISSION-002, MISSION-003
  Scenario: Start a pending Cleaning Mission with an available assigned Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has one assigned Robot with Robot Operational State "available"
    When the Operator requests to start the Cleaning Mission
    Then the Cleaning Mission has Mission State "running"
    And the assigned Robot has Robot Operational State "executing mission"

  # MISSION-002, MISSION-003, MISSION-009
  Scenario: Repeat a start after the Cleaning Mission has started successfully
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has one assigned Robot with Robot Operational State "available"
    When the Operator requests to start the Cleaning Mission
    And the Operator requests to start the Cleaning Mission again
    Then the second start produces a Mission Start Rejection
    And the Cleaning Mission has Mission State "running"
    And the assigned Robot has Robot Operational State "executing mission"

  # MISSION-002, MISSION-009, ROBOT-006
  Scenario: Start a pending Cleaning Mission with a non-available assigned Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has one assigned Robot with Robot Operational State "out of service"
    When the Operator requests to start the Cleaning Mission
    Then the start produces a Mission Start Rejection
    And the Cleaning Mission has Mission State "pending"
    And the assigned Robot has Robot Operational State "out of service"
