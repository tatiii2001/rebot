from dataclasses import dataclass
from typing import cast

from rebot.domain.position import Position


@dataclass(frozen=True, init=False)
class SimulatedEnvironment:
    lower_bound: Position
    upper_bound: Position
    static_obstacle_positions: frozenset[Position]

    def __init__(
        self,
        lower_bound: Position,
        upper_bound: Position,
        static_obstacle_positions: frozenset[Position],
    ) -> None:
        if not isinstance(cast(object, lower_bound), Position):
            raise TypeError("Simulated Environment lower bound must be a Position")
        if not isinstance(cast(object, upper_bound), Position):
            raise TypeError("Simulated Environment upper bound must be a Position")
        if lower_bound.x > upper_bound.x or lower_bound.y > upper_bound.y:
            raise ValueError("Simulated Environment bounds must be ordered")
        if not _are_static_obstacle_positions(static_obstacle_positions):
            raise TypeError("Static Obstacle Positions must be Positions")
        if any(
            not _is_within_inclusive_bounds(position, lower_bound, upper_bound)
            for position in static_obstacle_positions
        ):
            raise ValueError(
                "Static Obstacle Positions must be within Simulated Environment bounds"
            )

        object.__setattr__(self, "lower_bound", lower_bound)
        object.__setattr__(self, "upper_bound", upper_bound)
        object.__setattr__(self, "static_obstacle_positions", static_obstacle_positions)

    def contains(self, position: Position) -> bool:
        return _is_within_inclusive_bounds(position, self.lower_bound, self.upper_bound)


def _are_static_obstacle_positions(value: object) -> bool:
    if not isinstance(value, frozenset):
        return False
    positions = cast(frozenset[object], value)
    return all(isinstance(position, Position) for position in positions)


def _is_within_inclusive_bounds(
    position: Position, lower_bound: Position, upper_bound: Position
) -> bool:
    return (
        lower_bound.x <= position.x <= upper_bound.x
        and lower_bound.y <= position.y <= upper_bound.y
    )
