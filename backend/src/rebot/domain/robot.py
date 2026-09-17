from enum import StrEnum

from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection


class RobotOperationalState(StrEnum):
    AVAILABLE = "available"


class Robot:
    def __init__(self, identity: RobotIdentity) -> None:
        self._identity = identity
        self._operational_state = RobotOperationalState.AVAILABLE
        self._current_active_mission_identity: CleaningMissionIdentity | None = None

    @property
    def identity(self) -> RobotIdentity:
        return self._identity

    @property
    def operational_state(self) -> RobotOperationalState:
        return self._operational_state

    @property
    def current_active_mission_identity(self) -> CleaningMissionIdentity | None:
        return self._current_active_mission_identity

    def create_cleaning_mission(
        self, identity: CleaningMissionIdentity
    ) -> CleaningMission | MissionAssignmentRejection:
        if self._current_active_mission_identity is not None:
            return MissionAssignmentRejection()

        mission = self._create_cleaning_mission(identity)
        self._current_active_mission_identity = identity
        return mission

    def _create_cleaning_mission(self, identity: CleaningMissionIdentity) -> CleaningMission:
        mission = object.__new__(CleaningMission)
        object.__setattr__(mission, "_identity", identity)
        object.__setattr__(mission, "_assigned_robot_identity", self._identity)
        object.__setattr__(mission, "_state", MissionState.PENDING)
        return mission
