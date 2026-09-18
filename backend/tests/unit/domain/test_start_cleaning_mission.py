from collections.abc import Callable
from typing import cast

import pytest

from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_start_rejection import MissionStartRejection
from rebot.domain.robot import Robot, RobotOperationalState
from rebot.domain.start_cleaning_mission import start_cleaning_mission


def test_public_robot_construction_cannot_select_executing_mission() -> None:
    constructor = cast(Callable[..., Robot], Robot)

    with pytest.raises(TypeError):
        constructor(
            RobotIdentity("robot-1"),
            RobotOperationalState.EXECUTING_MISSION,
        )


def test_starts_a_pending_mission_with_an_available_assigned_robot() -> None:
    robot_identity = RobotIdentity("robot-1")
    mission_identity = CleaningMissionIdentity("mission-1")
    robot = Robot(robot_identity)
    mission = robot.create_cleaning_mission(mission_identity)
    assert isinstance(mission, CleaningMission)

    result = start_cleaning_mission(mission, robot)

    assert result is None
    assert mission.state is MissionState.RUNNING
    assert robot.operational_state is RobotOperationalState.EXECUTING_MISSION
    assert mission.identity is mission_identity
    assert robot.identity is robot_identity
    assert mission.assigned_robot_identity is robot_identity
    assert robot.current_active_mission_identity is mission_identity


def test_neutrally_rejects_repeating_a_successful_start() -> None:
    robot_identity = RobotIdentity("robot-1")
    mission_identity = CleaningMissionIdentity("mission-1")
    robot = Robot(robot_identity)
    mission = robot.create_cleaning_mission(mission_identity)
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None

    result = start_cleaning_mission(mission, robot)

    assert result == MissionStartRejection()
    assert mission.state is MissionState.RUNNING
    assert robot.operational_state is RobotOperationalState.EXECUTING_MISSION
    assert mission.identity is mission_identity
    assert robot.identity is robot_identity
    assert mission.assigned_robot_identity is robot_identity
    assert robot.current_active_mission_identity is mission_identity


def test_neutrally_rejects_starting_with_an_out_of_service_assigned_robot() -> None:
    robot_identity = RobotIdentity("robot-1")
    mission_identity = CleaningMissionIdentity("mission-1")
    robot = Robot.out_of_service(robot_identity)
    mission = robot.create_cleaning_mission(mission_identity)
    assert isinstance(mission, CleaningMission)

    result = start_cleaning_mission(mission, robot)

    assert result == MissionStartRejection()
    assert mission.state is MissionState.PENDING
    assert robot.operational_state is RobotOperationalState.OUT_OF_SERVICE
    assert mission.identity is mission_identity
    assert robot.identity is robot_identity
    assert mission.assigned_robot_identity is robot_identity
    assert robot.current_active_mission_identity is mission_identity


def test_neutrally_rejects_when_mission_identifies_a_different_robot() -> None:
    assigned_robot_identity = RobotIdentity("robot-1")
    other_robot_identity = RobotIdentity("robot-2")
    mission_identity = CleaningMissionIdentity("mission-1")
    assigned_robot = Robot(assigned_robot_identity)
    mission = assigned_robot.create_cleaning_mission(mission_identity)
    other_robot = Robot(other_robot_identity)
    assert isinstance(mission, CleaningMission)

    result = start_cleaning_mission(mission, other_robot)

    assert result == MissionStartRejection()
    assert mission.state is MissionState.PENDING
    assert mission.identity is mission_identity
    assert mission.assigned_robot_identity is assigned_robot_identity
    assert assigned_robot.operational_state is RobotOperationalState.AVAILABLE
    assert assigned_robot.identity is assigned_robot_identity
    assert assigned_robot.current_active_mission_identity is mission_identity
    assert other_robot.operational_state is RobotOperationalState.AVAILABLE
    assert other_robot.identity is other_robot_identity
    assert other_robot.current_active_mission_identity is None


def test_neutrally_rejects_when_robot_identifies_a_different_active_mission() -> None:
    first_robot_identity = RobotIdentity("robot-1")
    second_robot_identity = RobotIdentity("robot-2")
    first_mission_identity = CleaningMissionIdentity("mission-1")
    second_mission_identity = CleaningMissionIdentity("mission-2")
    first_robot = Robot(first_robot_identity)
    second_robot = Robot(second_robot_identity)
    first_mission = first_robot.create_cleaning_mission(first_mission_identity)
    second_mission = second_robot.create_cleaning_mission(second_mission_identity)
    assert isinstance(first_mission, CleaningMission)
    assert isinstance(second_mission, CleaningMission)

    result = start_cleaning_mission(first_mission, second_robot)

    assert result == MissionStartRejection()
    assert first_mission.state is MissionState.PENDING
    assert first_mission.identity is first_mission_identity
    assert first_mission.assigned_robot_identity is first_robot_identity
    assert first_robot.operational_state is RobotOperationalState.AVAILABLE
    assert first_robot.identity is first_robot_identity
    assert first_robot.current_active_mission_identity is first_mission_identity
    assert second_mission.state is MissionState.PENDING
    assert second_mission.identity is second_mission_identity
    assert second_mission.assigned_robot_identity is second_robot_identity
    assert second_robot.operational_state is RobotOperationalState.AVAILABLE
    assert second_robot.identity is second_robot_identity
    assert second_robot.current_active_mission_identity is second_mission_identity
