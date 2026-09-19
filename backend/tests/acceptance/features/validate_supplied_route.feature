Feature: Validate a supplied Route
  A supplied sequence of Positions is valid as a Route only when it satisfies
  the minimum Route semantics of the Simulated Environment.

  Background:
    Given a local example Simulated Environment contains Positions from "(0,0)" through "(2,2)"
    And a Static Obstacle occupies Position "(1,1)"
    And the supplied origin Position is "(0,0)"
    And the supplied destination Position is "(2,2)"

  # NAV-003, NAV-004, NAV-005, NAV-006, NAV-007, NAV-008
  Scenario: Validate a supplied Route
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (1,0)    |
      | (2,0)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is valid as a Route

  # NAV-003
  Scenario: An empty Position sequence is invalid
    Given the supplied Position sequence contains no Positions
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-004
  Scenario: A sequence with the wrong origin Position is invalid
    Given the supplied Position sequence is:
      | Position |
      | (1,0)    |
      | (2,0)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-005
  Scenario: A sequence with the wrong destination Position is invalid
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (1,0)    |
      | (2,0)    |
      | (2,1)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-006
  Scenario: A sequence containing an out-of-bounds Position is invalid
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (1,0)    |
      | (2,0)    |
      | (3,0)    |
      | (2,0)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-007
  Scenario: A sequence containing a blocked Position is invalid
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (1,0)    |
      | (1,1)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-008
  Scenario: A sequence containing a non-adjacent step is invalid
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (2,0)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route

  # NAV-008
  Scenario: A sequence containing a diagonal step is invalid
    Given the supplied Position sequence is:
      | Position |
      | (0,0)    |
      | (1,0)    |
      | (2,1)    |
      | (2,2)    |
    When the supplied Position sequence is evaluated as a Route
    Then it is invalid as a Route
