from collections.abc import Sequence
from typing import cast

from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment


class Route:
    __slots__ = ("_positions",)

    def __init__(
        self,
        environment: SimulatedEnvironment,
        origin: Position,
        destination: Position,
        supplied_positions: Sequence[object],
    ) -> None:
        if not isinstance(cast(object, environment), SimulatedEnvironment):
            raise TypeError("Route Simulated Environment must be a SimulatedEnvironment")
        if not isinstance(cast(object, origin), Position) or not isinstance(
            cast(object, destination), Position
        ):
            raise TypeError("Route endpoints must be Positions")
        if not isinstance(cast(object, supplied_positions), Sequence):
            raise TypeError("Route Positions must be a sequence")

        route_positions: list[Position] = []
        for position in supplied_positions:
            if not isinstance(position, Position):
                raise TypeError("Route Positions must be Positions")
            route_positions.append(position)
        positions = tuple(route_positions)
        if not positions:
            raise ValueError("Route must contain Positions")
        if positions[0] != origin or positions[-1] != destination:
            raise ValueError("Route endpoints must match its origin and destination")
        if not all(environment.contains(position) for position in positions):
            raise ValueError("Route Positions must be within Simulated Environment bounds")
        if any(position in environment.static_obstacle_positions for position in positions):
            raise ValueError("Route Positions must not be blocked")
        if not all(
            _are_orthogonally_adjacent(first, second)
            for first, second in zip(positions, positions[1:], strict=False)
        ):
            raise ValueError("Route Positions must be orthogonally adjacent")

        self._positions = positions

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_positions" and hasattr(self, "_positions"):
            raise AttributeError("Route values are immutable")
        super().__setattr__(name, value)

    @property
    def positions(self) -> tuple[Position, ...]:
        return self._positions


def validate_supplied_route(
    environment: SimulatedEnvironment,
    origin: Position,
    destination: Position,
    supplied_positions: Sequence[object],
) -> Route | None:
    try:
        return Route(environment, origin, destination, supplied_positions)
    except TypeError, ValueError:
        return None


def _are_orthogonally_adjacent(first: Position, second: Position) -> bool:
    return abs(first.x - second.x) + abs(first.y - second.y) == 1
