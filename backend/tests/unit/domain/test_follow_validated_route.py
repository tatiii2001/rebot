from typing import cast

import pytest

from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.follow_validated_route import follow_validated_route
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.start_cleaning_mission import start_cleaning_mission
from rebot.domain.validate_supplied_route import Route, validate_supplied_route

ORIGIN = Position(2, 4)
FIRST_STEP = Position(2, 3)
DESTINATION = Position(2, 2)


class ForgedBatteryLevel(BatteryLevel):
    def consume_one_percentage_point(self) -> BatteryLevel:
        return BatteryLevel(100)


class ForgedRobot(Robot):
    def follow_validated_route(self, route: Route) -> RequiredIncident | None:
        return None


def _validated_route() -> Route:
    environment = SimulatedEnvironment(
        lower_bound=DESTINATION,
        upper_bound=ORIGIN,
        static_obstacle_positions=frozenset(),
    )
    route = validate_supplied_route(
        environment,
        origin=ORIGIN,
        destination=DESTINATION,
        supplied_positions=(ORIGIN, FIRST_STEP, DESTINATION),
    )
    assert route is not None
    return route


def _executing_robot(battery_level: BatteryLevel) -> Robot:
    robot = Robot(RobotIdentity("robot-1"), ORIGIN, battery_level)
    mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    return robot


def _snapshot_route_following_state(robot: Robot, route: Route) -> tuple[object, ...]:
    return (
        robot,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.position,
        robot.battery_level,
        route,
        route.positions,
    )


def _assert_route_following_state_is_preserved(
    robot: Robot, route: Route, snapshot: tuple[object, ...]
) -> None:
    (
        expected_robot,
        expected_identity,
        expected_operational_state,
        expected_active_mission_identity,
        expected_position,
        expected_battery_level,
        expected_route,
        expected_route_positions,
    ) = snapshot

    assert robot is expected_robot
    assert robot.identity is expected_identity
    assert robot.operational_state is expected_operational_state
    assert robot.current_active_mission_identity is expected_active_mission_identity
    assert robot.position is expected_position
    assert robot.battery_level is expected_battery_level
    assert route is expected_route
    assert route.positions is expected_route_positions
    assert route.positions == (ORIGIN, FIRST_STEP, DESTINATION)


@pytest.mark.parametrize("percentage", [0, 47, 100])
def test_battery_level_accepts_valid_integer_percentages(percentage: int) -> None:
    assert BatteryLevel(percentage).percentage == percentage


@pytest.mark.parametrize("percentage", [-1, 101])
def test_battery_level_rejects_percentages_outside_its_bounds(percentage: int) -> None:
    with pytest.raises(ValueError):
        BatteryLevel(percentage)


@pytest.mark.parametrize("percentage", ["1", 1.0, None, True])
def test_battery_level_rejects_non_integer_runtime_values(percentage: object) -> None:
    with pytest.raises(TypeError):
        BatteryLevel(cast(int, percentage))


def test_battery_level_is_read_only_and_cannot_consume_below_zero() -> None:
    battery_level = BatteryLevel(0)
    percentage_attribute = "percentage"

    with pytest.raises(AttributeError):
        setattr(battery_level, percentage_attribute, 1)
    with pytest.raises(RuntimeError):
        battery_level.consume_one_percentage_point()


def test_robot_requires_valid_position_and_battery_level_and_exposes_them_read_only() -> None:
    identity = RobotIdentity("robot-1")
    position = Position(2, 4)
    battery_level = BatteryLevel(2)

    robot = Robot(identity, position, battery_level)
    position_attribute = "position"
    battery_level_attribute = "battery_level"

    assert robot.position is position
    assert robot.battery_level is battery_level
    with pytest.raises(AttributeError):
        setattr(robot, position_attribute, Position(2, 3))
    with pytest.raises(AttributeError):
        setattr(robot, battery_level_attribute, BatteryLevel(1))
    with pytest.raises(TypeError):
        Robot(identity, cast(Position, "not a Position"), battery_level)
    with pytest.raises(TypeError):
        Robot(identity, position, cast(BatteryLevel, "not a BatteryLevel"))


def test_robot_rejects_a_forged_battery_level_subclass() -> None:
    forged_battery_level = ForgedBatteryLevel(2)

    with pytest.raises(TypeError):
        Robot(RobotIdentity("robot-1"), ORIGIN, forged_battery_level)


