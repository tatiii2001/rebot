from __future__ import annotations

from enum import StrEnum
from typing import cast

from rebot.domain.battery_level import BatteryLevel
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection
from rebot.domain.mission_start_rejection import MissionStartRejection
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.validate_supplied_route import Route


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
    def __init__(
        self, identity: RobotIdentity, position: Position, battery_level: BatteryLevel
    ) -> None:
        if not isinstance(cast(object, position), Position):
            raise TypeError("Robot Position must be a Position")
        if type(battery_level) is not BatteryLevel:
            raise TypeError("Robot Battery Level must be a BatteryLevel")

        self._identity = identity
        self._position = position
        self._battery_level = battery_level
        self._operational_state = RobotOperationalState.AVAILABLE
        self._current_active_mission_identity: CleaningMissionIdentity | None = None

    @classmethod
    def out_of_service(
        cls, identity: RobotIdentity, position: Position, battery_level: BatteryLevel
    ) -> Robot:
        robot = cls(identity, position, battery_level)
        robot._operational_state = RobotOperationalState.OUT_OF_SERVICE
        return robot

    @property
    def identity(self) -> RobotIdentity:
        return self._identity

    @property
    def operational_state(self) -> RobotOperationalState:
        return self._operational_state

    @property
    def position(self) -> Position:
        return self._position

    @property
    def battery_level(self) -> BatteryLevel:
        return self._battery_level

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

    def follow_validated_route(self, route: Route) -> RequiredIncident | None:
        if type(route) is not Route:
            raise TypeError("Route-following Route must be a Route")
        if self.position != route.positions[0]:
            raise ValueError("Route origin must match Robot Position")
        if self.operational_state is not RobotOperationalState.EXECUTING_MISSION:
            raise RuntimeError("Robot must be executing a Cleaning Mission to follow a Route")

        for next_position in route.positions[1:]:
            if self.battery_level.percentage == 0:
                return RequiredIncident()
            next_battery_level = self.battery_level.consume_one_percentage_point()
            self._position = next_position
            self._battery_level = next_battery_level
        return None


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
