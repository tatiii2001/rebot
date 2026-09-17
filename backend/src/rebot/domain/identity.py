from dataclasses import dataclass


@dataclass(frozen=True)
class RobotIdentity:
    value: object


@dataclass(frozen=True)
class CleaningMissionIdentity:
    value: object
