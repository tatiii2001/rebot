from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MissionAssignmentRejection:
    """Neutral outcome of a rejected Cleaning Mission assignment."""
