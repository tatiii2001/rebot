from __future__ import annotations

from enum import StrEnum

from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection
from rebot.domain.mission_start_rejection import MissionStartRejection


class MissionState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"


class RobotOperationalState(StrEnum):
    AVAILABLE = "available"
    EXECUTING_MISSION = "executing mission"
    OUT_OF_SERVICE = "out of service"


class _StartCleaningMissionParticipant:
    def _start_for_cleaning_mission(self) -> None:
        raise NotImplementedError

    @staticmethod
    def start_together(
        mission: _StartCleaningMissionParticipant, robot: _StartCleaningMissionParticipant
    ) -> None:
        mission._start_for_cleaning_mission()
        robot._start_for_cleaning_mission()


class Robot(_StartCleaningMissionParticipant):
    def __init__(self, identity: RobotIdentity) -> None:
        self._identity = identity
        self._operational_state = RobotOperationalState.AVAILABLE
        self._current_active_mission_identity: CleaningMissionIdentity | None = None

    @classmethod
    def out_of_service(cls, identity: RobotIdentity) -> Robot:
        robot = cls(identity)
        robot._operational_state = RobotOperationalState.OUT_OF_SERVICE
        return robot

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

        mission = _CleaningMission(identity, self._identity)
        self._current_active_mission_identity = identity
        return mission

    def _start_for_cleaning_mission(self) -> None:
        self._operational_state = RobotOperationalState.EXECUTING_MISSION


class CleaningMission(_StartCleaningMissionParticipant):
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

    def _start_for_cleaning_mission(self) -> None:
        self._state = MissionState.RUNNING


class _CleaningMission(CleaningMission):
    def __init__(
        self, identity: CleaningMissionIdentity, assigned_robot_identity: RobotIdentity
    ) -> None:
        self._identity = identity
        self._assigned_robot_identity = assigned_robot_identity
        self._state = MissionState.PENDING


def start_cleaning_mission(mission: CleaningMission, robot: Robot) -> MissionStartRejection | None:
    preconditions = (
        mission.state is MissionState.PENDING,
        robot.operational_state is RobotOperationalState.AVAILABLE,
        mission.assigned_robot_identity == robot.identity,
        robot.current_active_mission_identity == mission.identity,
    )
    if not all(preconditions):
        return MissionStartRejection()

    _StartCleaningMissionParticipant.start_together(mission, robot)
    return None
