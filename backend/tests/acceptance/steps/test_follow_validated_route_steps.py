import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.create_cleaning_mission import create_cleaning_mission
from rebot.application.follow_validated_route import follow_validated_route
from rebot.application.start_cleaning_mission import start_cleaning_mission
from rebot.application.validate_supplied_route import validate_supplied_route
from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route


class RouteFollowingContext:
    def __init__(self) -> None:
        self.position: Position | None = None
        self.battery_level: BatteryLevel | None = None
        self.robot: Robot | None = None
        self.route: Route | None = None
        self.incident: RequiredIncident | None = None


@pytest.fixture
def route_following_context() -> RouteFollowingContext:
    return RouteFollowingContext()


@scenario(
    "../features/follow_validated_route.feature",
    "Follow the complete Route with sufficient Battery Level",
)
def test_follow_the_complete_route_with_sufficient_battery_level() -> None:
    pass


@scenario(
    "../features/follow_validated_route.feature",
    "Battery Level becomes insufficient before the next Route step",
)
def test_battery_level_becomes_insufficient_before_the_next_route_step() -> None:
    pass


@given(
    parsers.parse('a Robot executing its active Cleaning Mission occupies Position "{position}"')
)
def robot_executing_active_mission_at_position(
    route_following_context: RouteFollowingContext, position: str
) -> None:
    route_following_context.position = _parse_position(position)
    _create_executing_robot(route_following_context)


@given(parsers.parse('the Robot has Battery Level "{percentage}%"'))
def robot_has_battery_level(
    route_following_context: RouteFollowingContext, percentage: str
) -> None:
    route_following_context.battery_level = BatteryLevel(int(percentage))
    _create_executing_robot(route_following_context)


@given("an already validated Route contains these Positions in order:")
def validated_route_contains_positions(
    route_following_context: RouteFollowingContext, datatable: list[list[str]]
) -> None:
    positions = tuple(_parse_position(row[0]) for row in datatable[1:])
    environment = SimulatedEnvironment(
        lower_bound=Position(
            min(position.x for position in positions), min(position.y for position in positions)
        ),
        upper_bound=Position(
            max(position.x for position in positions), max(position.y for position in positions)
        ),
        static_obstacle_positions=frozenset(),
    )
    route = validate_supplied_route(environment, positions[0], positions[-1], positions)
    assert route is not None
    route_following_context.route = route


@when("the Robot follows the validated Route")
def robot_follows_validated_route(route_following_context: RouteFollowingContext) -> None:
    assert route_following_context.robot is not None
    assert route_following_context.route is not None
    route_following_context.incident = follow_validated_route(
        route_following_context.robot, route_following_context.route
    )


@then(parsers.parse('the Robot occupies Position "{position}"'))
@then(parsers.parse('the Robot remains at Position "{position}"'))
def robot_occupies_position(route_following_context: RouteFollowingContext, position: str) -> None:
    assert route_following_context.robot is not None
    assert route_following_context.robot.position == _parse_position(position)


@then(parsers.parse('the Robot has Battery Level "{percentage}%"'))
@then(parsers.parse('the Robot\'s Battery Level remains "{percentage}%"'))
def robot_has_expected_battery_level(
    route_following_context: RouteFollowingContext, percentage: str
) -> None:
    assert route_following_context.robot is not None
    assert route_following_context.robot.battery_level == BatteryLevel(int(percentage))


@then("no Required Incident is created")
def no_required_incident_is_created(route_following_context: RouteFollowingContext) -> None:
    assert route_following_context.incident is None


@then(
    parsers.parse(
        'the first movement step atomically changes the Robot\'s Position to "{position}" '
        'and its Battery Level to "{percentage}%"'
    )
)
def first_movement_step_completed(
    route_following_context: RouteFollowingContext, position: str, percentage: str
) -> None:
    robot_occupies_position(route_following_context, position)
    robot_has_expected_battery_level(route_following_context, percentage)


@then("the second movement step does not begin")
def second_movement_step_does_not_begin(route_following_context: RouteFollowingContext) -> None:
    assert route_following_context.incident is not None


@then(parsers.parse('exactly one Required Incident concerning "{concern}" is created'))
def required_incident_is_created(
    route_following_context: RouteFollowingContext, concern: str
) -> None:
    assert route_following_context.incident == RequiredIncident()
    assert route_following_context.incident is not None
    assert route_following_context.incident.concern == concern


@then("that Required Incident is available for the application to report")
def required_incident_is_available_to_the_application(
    route_following_context: RouteFollowingContext,
) -> None:
    assert route_following_context.incident is not None


@then("the validated Route still contains these Positions in order:")
def validated_route_still_contains_positions(
    route_following_context: RouteFollowingContext, datatable: list[list[str]]
) -> None:
    assert route_following_context.route is not None
    assert route_following_context.route.positions == tuple(
        _parse_position(row[0]) for row in datatable[1:]
    )


def _create_executing_robot(context: RouteFollowingContext) -> None:
    if context.robot is not None or context.position is None or context.battery_level is None:
        return
    robot = Robot(RobotIdentity("robot-1"), context.position, context.battery_level)
    mission = create_cleaning_mission(CleaningMissionIdentity("mission-1"), robot)
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    context.robot = robot


def _parse_position(value: str) -> Position:
    x, y = value.strip("()").split(",")
    return Position(int(x), int(y))