def test_follows_a_complete_validated_route_and_preserves_robot_association_and_route() -> None:
    robot = _executing_robot(BatteryLevel(2))
    route = _validated_route()
    identity = robot.identity
    operational_state = robot.operational_state
    active_mission_identity = robot.current_active_mission_identity
    route_positions = route.positions

    incident = follow_validated_route(robot, route)

    assert incident is None
    assert robot.position == DESTINATION
    assert robot.battery_level == BatteryLevel(0)
    assert robot.identity is identity
    assert robot.operational_state is operational_state
    assert robot.current_active_mission_identity is active_mission_identity
    assert route.positions is route_positions
    assert route.positions == (ORIGIN, FIRST_STEP, DESTINATION)


def test_stops_at_the_first_step_without_battery_and_creates_one_required_incident() -> None:
    robot = _executing_robot(BatteryLevel(1))
    route = _validated_route()
    identity = robot.identity
    operational_state = robot.operational_state
    active_mission_identity = robot.current_active_mission_identity
    route_positions = route.positions

    incident = follow_validated_route(robot, route)

    assert robot.position == FIRST_STEP
    assert robot.battery_level == BatteryLevel(0)
    assert incident == RequiredIncident()
    assert incident is not None
    assert incident.concern == "insufficient battery"
    assert robot.identity is identity
    assert robot.operational_state is operational_state
    assert robot.current_active_mission_identity is active_mission_identity
    assert route.positions is route_positions
    assert route.positions == (ORIGIN, FIRST_STEP, DESTINATION)


def test_does_not_move_with_no_battery_and_creates_one_required_incident() -> None:
    robot = _executing_robot(BatteryLevel(0))
    route = _validated_route()

    incident = follow_validated_route(robot, route)

    assert robot.position == ORIGIN
    assert robot.battery_level == BatteryLevel(0)
    assert incident == RequiredIncident()


def test_rejects_a_route_origin_mismatch_before_mutating_the_robot() -> None:
    route = _validated_route()

    robot_with_different_position = Robot(RobotIdentity("robot-2"), FIRST_STEP, BatteryLevel(2))
    mission = robot_with_different_position.create_cleaning_mission(
        CleaningMissionIdentity("mission-2")
    )
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot_with_different_position) is None
    snapshot = _snapshot_route_following_state(robot_with_different_position, route)

    with pytest.raises(ValueError):
        follow_validated_route(robot_with_different_position, route)

    _assert_route_following_state_is_preserved(robot_with_different_position, route, snapshot)


def test_rejects_a_non_route_before_mutating_the_robot() -> None:
    robot = _executing_robot(BatteryLevel(2))
    invalid_route = "not a Route"
    robot_object = robot
    identity = robot.identity
    operational_state = robot.operational_state
    active_mission_identity = robot.current_active_mission_identity
    position = robot.position
    battery_level = robot.battery_level

    with pytest.raises(TypeError):
        follow_validated_route(robot, cast(Route, invalid_route))

    assert robot is robot_object
    assert robot.identity is identity
    assert robot.operational_state is operational_state
    assert robot.current_active_mission_identity is active_mission_identity
    assert robot.position is position
    assert robot.battery_level is battery_level
    assert invalid_route == "not a Route"


@pytest.mark.parametrize(
    "robot",
    [
        Robot(RobotIdentity("available-robot"), ORIGIN, BatteryLevel(2)),
        Robot.out_of_service(RobotIdentity("out-of-service-robot"), ORIGIN, BatteryLevel(2)),
    ],
)
def test_rejects_robot_operational_states_that_cannot_follow_a_route(robot: Robot) -> None:
    route = _validated_route()
    snapshot = _snapshot_route_following_state(robot, route)

    with pytest.raises(RuntimeError):
        follow_validated_route(robot, route)

    _assert_route_following_state_is_preserved(robot, route, snapshot)


def test_rejects_a_forged_robot_subclass_before_mutating_it_or_the_route() -> None:
    robot = ForgedRobot(RobotIdentity("robot-1"), ORIGIN, BatteryLevel(2))
    mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    route = _validated_route()
    snapshot = _snapshot_route_following_state(robot, route)

    with pytest.raises(TypeError):
        follow_validated_route(robot, route)

    _assert_route_following_state_is_preserved(robot, route, snapshot)
