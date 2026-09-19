from collections.abc import Sequence

from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment


class Route:
    __slots__ = ("_positions",)

    def __init__(self, positions: tuple[Position, ...]) -> None:
        raise TypeError("Route values must be created by supplied Route validation")

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_positions" and hasattr(self, "_positions"):
            raise AttributeError("Route values are immutable")
        super().__setattr__(name, value)

    @property
    def positions(self) -> tuple[Position, ...]:
        return self._positions


class _Route(Route):
    def __init__(self, positions: tuple[Position, ...]) -> None:
        self._positions = positions


def validate_supplied_route(
    environment: SimulatedEnvironment,
    origin: Position,
    destination: Position,
    supplied_positions: Sequence[object],
) -> Route | None:
    route_positions: list[Position] = []
    for position in supplied_positions:
        if not isinstance(position, Position):
            return None
        route_positions.append(position)
    positions = tuple(route_positions)
    if not positions or positions[0] != origin or positions[-1] != destination:
        return None
    if not all(environment.contains(position) for position in positions):
        return None
    if any(position in environment.static_obstacle_positions for position in positions):
        return None
    if not all(
        _are_orthogonally_adjacent(first, second)
        for first, second in zip(positions, positions[1:], strict=False)
    ):
        return None
    return _Route(positions)


def _are_orthogonally_adjacent(first: Position, second: Position) -> bool:
    return abs(first.x - second.x) + abs(first.y - second.y) == 1
