Feature: Follow a validated Route
  A Robot follows an already validated Route one movement step at a time,
  using Route Positions and Battery Levels that are local to these examples.

  # NAV-001, NAV-009, BATTERY-002, BATTERY-005
  Scenario: Follow the complete Route with sufficient Battery Level
    Given a Robot executing its active Cleaning Mission occupies Position "(2,4)"
    And the Robot has Battery Level "2%"
    And an already validated Route contains these Positions in order:
      | Position |
      | (2,4)    |
      | (2,3)    |
      | (2,2)    |
    When the Robot follows the validated Route
    Then the Robot occupies Position "(2,2)"
    And the Robot has Battery Level "0%"
    And no Required Incident is created
    And the validated Route still contains these Positions in order:
      | Position |
      | (2,4)    |
      | (2,3)    |
      | (2,2)    |

  # NAV-001, NAV-009, BATTERY-002, BATTERY-004, BATTERY-005, BATTERY-006, INCIDENT-002
  Scenario: Battery Level becomes insufficient before the next Route step
    Given a Robot executing its active Cleaning Mission occupies Position "(2,4)"
    And the Robot has Battery Level "1%"
    And an already validated Route contains these Positions in order:
      | Position |
      | (2,4)    |
      | (2,3)    |
      | (2,2)    |
    When the Robot follows the validated Route
    Then the first movement step atomically changes the Robot's Position to "(2,3)" and its Battery Level to "0%"
    And the second movement step does not begin
    And the Robot remains at Position "(2,3)"
    And the Robot's Battery Level remains "0%"
    And exactly one Required Incident concerning "insufficient battery" is created
    And that Required Incident is available for the application to report
    And the validated Route still contains these Positions in order:
      | Position |
      | (2,4)    |
      | (2,3)    |
      | (2,2)    |
