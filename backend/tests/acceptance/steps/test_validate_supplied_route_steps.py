import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.validate_supplied_route import validate_supplied_route
from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route


class RouteValidationContext:
    def __init__(self) -> None:
        self.environment: SimulatedEnvironment | None = None
        self.origin: Position | None = None
        self.destination: Position | None = None
        self.supplied_positions: tuple[Position, ...] = ()
        self.result: Route | None = None


@pytest.fixture
def route_validation_context() -> RouteValidationContext:
    return RouteValidationContext()


@scenario("../features/validate_supplied_route.feature", "Validate a supplied Route")
def test_validate_a_supplied_route() -> None:
    pass


@scenario("../features/validate_supplied_route.feature", "An empty Position sequence is invalid")
def test_an_empty_position_sequence_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence with the wrong origin Position is invalid",
)
def test_a_sequence_with_the_wrong_origin_position_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence with the wrong destination Position is invalid",
)
def test_a_sequence_with_the_wrong_destination_position_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence containing an out-of-bounds Position is invalid",
)
def test_a_sequence_containing_an_out_of_bounds_position_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence containing a blocked Position is invalid",
)
def test_a_sequence_containing_a_blocked_position_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence containing a non-adjacent step is invalid",
)
def test_a_sequence_containing_a_non_adjacent_step_is_invalid() -> None:
    pass


@scenario(
    "../features/validate_supplied_route.feature",
    "A sequence containing a diagonal step is invalid",
)
def test_a_sequence_containing_a_diagonal_step_is_invalid() -> None:
    pass


@given(
    parsers.parse(
        'a local example Simulated Environment contains Positions from "{lower_bound}" through "{upper_bound}"'
    )
)
def local_example_simulated_environment(
    route_validation_context: RouteValidationContext,
    lower_bound: str,
    upper_bound: str,
) -> None:
    route_validation_context.environment = SimulatedEnvironment(
        lower_bound=_parse_position(lower_bound),
        upper_bound=_parse_position(upper_bound),
        static_obstacle_positions=frozenset(),
    )


@given(parsers.parse('a Static Obstacle occupies Position "{position}"'))
def static_obstacle_occupies_position(
    route_validation_context: RouteValidationContext, position: str
) -> None:
    assert route_validation_context.environment is not None
    environment = route_validation_context.environment
    route_validation_context.environment = SimulatedEnvironment(
        lower_bound=environment.lower_bound,
        upper_bound=environment.upper_bound,
        static_obstacle_positions=frozenset({_parse_position(position)}),
    )


@given(parsers.parse('the supplied origin Position is "{position}"'))
def supplied_origin_position(
    route_validation_context: RouteValidationContext, position: str
) -> None:
    route_validation_context.origin = _parse_position(position)


@given(parsers.parse('the supplied destination Position is "{position}"'))
def supplied_destination_position(
    route_validation_context: RouteValidationContext, position: str
) -> None:
    route_validation_context.destination = _parse_position(position)


@given("the supplied Position sequence is:")
def supplied_position_sequence(
    route_validation_context: RouteValidationContext, datatable: list[list[str]]
) -> None:
    route_validation_context.supplied_positions = tuple(
        _parse_position(row[0]) for row in datatable[1:]
    )


@given("the supplied Position sequence contains no Positions")
def empty_supplied_position_sequence(route_validation_context: RouteValidationContext) -> None:
    route_validation_context.supplied_positions = ()


@when("the supplied Position sequence is evaluated as a Route")
def evaluate_supplied_position_sequence(route_validation_context: RouteValidationContext) -> None:
    assert route_validation_context.environment is not None
    assert route_validation_context.origin is not None
    assert route_validation_context.destination is not None
    route_validation_context.result = validate_supplied_route(
        route_validation_context.environment,
        route_validation_context.origin,
        route_validation_context.destination,
        route_validation_context.supplied_positions,
    )


@then("it is valid as a Route")
def valid_route(route_validation_context: RouteValidationContext) -> None:
    assert route_validation_context.result is not None


@then("it is invalid as a Route")
def invalid_route(route_validation_context: RouteValidationContext) -> None:
    assert route_validation_context.result is None


def _parse_position(value: str) -> Position:
    x, y = value.strip("()").split(",")
    return Position(int(x), int(y))
