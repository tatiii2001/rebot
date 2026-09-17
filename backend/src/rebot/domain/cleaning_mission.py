from enum import StrEnum

from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity


class MissionState(StrEnum):
    PENDING = "pending"


class CleaningMission:
    _identity: CleaningMissionIdentity
    _assigned_robot_identity: RobotIdentity
    _state: MissionState

    def __init__(
        self, identity: CleaningMissionIdentity, assigned_robot_identity: RobotIdentity
    ) -> None:
        raise TypeError("CleaningMission must be created by its assigned Robot")

    @property
    def identity(self) -> CleaningMissionIdentity:
        return self._identity

    @property
    def assigned_robot_identity(self) -> RobotIdentity:
        return self._assigned_robot_identity

    @property
    def state(self) -> MissionState:
        return self._state
