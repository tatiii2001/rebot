Feature: Create a Cleaning Mission
  A Cleaning Mission is created as pending with exactly one Assigned Robot,
  and the active assignment is reciprocal from creation.

  # MISSION-001, MISSION-004, MISSION-005, MISSION-010,
  # MISSION-011, MISSION-012, ROBOT-008, ROBOT-009
  Scenario: Create a Cleaning Mission with an available Robot
    Given an available Robot records no Current Active Mission
    When a Cleaning Mission is created with the Robot as its Assigned Robot
    Then exactly one Cleaning Mission is created
    And the Cleaning Mission has Mission State "pending"
    And the Cleaning Mission has exactly one Assigned Robot
    And the Cleaning Mission records the Robot Identity of its Assigned Robot
    And the Robot records the Cleaning Mission Identity as its Current Active Mission
    And the Cleaning Mission and Robot have a reciprocal active assignment

  # MISSION-004, MISSION-005, MISSION-012, MISSION-014, ROBOT-009
  Scenario: Reject another Active Mission for the same Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And its Assigned Robot has Robot Operational State "available"
    And the Cleaning Mission and Robot have a reciprocal active assignment
    When creation of another Cleaning Mission with the same Robot as its Assigned Robot is attempted
    Then one neutral Mission Assignment Rejection is produced
    And no second Cleaning Mission is created
    And the existing Cleaning Mission has Mission State "pending"
    And the Robot has Robot Operational State "available"
    And the existing Cleaning Mission retains its Assigned Robot
    And the Cleaning Mission and Robot retain their reciprocal active assignment
    And no Cleaning Mission transitions to Mission State "failed"

  # MISSION-012, MISSION-013, MISSION-014, ROBOT-009
  Scenario: Reject reassignment of an Active Mission to another Robot
    Given an existing Cleaning Mission has Mission State "pending"
    And its Assigned Robot has Robot Operational State "available"
    And the Cleaning Mission and its Assigned Robot have a reciprocal active assignment
    And another available Robot records no Current Active Mission
    When reassignment of the Cleaning Mission to the other Robot is attempted
    Then one neutral Mission Assignment Rejection is produced
    And the Cleaning Mission has Mission State "pending"
    And the original Assigned Robot has Robot Operational State "available"
    And the other Robot has Robot Operational State "available"
    And the Cleaning Mission retains its original Assigned Robot
    And the Cleaning Mission and its original Assigned Robot retain their reciprocal active assignment
    And the other Robot records no Current Active Mission
    And no Incident is created
    And the Cleaning Mission does not transition to Mission State "failed"
