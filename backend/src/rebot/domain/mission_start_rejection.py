from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MissionStartRejection:
    """Neutral outcome of a rejected Cleaning Mission start."""
