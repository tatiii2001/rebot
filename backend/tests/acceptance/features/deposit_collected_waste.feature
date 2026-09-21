Feature: Deposit Collected Waste
  A Robot can deposit one Collected Waste Item at a Compatible Collection Point
  when the Cleaning Mission is active and the Robot has sufficient Battery Level.

  # MISSION-010, MISSION-012; ROBOT-002, ROBOT-008; WASTE-015, WASTE-016,
  # WASTE-017, WASTE-018; BATTERY-003, BATTERY-010, BATTERY-011
  # Coordinates, Battery Levels, Routes, and category acceptance are local example data, not universal product rules.
  Scenario: Deposit Collected Waste at a Compatible Collection Point
    Given a Robot begins at Position "(0,0)" with Battery Level "3%"
    And a Cleaning Mission is created with that Robot and started
    And the Cleaning Mission has Mission State "running"
    And the Robot has Robot Operational State "executing mission"
    And the Cleaning Mission and Robot active identities are reciprocal
    And a detected Waste Item at Position "(1,0)" is classified as "plastic"
    And an already validated Route "(0,0) -> (1,0)" is used to target the Waste Item
    And the Robot follows that validated Route to Position "(1,0)"
    And the Robot collects that targeted Waste Item
    And a Collection Point at Position "(2,0)" accepts Waste Category "plastic"
    And an already validated Route "(1,0) -> (2,0)" moves the Robot to the Collection Point
    And the Robot arrives at Position "(2,0)" with Battery Level "1%"
    And the Mission is "running"
    And the Robot is "executing mission"
    And the Mission and Robot active identities are reciprocal
    And the Robot carries that one Waste Item in lifecycle state "collected"
    And the Robot and Compatible Collection Point occupy Position "(2,0)"
    When the Robot deposits the Collected Waste at the Compatible Collection Point
    Then the Waste Item has lifecycle state "deposited"
    And the Waste Item occupies Position "(2,0)"
    And the Robot carries no Waste Item
    And the Robot remains at Position "(2,0)"
    And the Robot's Battery Level remains "1%"
    And the Mission remains "running"
    And the Robot remains "executing mission"
    And the Cleaning Mission Identity is unchanged
    And the Robot Identity is unchanged
    And the reciprocal active Mission identities remain unchanged
    And no Required Incident is created

  # MISSION-010, MISSION-012; ROBOT-002, ROBOT-008; WASTE-015, WASTE-016,
  # WASTE-018; BATTERY-003, BATTERY-004, BATTERY-010, BATTERY-012; INCIDENT-002
  # Coordinates, Battery Levels, Routes, and category acceptance are local example data, not universal product rules.
  Scenario: Battery Level is insufficient to deposit Collected Waste
    Given a Robot begins at Position "(0,0)" with Battery Level "2%"
    And a Cleaning Mission is created with that Robot and started
    And the Cleaning Mission has Mission State "running"
    And the Robot has Robot Operational State "executing mission"
    And the Cleaning Mission and Robot active identities are reciprocal
    And a detected Waste Item at Position "(1,0)" is classified as "plastic"
    And an already validated Route "(0,0) -> (1,0)" is used to target the Waste Item
    And the Robot follows that validated Route to Position "(1,0)"
    And the Robot collects that targeted Waste Item
    And a Collection Point at Position "(2,0)" accepts Waste Category "plastic"
    And an already validated Route "(1,0) -> (2,0)" moves the Robot to the Collection Point
    And the Robot arrives at Position "(2,0)" with Battery Level "0%"
    And every non-battery deposit precondition is valid
    And the Mission is "running"
    And the Robot is "executing mission"
    And the Mission and Robot active identities are reciprocal
    And the Robot carries that one Waste Item in lifecycle state "collected"
    And the Robot and Compatible Collection Point occupy Position "(2,0)"
    When the Robot attempts to deposit the Collected Waste at the Compatible Collection Point
    Then deposit does not begin
    And the Waste Item remains in lifecycle state "collected"
    And the Waste Item retains its pre-deposit Position
    And the Robot still carries that exact Waste Item
    And the Robot remains at Position "(2,0)"
    And the Compatible Collection Point remains at Position "(2,0)" and still accepts Waste Category "plastic"
    And the Robot's Battery Level remains "0%"
    And the Mission remains "running"
    And the Robot remains "executing mission"
    And the Cleaning Mission Identity remains unchanged
    And the Robot Identity remains unchanged
    And the reciprocal active Mission identities remain unchanged
    And exactly one Required Incident concerning "insufficient battery" is created
    And that Required Incident is available for the application to report
