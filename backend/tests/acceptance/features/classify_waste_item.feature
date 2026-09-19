Feature: Classify a Waste Item
  A Classification Candidate receives a deterministic Waste Category
  before its processability is evaluated under the current MVP policy.

  # WASTE-001, WASTE-002, WASTE-003, WASTE-004
  Scenario: Classify a Waste Item as a Known Waste Category
    Given a detected Waste Item has been selected as the Classification Candidate
    When the supplied deterministic classification result is "plastic"
    Then the Waste Item has Waste Category "plastic"
    And the Waste Item has lifecycle state "classified"
    When processability is evaluated
    Then the Waste Item is Processable Waste under the current MVP policy

  # WASTE-001, WASTE-002, WASTE-003, WASTE-005
  Scenario: Classify a Waste Item as unknown
    Given a detected Waste Item has been selected as the Classification Candidate
    When the supplied deterministic classification result is "unknown"
    Then the Waste Item has Waste Category "unknown"
    And the Waste Item has lifecycle state "classified"
    When processability is evaluated
    Then the Waste Item is not Processable Waste under the current MVP policy
