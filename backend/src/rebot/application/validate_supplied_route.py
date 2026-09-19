from collections.abc import Sequence

from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route
from rebot.domain.validate_supplied_route import validate_supplied_route as validate_domain_route


def validate_supplied_route(
    environment: SimulatedEnvironment,
    origin: Position,
    destination: Position,
    supplied_positions: Sequence[object],
) -> Route | None:
    return validate_domain_route(environment, origin, destination, supplied_positions)
