import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.classify_waste_item import classify_waste_item
from rebot.application.collect_targeted_waste import collect_targeted_waste
from rebot.application.create_cleaning_mission import create_cleaning_mission
from rebot.application.deposit_collected_waste import deposit_collected_waste
from rebot.application.follow_validated_route import follow_validated_route
from rebot.application.start_cleaning_mission import start_cleaning_mission
from rebot.application.target_waste_item import target_waste_item
from rebot.application.validate_supplied_route import validate_supplied_route
from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.compatible_collection_point import CompatibleCollectionPoint
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot, RobotOperationalState
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState


class DepositContext:
    def __init__(self) -> None:
        self.robot: Robot | None = None
        self.mission: CleaningMission | None = None
        self.waste_item: WasteItem | None = None
        self.collection_point: CompatibleCollectionPoint | None = None
        self.first_route: Route | None = None
        self.second_route: Route | None = None
        self.incident: RequiredIncident | None = None
        self.snapshot: tuple[object, ...] | None = None


@pytest.fixture
def deposit_context() -> DepositContext:
    return DepositContext()


@scenario(
    "../features/deposit_collected_waste.feature",
    "Deposit Collected Waste at a Compatible Collection Point",
)
def test_deposit_collected_waste_at_a_compatible_collection_point() -> None:
    pass


@scenario(
    "../features/deposit_collected_waste.feature",
    "Battery Level is insufficient to deposit Collected Waste",
)
def test_battery_level_is_insufficient_to_deposit_collected_waste() -> None:
    pass


@given(parsers.parse('a Robot begins at Position "{position}" with Battery Level "{percentage}%"'))
def robot_begins_at_position(
    deposit_context: DepositContext, position: str, percentage: str
) -> None:
    deposit_context.robot = Robot(
        RobotIdentity("robot-1"), _parse_position(position), BatteryLevel(int(percentage))
    )


@given("a Cleaning Mission is created with that Robot and started")
def cleaning_mission_is_created_and_started(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    mission = create_cleaning_mission(CleaningMissionIdentity("mission-1"), deposit_context.robot)
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, deposit_context.robot) is None
    deposit_context.mission = mission


@given(parsers.parse('the Cleaning Mission has Mission State "{state}"'))
def cleaning_mission_has_state(deposit_context: DepositContext, state: str) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.mission.state is MissionState(state)


@given(parsers.parse('the Robot has Robot Operational State "{state}"'))
def robot_has_operational_state(deposit_context: DepositContext, state: str) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.robot.operational_state is RobotOperationalState(state)


@given("the Cleaning Mission and Robot active identities are reciprocal")
def mission_and_robot_active_identities_are_reciprocal(deposit_context: DepositContext) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.robot is not None
    assert deposit_context.mission.assigned_robot_identity is deposit_context.robot.identity
    assert deposit_context.robot.current_active_mission_identity is deposit_context.mission.identity


@given(
    parsers.parse('a detected Waste Item at Position "{position}" is classified as "{category}"')
)
def detected_waste_item_is_classified(
    deposit_context: DepositContext, position: str, category: str
) -> None:
    waste_item = WasteItem(_parse_position(position))
    classify_waste_item(waste_item, WasteCategory(category))
    deposit_context.waste_item = waste_item


@given(parsers.parse('an already validated Route "{route}" is used to target the Waste Item'))
def first_route_targets_waste_item(deposit_context: DepositContext, route: str) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    origin, destination = _parse_route(route)
    environment = SimulatedEnvironment(origin, Position(2, 0), frozenset())
    validated_route = validate_supplied_route(
        environment, origin, destination, (origin, destination)
    )
    assert validated_route is not None
    assert origin == deposit_context.robot.position
    assert destination == deposit_context.waste_item.position
    target_waste_item(deposit_context.waste_item, validated_route)
    deposit_context.first_route = validated_route


@given(parsers.parse('the Robot follows that validated Route to Position "{position}"'))
def robot_follows_first_route(deposit_context: DepositContext, position: str) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.first_route is not None
    assert follow_validated_route(deposit_context.robot, deposit_context.first_route) is None
    assert deposit_context.robot.position == _parse_position(position)


