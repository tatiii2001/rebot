Feature: Collect Targeted Waste
  A Robot that has reached its targeted Processable Waste Item can collect
  that Waste Item when it has sufficient Battery Level and carries no Waste Item.

  # ROBOT-002; WASTE-004, WASTE-006, WASTE-012, WASTE-013, WASTE-014;
  # BATTERY-003, BATTERY-007, BATTERY-008
  Scenario: Collect targeted Processable Waste at the Robot's Position
    Given a Robot executing its active Cleaning Mission occupies Position "(2,2)"
    And the Robot has Battery Level "1%"
    And the Robot carries no Waste Item
    And a targeted Processable Waste Item classified as "plastic" occupies Position "(2,2)"
    When the Robot collects that targeted Waste Item
    Then the Waste Item has lifecycle state "collected"
    And the Robot carries that Waste Item
    And the Robot has Battery Level "1%"
    And no Required Incident is created

  # ROBOT-002; WASTE-004, WASTE-006, WASTE-012, WASTE-013, WASTE-014;
  # BATTERY-003, BATTERY-004, BATTERY-007, BATTERY-009; INCIDENT-002
  Scenario: Battery Level is insufficient to collect targeted Waste
    Given a Robot executing its active Cleaning Mission occupies Position "(2,2)"
    And the Robot has Battery Level "0%"
    And the Robot carries no Waste Item
    And a targeted Processable Waste Item classified as "plastic" occupies Position "(2,2)"
    When the Robot attempts to collect that targeted Waste Item
    Then collection does not begin
    And the Waste Item remains in lifecycle state "targeted"
    And the Waste Item still occupies Position "(2,2)"
    And the Robot still occupies Position "(2,2)"
    And the Robot carries no Waste Item
    And the Robot's Battery Level remains "0%"
    And exactly one Required Incident concerning "insufficient battery" is created
    And that Required Incident is available for the application to report
