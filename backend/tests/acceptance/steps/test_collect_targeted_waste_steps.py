import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.classify_waste_item import classify_waste_item
from rebot.application.collect_targeted_waste import collect_targeted_waste
from rebot.application.create_cleaning_mission import create_cleaning_mission
from rebot.application.start_cleaning_mission import start_cleaning_mission
from rebot.application.target_waste_item import target_waste_item
from rebot.application.validate_supplied_route import validate_supplied_route
from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState


class CollectionContext:
    def __init__(self) -> None:
        self.position: Position | None = None
        self.battery_level: BatteryLevel | None = None
        self.robot: Robot | None = None
        self.waste_item: WasteItem | None = None
        self.incident: RequiredIncident | None = None
        self.pre_collection_state: tuple[object, ...] | None = None


@pytest.fixture
def collection_context() -> CollectionContext:
    return CollectionContext()


@scenario(
    "../features/collect_targeted_waste.feature",
    "Collect targeted Processable Waste at the Robot's Position",
)
def test_collect_targeted_processable_waste_at_the_robots_position() -> None:
    pass


@scenario(
    "../features/collect_targeted_waste.feature",
    "Battery Level is insufficient to collect targeted Waste",
)
def test_battery_level_is_insufficient_to_collect_targeted_waste() -> None:
    pass


@given(
    parsers.parse('a Robot executing its active Cleaning Mission occupies Position "{position}"')
)
def robot_executing_active_mission_at_position(
    collection_context: CollectionContext, position: str
) -> None:
    collection_context.position = _parse_position(position)
    _create_executing_robot(collection_context)


@given(parsers.parse('the Robot has Battery Level "{percentage}%"'))
def robot_has_battery_level(collection_context: CollectionContext, percentage: str) -> None:
    collection_context.battery_level = BatteryLevel(int(percentage))
    _create_executing_robot(collection_context)


@given("the Robot carries no Waste Item")
@then("the Robot carries no Waste Item")
def robot_carries_no_waste_item(collection_context: CollectionContext) -> None:
    assert collection_context.robot is not None
    assert collection_context.robot.carried_waste_item is None


@given(
    parsers.parse(
        'a targeted Processable Waste Item classified as "{category}" occupies Position "{position}"'
    )
)
def targeted_processable_waste_item(
    collection_context: CollectionContext, category: str, position: str
) -> None:
    waste_item = WasteItem(_parse_position(position))
    classify_waste_item(waste_item, WasteCategory(category))
    environment = SimulatedEnvironment(
        lower_bound=waste_item.position,
        upper_bound=waste_item.position,
        static_obstacle_positions=frozenset(),
    )
    route = validate_supplied_route(
        environment, waste_item.position, waste_item.position, (waste_item.position,)
    )
    assert route is not None
    target_waste_item(waste_item, route)
    collection_context.waste_item = waste_item


@when("the Robot collects that targeted Waste Item")
@when("the Robot attempts to collect that targeted Waste Item")
def collect_that_targeted_waste_item(collection_context: CollectionContext) -> None:
    assert collection_context.robot is not None
    assert collection_context.waste_item is not None
    collection_context.pre_collection_state = _snapshot(
        collection_context.robot, collection_context.waste_item
    )
    collection_context.incident = collect_targeted_waste(
        collection_context.robot, collection_context.waste_item
    )


@then(parsers.parse('the Waste Item has lifecycle state "{state}"'))
def waste_item_has_lifecycle_state(collection_context: CollectionContext, state: str) -> None:
    assert collection_context.waste_item is not None
    assert collection_context.waste_item.lifecycle_state is WasteLifecycleState(state)


@then("the Robot carries that Waste Item")
def robot_carries_that_waste_item(collection_context: CollectionContext) -> None:
    assert collection_context.robot is not None
    assert collection_context.waste_item is not None
    assert collection_context.robot.carried_waste_item is collection_context.waste_item


@then(parsers.parse('the Robot has Battery Level "{percentage}%"'))
@then(parsers.parse('the Robot\'s Battery Level remains "{percentage}%"'))
def robot_has_expected_battery_level(
    collection_context: CollectionContext, percentage: str
) -> None:
    assert collection_context.robot is not None
    assert collection_context.robot.battery_level == BatteryLevel(int(percentage))


@then("no Required Incident is created")
def no_required_incident_is_created(collection_context: CollectionContext) -> None:
    assert collection_context.incident is None


@then("collection does not begin")
def collection_does_not_begin(collection_context: CollectionContext) -> None:
    assert collection_context.robot is not None
    assert collection_context.waste_item is not None
    assert collection_context.pre_collection_state is not None
    _assert_snapshot_is_preserved(
        collection_context.robot,
        collection_context.waste_item,
        collection_context.pre_collection_state,
    )


@then(parsers.parse('the Waste Item remains in lifecycle state "{state}"'))
def waste_item_remains_in_lifecycle_state(
    collection_context: CollectionContext, state: str
) -> None:
    waste_item_has_lifecycle_state(collection_context, state)


@then(parsers.parse('the Waste Item still occupies Position "{position}"'))
def waste_item_still_occupies_position(
    collection_context: CollectionContext, position: str
) -> None:
    assert collection_context.waste_item is not None
    assert collection_context.waste_item.position == _parse_position(position)


@then(parsers.parse('the Robot still occupies Position "{position}"'))
def robot_still_occupies_position(collection_context: CollectionContext, position: str) -> None:
    assert collection_context.robot is not None
    assert collection_context.robot.position == _parse_position(position)


@then(parsers.parse('exactly one Required Incident concerning "{concern}" is created'))
def required_incident_is_created(collection_context: CollectionContext, concern: str) -> None:
    assert collection_context.incident == RequiredIncident()
    assert collection_context.incident is not None
    assert collection_context.incident.concern == concern


@then("that Required Incident is available for the application to report")
def required_incident_is_available_for_application_reporting(
    collection_context: CollectionContext,
) -> None:
    assert collection_context.incident is not None


def _create_executing_robot(context: CollectionContext) -> None:
    if context.robot is not None or context.position is None or context.battery_level is None:
        return
    robot = Robot(RobotIdentity("robot-1"), context.position, context.battery_level)
    mission = create_cleaning_mission(CleaningMissionIdentity("mission-1"), robot)
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    context.robot = robot


def _snapshot(robot: Robot, waste_item: WasteItem) -> tuple[object, ...]:
    return (
        robot.position,
        robot.battery_level,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.carried_waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )


def _assert_snapshot_is_preserved(
    robot: Robot, waste_item: WasteItem, snapshot: tuple[object, ...]
) -> None:
    assert snapshot == (
        robot.position,
        robot.battery_level,
        robot.identity,
        robot.operational_state,
        robot.current_active_mission_identity,
        robot.carried_waste_item,
        waste_item.lifecycle_state,
        waste_item.category,
        waste_item.position,
    )


def _parse_position(value: str) -> Position:
    x, y = value.strip("()").split(",")
    return Position(int(x), int(y))
