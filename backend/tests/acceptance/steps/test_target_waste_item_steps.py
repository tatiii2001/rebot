import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.classify_waste_item import classify_waste_item
from rebot.application.target_waste_item import target_waste_item
from rebot.application.validate_supplied_route import validate_supplied_route
from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState


class TargetingContext:
    def __init__(self) -> None:
        self.waste_item: WasteItem | None = None
        self.route: Route | None = None
        self.is_processable: bool | None = None


@pytest.fixture
def targeting_context() -> TargetingContext:
    return TargetingContext()


@scenario(
    "../features/target_waste_item.feature",
    "Target Processable Waste using a validated Route",
)
def test_target_processable_waste_using_a_validated_route() -> None:
    pass


@scenario("../features/target_waste_item.feature", "Unknown Waste is not targeted")
def test_unknown_waste_is_not_targeted() -> None:
    pass


@scenario(
    "../features/target_waste_item.feature",
    "Waste outside the classified lifecycle state is not targeted",
)
def test_waste_outside_the_classified_lifecycle_state_is_not_targeted() -> None:
    pass


@scenario(
    "../features/target_waste_item.feature",
    "A Route to another Position does not target the Waste Item",
)
def test_a_route_to_another_position_does_not_target_the_waste_item() -> None:
    pass


@given(parsers.parse('a Waste Item at Position "{position}" has been classified as "{category}"'))
def classified_waste_item(
    targeting_context: TargetingContext, position: str, category: str
) -> None:
    waste_item = WasteItem(_parse_position(position))
    classify_waste_item(waste_item, WasteCategory(category))
    targeting_context.waste_item = waste_item


@given("processability has been evaluated under the current MVP policy")
def processability_evaluated(targeting_context: TargetingContext) -> None:
    assert targeting_context.waste_item is not None
    targeting_context.is_processable = targeting_context.waste_item.is_processable()


@given("an already validated Route ends at the Waste Item's Position")
def route_ends_at_waste_item_position(targeting_context: TargetingContext) -> None:
    assert targeting_context.waste_item is not None
    targeting_context.route = _validated_route(targeting_context.waste_item.position)


@given(parsers.parse('a Waste Item at Position "{position}" has lifecycle state "{state}"'))
def waste_item_in_lifecycle_state(
    targeting_context: TargetingContext, position: str, state: str
) -> None:
    waste_item = WasteItem(_parse_position(position))
    if WasteLifecycleState(state) is WasteLifecycleState.TARGETED:
        classify_waste_item(waste_item, WasteCategory.PLASTIC)
        target_waste_item(waste_item, _validated_route(waste_item.position))
    targeting_context.waste_item = waste_item


@given(parsers.parse('an already validated Route ends at Position "{position}"'))
def route_ends_at_position(targeting_context: TargetingContext, position: str) -> None:
    targeting_context.route = _validated_route(_parse_position(position))


@when("that Waste Item is selected as the collection target using the Route")
def target_waste_item_using_route(targeting_context: TargetingContext) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.route is not None
    target_waste_item(targeting_context.waste_item, targeting_context.route)


@when("targeting that Waste Item is attempted using the Route")
def attempt_to_target_waste_item(targeting_context: TargetingContext) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.route is not None
    with pytest.raises((RuntimeError, ValueError)):
        target_waste_item(targeting_context.waste_item, targeting_context.route)


@then(parsers.parse('the Waste Item has lifecycle state "{state}"'))
def waste_item_has_lifecycle_state(targeting_context: TargetingContext, state: str) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.waste_item.lifecycle_state is WasteLifecycleState(state)


@then(parsers.parse('the Waste Item remains in lifecycle state "{state}"'))
def waste_item_remains_in_lifecycle_state(targeting_context: TargetingContext, state: str) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.waste_item.lifecycle_state is WasteLifecycleState(state)


@then(parsers.parse('the Waste Item still has Waste Category "{category}"'))
def waste_item_still_has_category(targeting_context: TargetingContext, category: str) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.waste_item.category is WasteCategory(category)


@then(parsers.parse('the Waste Item still occupies Position "{position}"'))
def waste_item_still_occupies_position(targeting_context: TargetingContext, position: str) -> None:
    assert targeting_context.waste_item is not None
    assert targeting_context.waste_item.position == _parse_position(position)


def _validated_route(destination: Position) -> Route:
    origin = Position(0, 0)
    environment = SimulatedEnvironment(
        lower_bound=origin,
        upper_bound=Position(2, 2),
        static_obstacle_positions=frozenset(),
    )
    supplied_positions = (origin, Position(1, 0), Position(2, 0), Position(2, 1))
    if destination == Position(2, 2):
        supplied_positions += (destination,)
    route = validate_supplied_route(environment, origin, destination, supplied_positions)
    assert route is not None
    return route


def _parse_position(value: str) -> Position:
    x, y = value.strip("()").split(",")
    return Position(int(x), int(y))