@given("the Robot collects that targeted Waste Item")
def robot_collects_targeted_waste_item(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    assert collect_targeted_waste(deposit_context.robot, deposit_context.waste_item) is None


@given(
    parsers.parse('a Collection Point at Position "{position}" accepts Waste Category "{category}"')
)
def compatible_collection_point_is_created(
    deposit_context: DepositContext, position: str, category: str
) -> None:
    deposit_context.collection_point = CompatibleCollectionPoint(
        _parse_position(position), frozenset({WasteCategory(category)})
    )


@given(
    parsers.parse('an already validated Route "{route}" moves the Robot to the Collection Point')
)
def second_route_moves_robot_to_collection_point(
    deposit_context: DepositContext, route: str
) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.collection_point is not None
    origin, destination = _parse_route(route)
    environment = SimulatedEnvironment(Position(0, 0), destination, frozenset())
    validated_route = validate_supplied_route(
        environment, origin, destination, (origin, destination)
    )
    assert validated_route is not None
    assert origin == deposit_context.robot.position
    assert destination == deposit_context.collection_point.position
    assert follow_validated_route(deposit_context.robot, validated_route) is None
    deposit_context.second_route = validated_route


@given(
    parsers.parse('the Robot arrives at Position "{position}" with Battery Level "{percentage}%"')
)
def robot_arrives_with_battery_level(
    deposit_context: DepositContext, position: str, percentage: str
) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.robot.position == _parse_position(position)
    assert deposit_context.robot.battery_level == BatteryLevel(int(percentage))


@given(parsers.parse('the Mission is "{state}"'))
def mission_is_state(deposit_context: DepositContext, state: str) -> None:
    cleaning_mission_has_state(deposit_context, state)


@given(parsers.parse('the Robot is "{state}"'))
def robot_is_state(deposit_context: DepositContext, state: str) -> None:
    robot_has_operational_state(deposit_context, state)


@given("the Mission and Robot active identities are reciprocal")
def mission_and_robot_identities_are_reciprocal(deposit_context: DepositContext) -> None:
    mission_and_robot_active_identities_are_reciprocal(deposit_context)


@given('the Robot carries that one Waste Item in lifecycle state "collected"')
def robot_carries_collected_waste_item(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    assert deposit_context.robot.carried_waste_item is deposit_context.waste_item
    assert deposit_context.waste_item.lifecycle_state is WasteLifecycleState.COLLECTED


@given('the Robot and Compatible Collection Point occupy Position "(2,0)"')
@given("every non-battery deposit precondition is valid")
def deposit_preconditions_are_valid(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.collection_point is not None
    assert deposit_context.robot.position == deposit_context.collection_point.position


@when("the Robot deposits the Collected Waste at the Compatible Collection Point")
@when("the Robot attempts to deposit the Collected Waste at the Compatible Collection Point")
def deposit_collected_waste_at_collection_point(deposit_context: DepositContext) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    assert deposit_context.collection_point is not None
    deposit_context.snapshot = _snapshot(
        deposit_context.mission,
        deposit_context.robot,
        deposit_context.waste_item,
        deposit_context.collection_point,
    )
    deposit_context.incident = deposit_collected_waste(
        deposit_context.mission, deposit_context.robot, deposit_context.collection_point
    )


@then(parsers.parse('the Waste Item has lifecycle state "{state}"'))
def waste_item_has_lifecycle_state(deposit_context: DepositContext, state: str) -> None:
    assert deposit_context.waste_item is not None
    assert deposit_context.waste_item.lifecycle_state is WasteLifecycleState(state)


@then(parsers.parse('the Waste Item occupies Position "{position}"'))
def waste_item_occupies_position(deposit_context: DepositContext, position: str) -> None:
    assert deposit_context.waste_item is not None
    assert deposit_context.waste_item.position == _parse_position(position)


@then(parsers.parse('the Robot remains at Position "{position}"'))
def robot_remains_at_position(deposit_context: DepositContext, position: str) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.robot.position == _parse_position(position)


@then("the Robot carries no Waste Item")
def robot_carries_no_waste_item(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.robot.carried_waste_item is None


@then(parsers.parse('the Robot\'s Battery Level remains "{percentage}%"'))
def robot_battery_level_remains(deposit_context: DepositContext, percentage: str) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.robot.battery_level == BatteryLevel(int(percentage))


@then(parsers.parse('the Mission remains "{state}"'))
def mission_remains_state(deposit_context: DepositContext, state: str) -> None:
    cleaning_mission_has_state(deposit_context, state)


@then(parsers.parse('the Robot remains "{state}"'))
def robot_remains_state(deposit_context: DepositContext, state: str) -> None:
    robot_has_operational_state(deposit_context, state)


@then("the Cleaning Mission Identity is unchanged")
@then("the Cleaning Mission Identity remains unchanged")
def mission_identity_is_unchanged(deposit_context: DepositContext) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.snapshot is not None
    assert deposit_context.mission.identity is deposit_context.snapshot[1]


@then("the Robot Identity is unchanged")
@then("the Robot Identity remains unchanged")
def robot_identity_is_unchanged(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.snapshot is not None
    assert deposit_context.robot.identity is deposit_context.snapshot[5]


@then("the reciprocal active Mission identities remain unchanged")
def reciprocal_active_mission_identities_remain_unchanged(deposit_context: DepositContext) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.robot is not None
    assert deposit_context.snapshot is not None
    assert deposit_context.mission.assigned_robot_identity is deposit_context.snapshot[2]
    assert deposit_context.robot.current_active_mission_identity is deposit_context.snapshot[6]
    assert deposit_context.mission.assigned_robot_identity is deposit_context.robot.identity
    assert deposit_context.robot.current_active_mission_identity is deposit_context.mission.identity


@then("no Required Incident is created")
def no_required_incident_is_created(deposit_context: DepositContext) -> None:
    assert deposit_context.incident is None


@then("deposit does not begin")
def deposit_does_not_begin(deposit_context: DepositContext) -> None:
    assert deposit_context.mission is not None
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    assert deposit_context.collection_point is not None
    assert deposit_context.snapshot == _snapshot(
        deposit_context.mission,
        deposit_context.robot,
        deposit_context.waste_item,
        deposit_context.collection_point,
    )


@then(parsers.parse('the Waste Item remains in lifecycle state "{state}"'))
def waste_item_remains_in_lifecycle_state(deposit_context: DepositContext, state: str) -> None:
    waste_item_has_lifecycle_state(deposit_context, state)


@then("the Waste Item retains its pre-deposit Position")
def waste_item_retains_pre_deposit_position(deposit_context: DepositContext) -> None:
    assert deposit_context.waste_item is not None
    assert deposit_context.snapshot is not None
    assert deposit_context.waste_item.position is deposit_context.snapshot[13]


@then("the Robot still carries that exact Waste Item")
def robot_still_carries_exact_waste_item(deposit_context: DepositContext) -> None:
    assert deposit_context.robot is not None
    assert deposit_context.waste_item is not None
    assert deposit_context.robot.carried_waste_item is deposit_context.waste_item


@then(
    'the Compatible Collection Point remains at Position "(2,0)" and still accepts Waste Category "plastic"'
)
def collection_point_is_unchanged(deposit_context: DepositContext) -> None:
    assert deposit_context.collection_point is not None
    assert deposit_context.collection_point.position == Position(2, 0)
    assert deposit_context.collection_point.accepts(WasteCategory.PLASTIC) is True


@then(parsers.parse('exactly one Required Incident concerning "{concern}" is created'))
def required_incident_is_created(deposit_context: DepositContext, concern: str) -> None:
    assert deposit_context.incident == RequiredIncident()
    assert deposit_context.incident is not None
    assert deposit_context.incident.concern == concern


@then("that Required Incident is available for the application to report")
def required_incident_is_available_for_application_reporting(
    deposit_context: DepositContext,
) -> None:
    assert deposit_context.incident is not None


def _snapshot(
    mission: CleaningMission,
    robot: Robot,
    waste_item: WasteItem,
    collection_point: CompatibleCollectionPoint,
) -> tuple[object, ...]:
    return (
        mission,
        mission.identity,
        mission.assigned_robot_identity,
        mission.state,
        robot,
        robot.identity,
        robot.current_active_mission_identity,
        robot.operational_state,
        robot.position,
        robot.battery_level,
        robot.carried_waste_item,
        waste_item,
        waste_item.lifecycle_state,
        waste_item.position,
        waste_item.category,
        collection_point,
        collection_point.position,
        collection_point.accepted_categories,
    )


def _parse_position(value: str) -> Position:
    x, y = value.strip("()").split(",")
    return Position(int(x), int(y))


def _parse_route(value: str) -> tuple[Position, Position]:
    origin, destination = value.split(" -> ")
    return _parse_position(origin), _parse_position(destination)
