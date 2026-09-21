import importlib
from typing import cast

import pytest

from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.collect_targeted_waste import collect_targeted_waste
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot, RobotOperationalState
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.start_cleaning_mission import start_cleaning_mission
from rebot.domain.validate_supplied_route import validate_supplied_route
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState

POSITION = Position(2, 2)


class ForgedRobot(Robot):
    pass


class ForgedWasteItem(WasteItem):
    pass


class ForgedPosition(Position):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Position)

    def __ne__(self, other: object) -> bool:
        return False


def _executing_robot(battery_level: BatteryLevel) -> Robot:
    robot = Robot(RobotIdentity("robot-1"), POSITION, battery_level)
    mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    return robot


def _targeted_waste_item(position: Position = POSITION) -> WasteItem:
    waste_item = WasteItem(position)
    waste_item.classify(WasteCategory.PLASTIC)
    environment = SimulatedEnvironment(
        lower_bound=position,
        upper_bound=position,
        static_obstacle_positions=frozenset(),
    )
    route = validate_supplied_route(environment, position, position, (position,))
    assert route is not None
    waste_item.target(route)
    return waste_item


def _snapshot(robot: Robot, waste_item: WasteItem) -> tuple[object, ...]:
    return (
        robot,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.position,
        robot.battery_level,
        robot.carried_waste_item,
        waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )


def _assert_snapshot_is_preserved(
    robot: Robot, waste_item: WasteItem, snapshot: tuple[object, ...]
) -> None:
    (
        expected_robot,
        expected_identity,
        expected_operational_state,
        expected_active_mission_identity,
        expected_position,
        expected_battery_level,
        expected_carried_waste_item,
        expected_waste_item,
        expected_lifecycle_state,
        expected_category,
        expected_waste_position,
    ) = snapshot
    assert robot is expected_robot
    assert robot.identity is expected_identity
    assert robot.operational_state is expected_operational_state
    assert robot.current_active_mission_identity is expected_active_mission_identity
    assert robot.position is expected_position
    assert robot.battery_level is expected_battery_level
    assert robot.carried_waste_item is expected_carried_waste_item
    assert waste_item is expected_waste_item
    assert waste_item.lifecycle_state is expected_lifecycle_state
    assert waste_item.category is expected_category
    assert waste_item.position is expected_waste_position


def test_robot_begins_carrying_no_waste_item_and_exposes_carrying_state_read_only() -> None:
    robot = Robot(RobotIdentity("robot-1"), POSITION, BatteryLevel(1))
    attribute_name = "carried_waste_item"

    assert robot.carried_waste_item is None
    with pytest.raises(AttributeError):
        setattr(robot, attribute_name, _targeted_waste_item())


def test_successful_collection_atomically_collects_and_carries_targeted_waste() -> None:
    battery_level = BatteryLevel(1)
    robot = _executing_robot(battery_level)
    waste_item = _targeted_waste_item()
    identity = robot.identity
    operational_state = robot.operational_state
    active_mission_identity = robot.current_active_mission_identity
    position = robot.position

    incident = collect_targeted_waste(robot, waste_item)

    assert incident is None
    assert waste_item.lifecycle_state is WasteLifecycleState.COLLECTED
    assert robot.carried_waste_item is waste_item
    assert robot.battery_level is battery_level
    assert robot.position is position
    assert robot.identity is identity
    assert robot.operational_state is RobotOperationalState.EXECUTING_MISSION
    assert robot.operational_state is operational_state
    assert robot.current_active_mission_identity is active_mission_identity


def test_collection_with_no_battery_preserves_participants_and_creates_one_required_incident() -> (
    None
):
    robot = _executing_robot(BatteryLevel(0))
    waste_item = _targeted_waste_item()
    snapshot = _snapshot(robot, waste_item)

    incident = collect_targeted_waste(robot, waste_item)

    assert incident == RequiredIncident()
    assert incident is not None
    assert incident.concern == "insufficient battery"
    _assert_snapshot_is_preserved(robot, waste_item, snapshot)


def test_collection_has_no_normal_public_half_transition() -> None:
    robot = Robot(RobotIdentity("robot-1"), POSITION, BatteryLevel(1))
    waste_item = _targeted_waste_item()

    assert not hasattr(robot, "carry")
    assert not hasattr(waste_item, "collect")


def test_collection_has_no_public_coordinator_that_bypasses_preconditions() -> None:
    try:
        collection_participant = importlib.import_module("rebot.domain.collection_participant")
    except ModuleNotFoundError:
        return

    coordinator = collection_participant.CollectionParticipant
    robot = Robot(RobotIdentity("robot-1"), POSITION, BatteryLevel(1))
    waste_item = _targeted_waste_item()

    coordinator.collect_together(robot, waste_item)

    assert waste_item.lifecycle_state is WasteLifecycleState.TARGETED
    assert robot.carried_waste_item is None


def test_forged_positions_with_different_coordinates_cannot_bypass_collection_colocation() -> None:
    with pytest.raises(TypeError):
        robot = Robot(RobotIdentity("robot-1"), ForgedPosition(1, 1), BatteryLevel(1))
        mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
        assert isinstance(mission, CleaningMission)
        assert start_cleaning_mission(mission, robot) is None
        waste_item = _targeted_waste_item(ForgedPosition(9, 9))

        assert collect_targeted_waste(robot, waste_item) is None
        assert waste_item.lifecycle_state is WasteLifecycleState.COLLECTED
        assert robot.carried_waste_item is waste_item


