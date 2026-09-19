from typing import cast

import pytest

from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import validate_supplied_route


@pytest.fixture
def simulated_environment() -> SimulatedEnvironment:
    return SimulatedEnvironment(
        lower_bound=Position(0, 0),
        upper_bound=Position(2, 2),
        static_obstacle_positions=frozenset({Position(1, 1)}),
    )


def test_validates_a_supplied_route_and_preserves_its_position_order(
    simulated_environment: SimulatedEnvironment,
) -> None:
    supplied_positions = (
        Position(0, 0),
        Position(1, 0),
        Position(2, 0),
        Position(2, 1),
        Position(2, 2),
    )

    route = validate_supplied_route(
        simulated_environment,
        origin=Position(0, 0),
        destination=Position(2, 2),
        supplied_positions=supplied_positions,
    )

    assert route is not None
    assert route.positions == supplied_positions
    assert isinstance(route.positions, tuple)


def test_rejects_a_non_position_lower_bound() -> None:
    with pytest.raises(TypeError, match="lower bound"):
        SimulatedEnvironment(
            lower_bound=cast(Position, "not a Position"),
            upper_bound=Position(2, 2),
            static_obstacle_positions=frozenset(),
        )


def test_rejects_a_non_position_upper_bound() -> None:
    with pytest.raises(TypeError, match="upper bound"):
        SimulatedEnvironment(
            lower_bound=Position(0, 0),
            upper_bound=cast(Position, "not a Position"),
            static_obstacle_positions=frozenset(),
        )


def test_rejects_a_static_obstacle_position_outside_inclusive_bounds() -> None:
    with pytest.raises(ValueError, match="Static Obstacle Positions"):
        SimulatedEnvironment(
            lower_bound=Position(0, 0),
            upper_bound=Position(2, 2),
            static_obstacle_positions=frozenset({Position(3, 2)}),
        )


@pytest.mark.parametrize(
    ("supplied_positions", "origin", "destination"),
    [
        ((), Position(0, 0), Position(2, 2)),
        (
            (Position(1, 0), Position(2, 0), Position(2, 1), Position(2, 2)),
            Position(0, 0),
            Position(2, 2),
        ),
        (
            (Position(0, 0), Position(1, 0), Position(2, 0), Position(2, 1)),
            Position(0, 0),
            Position(2, 2),
        ),
        (
            (
                Position(0, 0),
                Position(1, 0),
                Position(2, 0),
                Position(3, 0),
                Position(2, 0),
                Position(2, 1),
                Position(2, 2),
            ),
            Position(0, 0),
            Position(2, 2),
        ),
        (
            (Position(0, 0), Position(1, 0), Position(1, 1), Position(2, 1), Position(2, 2)),
            Position(0, 0),
            Position(2, 2),
        ),
        (
            (Position(0, 0), Position(2, 0), Position(2, 1), Position(2, 2)),
            Position(0, 0),
            Position(2, 2),
        ),
        (
            (Position(0, 0), Position(1, 0), Position(2, 1), Position(2, 2)),
            Position(0, 0),
            Position(2, 2),
        ),
    ],
)
def test_invalid_supplied_position_sequences_produce_no_route(
    simulated_environment: SimulatedEnvironment,
    supplied_positions: tuple[Position, ...],
    origin: Position,
    destination: Position,
) -> None:
    route = validate_supplied_route(
        simulated_environment,
        origin=origin,
        destination=destination,
        supplied_positions=supplied_positions,
    )

    assert route is None
