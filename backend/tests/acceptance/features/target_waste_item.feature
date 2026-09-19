Feature: Target Processable Waste
  A classified Processable Waste Item can become Targeted Waste only when
  an already validated Route reaches the Waste Item's Position.

  # WASTE-003, WASTE-004, WASTE-006, WASTE-007; NAV-003 through NAV-008
  Scenario: Target Processable Waste using a validated Route
    Given a Waste Item at Position "(2,2)" has been classified as "plastic"
    And processability has been evaluated under the current MVP policy
    And an already validated Route ends at the Waste Item's Position
    When that Waste Item is selected as the collection target using the Route
    Then the Waste Item has lifecycle state "targeted"
    And the Waste Item still has Waste Category "plastic"
    And the Waste Item still occupies Position "(2,2)"

  # WASTE-003, WASTE-005, WASTE-006
  Scenario: Unknown Waste is not targeted
    Given a Waste Item at Position "(2,2)" has been classified as "unknown"
    And processability has been evaluated under the current MVP policy
    And an already validated Route ends at the Waste Item's Position
    When targeting that Waste Item is attempted using the Route
    Then the Waste Item remains in lifecycle state "classified"
    And the Waste Item still has Waste Category "unknown"
    And the Waste Item still occupies Position "(2,2)"

  # WASTE-006, WASTE-007
  Scenario Outline: Waste outside the classified lifecycle state is not targeted
    Given a Waste Item at Position "(2,2)" has lifecycle state "<initial_state>"
    And an already validated Route ends at the Waste Item's Position
    When targeting that Waste Item is attempted using the Route
    Then the Waste Item remains in lifecycle state "<initial_state>"
    And the Waste Item still occupies Position "(2,2)"

    Examples:
      | initial_state |
      | detected      |
      | targeted      |

  # WASTE-006; NAV-005
  Scenario: A Route to another Position does not target the Waste Item
    Given a Waste Item at Position "(2,2)" has been classified as "plastic"
    And processability has been evaluated under the current MVP policy
    And an already validated Route ends at Position "(2,1)"
    When targeting that Waste Item is attempted using the Route
    Then the Waste Item remains in lifecycle state "classified"
    And the Waste Item still has Waste Category "plastic"
    And the Waste Item still occupies Position "(2,2)"
