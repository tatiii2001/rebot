---
description: Analyze an agreed feature and propose reviewable BDD scenarios.
agent: bdd-analyst
subtask: true
---

Analyze this feature, requirement, or acceptance-criteria scope:

$ARGUMENTS

If the scope is empty or too vague, ask one concise clarification question instead of proposing scenarios. Otherwise, inspect relevant project product, domain, and feature documentation when it exists; use the agreed ReBot ubiquitous language; and identify missing or conflicting requirements. Propose valid Gherkin only for sufficiently specified behavior and trace each acceptance criterion to its scenarios.

This is a proposal for human review. Do not create or modify `.feature` files or any other files.
