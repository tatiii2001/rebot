import pytest

from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection
from rebot.domain.position import Position
from rebot.domain.robot import Robot, RobotOperationalState


def test_cleaning_mission_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        CleaningMission(CleaningMissionIdentity("mission-1"), RobotIdentity("robot-1"))


def test_robot_creates_pending_cleaning_mission_with_reciprocal_assignment() -> None:
    robot_identity = RobotIdentity("robot-1")
    mission_identity = CleaningMissionIdentity("mission-1")
    robot = Robot(robot_identity, Position(0, 0), BatteryLevel(100))

    result = robot.create_cleaning_mission(mission_identity)

    assert isinstance(result, CleaningMission)
    assert result.identity is mission_identity
    assert result.state is MissionState.PENDING
    assert result.assigned_robot_identity is robot_identity
    assert robot.identity is robot_identity
    assert robot.operational_state is RobotOperationalState.AVAILABLE
    assert robot.current_active_mission_identity is mission_identity


def test_robot_neutrally_rejects_another_active_mission() -> None:
    robot_identity = RobotIdentity("robot-1")
    first_mission_identity = CleaningMissionIdentity("mission-1")
    robot = Robot(robot_identity, Position(0, 0), BatteryLevel(100))
    first_result = robot.create_cleaning_mission(first_mission_identity)
    assert isinstance(first_result, CleaningMission)

    result = robot.create_cleaning_mission(CleaningMissionIdentity("mission-2"))

    assert result == MissionAssignmentRejection()
    assert robot.identity is robot_identity
    assert robot.operational_state is RobotOperationalState.AVAILABLE
    assert robot.current_active_mission_identity is first_mission_identity
    assert first_result.state is MissionState.PENDING
    assert first_result.assigned_robot_identity is robot_identity