def test_robot_rejects_a_forged_position_before_participant_state_is_established() -> None:
    waste_item = _targeted_waste_item()
    waste_snapshot = (
        waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )

    with pytest.raises(TypeError):
        Robot(RobotIdentity("robot-1"), ForgedPosition(1, 1), BatteryLevel(1))

    assert waste_snapshot == (
        waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )


def test_out_of_service_robot_rejects_a_forged_position_before_participant_state_is_established() -> (
    None
):
    waste_item = _targeted_waste_item()
    waste_snapshot = (
        waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )

    with pytest.raises(TypeError):
        Robot.out_of_service(RobotIdentity("robot-1"), ForgedPosition(1, 1), BatteryLevel(1))

    assert waste_snapshot == (
        waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )


def test_waste_item_rejects_a_forged_position_without_changing_an_existing_robot() -> None:
    robot = _executing_robot(BatteryLevel(1))
    robot_snapshot = (
        robot,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.position,
        robot.battery_level,
        robot.carried_waste_item,
    )

    with pytest.raises(TypeError):
        WasteItem(ForgedPosition(9, 9))

    assert robot_snapshot == (
        robot,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.position,
        robot.battery_level,
        robot.carried_waste_item,
    )


def test_exact_positions_remain_accepted_for_robot_and_waste_item_construction() -> None:
    robot_position = Position(1, 1)
    waste_position = Position(9, 9)

    robot = Robot(RobotIdentity("robot-1"), robot_position, BatteryLevel(1))
    waste_item = WasteItem(waste_position)

    assert robot.position is robot_position
    assert waste_item.position is waste_position


@pytest.mark.parametrize(
    ("robot", "waste_item"),
    [
        (cast(Robot, "not a Robot"), _targeted_waste_item()),
        (_executing_robot(BatteryLevel(1)), cast(WasteItem, "not a Waste Item")),
    ],
)
def test_collection_rejects_invalid_runtime_arguments_before_mutation(
    robot: Robot, waste_item: WasteItem
) -> None:
    robot_state = (
        (
            robot.identity,
            robot.operational_state,
            robot.current_active_mission_identity,
            robot.position,
            robot.battery_level,
            robot.carried_waste_item,
        )
        if type(robot) is Robot
        else None
    )
    waste_item_state = (
        (
            waste_item.lifecycle_state,
            waste_item.category,
            waste_item.position,
        )
        if type(waste_item) is WasteItem
        else None
    )

    with pytest.raises(TypeError):
        collect_targeted_waste(robot, waste_item)

    if robot_state is not None:
        assert robot_state == (
            robot.identity,
            robot.operational_state,
            robot.current_active_mission_identity,
            robot.position,
            robot.battery_level,
            robot.carried_waste_item,
        )
    if waste_item_state is not None:
        assert waste_item_state == (
            waste_item.lifecycle_state,
            waste_item.category,
            waste_item.position,
        )


@pytest.mark.parametrize(
    ("robot", "waste_item"),
    [
        (ForgedRobot(RobotIdentity("robot-1"), POSITION, BatteryLevel(1)), _targeted_waste_item()),
        (_executing_robot(BatteryLevel(1)), ForgedWasteItem(POSITION)),
    ],
)
def test_collection_rejects_forged_participant_subclasses_before_mutation(
    robot: Robot, waste_item: WasteItem
) -> None:
    if type(waste_item) is ForgedWasteItem:
        waste_item.classify(WasteCategory.PLASTIC)
    snapshot = _snapshot(robot, waste_item)

    with pytest.raises(TypeError):
        collect_targeted_waste(robot, waste_item)

    _assert_snapshot_is_preserved(robot, waste_item, snapshot)


@pytest.mark.parametrize(
    "waste_item",
    [
        WasteItem(POSITION),
        _targeted_waste_item(Position(1, 1)),
    ],
)
def test_collection_rejects_wrong_lifecycle_or_position_mismatch_before_mutation(
    waste_item: WasteItem,
) -> None:
    robot = _executing_robot(BatteryLevel(1))
    if waste_item.lifecycle_state is WasteLifecycleState.DETECTED:
        waste_item.classify(WasteCategory.PLASTIC)
    snapshot = _snapshot(robot, waste_item)

    with pytest.raises((RuntimeError, ValueError)):
        collect_targeted_waste(robot, waste_item)

    _assert_snapshot_is_preserved(robot, waste_item, snapshot)


def test_collection_rejects_an_already_carrying_robot_before_mutation() -> None:
    robot = _executing_robot(BatteryLevel(1))
    carried_waste_item = _targeted_waste_item()
    assert collect_targeted_waste(robot, carried_waste_item) is None
    next_waste_item = _targeted_waste_item()
    snapshot = _snapshot(robot, next_waste_item)

    with pytest.raises(RuntimeError):
        collect_targeted_waste(robot, next_waste_item)

    _assert_snapshot_is_preserved(robot, next_waste_item, snapshot)
