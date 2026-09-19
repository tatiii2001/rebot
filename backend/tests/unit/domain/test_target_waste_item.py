from typing import cast

import pytest

from rebot.domain.position import Position
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.validate_supplied_route import Route, validate_supplied_route
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState

ORIGIN = Position(0, 0)
WASTE_POSITION = Position(2, 2)


class ForgedRoute(Route):
    def __init__(self, positions: tuple[Position, ...]) -> None:
        self._positions = positions


def _validated_route(destination: Position = WASTE_POSITION) -> Route:
    environment = SimulatedEnvironment(
        lower_bound=ORIGIN,
        upper_bound=WASTE_POSITION,
        static_obstacle_positions=frozenset(),
    )
    if destination == WASTE_POSITION:
        supplied_positions = (ORIGIN, Position(1, 0), Position(2, 0), Position(2, 1), destination)
    else:
        supplied_positions = (ORIGIN, Position(1, 0), Position(2, 0), destination)
    route = validate_supplied_route(environment, ORIGIN, destination, supplied_positions)
    assert route is not None
    return route


def test_new_waste_item_requires_and_exposes_an_immutable_position() -> None:
    position = Position(1, 1)
    waste_item = WasteItem(position)

    assert waste_item.position is position
    attribute_name = "position"
    with pytest.raises(AttributeError):
        setattr(waste_item, attribute_name, Position(2, 2))


def test_rejects_an_invalid_runtime_position_before_initialization() -> None:
    with pytest.raises(TypeError):
        WasteItem(cast(Position, "not a Position"))


def test_targets_classified_processable_waste_without_changing_its_category_position_or_route() -> (
    None
):
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.PLASTIC)
    route = _validated_route()
    route_positions = route.positions

    waste_item.target(route)

    assert waste_item.lifecycle_state is WasteLifecycleState.TARGETED
    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.position is WASTE_POSITION
    assert route.positions is route_positions


def test_unknown_waste_cannot_be_targeted_and_remains_unchanged() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.UNKNOWN)
    route = _validated_route()
    route_positions = route.positions

    with pytest.raises(RuntimeError):
        waste_item.target(route)

    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED
    assert waste_item.category is WasteCategory.UNKNOWN
    assert waste_item.position is WASTE_POSITION
    assert route.positions is route_positions
    assert route.positions == route_positions


def test_detected_waste_cannot_be_targeted_and_remains_unchanged() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    route = _validated_route()
    route_positions = route.positions

    with pytest.raises(RuntimeError):
        waste_item.target(route)

    assert waste_item.lifecycle_state is WasteLifecycleState.DETECTED
    assert waste_item.category is None
    assert waste_item.position is WASTE_POSITION
    assert route.positions is route_positions
    assert route.positions == route_positions


def test_already_targeted_waste_cannot_be_targeted_again_and_remains_unchanged() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    route = _validated_route()
    route_positions = route.positions
    waste_item.classify(WasteCategory.PLASTIC)
    waste_item.target(route)

    with pytest.raises(RuntimeError):
        waste_item.target(route)

    assert waste_item.lifecycle_state is WasteLifecycleState.TARGETED
    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.position is WASTE_POSITION
    assert route.positions is route_positions
    assert route.positions == route_positions


def test_route_ending_at_another_position_cannot_target_waste_and_leaves_it_unchanged() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.PLASTIC)
    route = _validated_route(Position(2, 1))
    route_positions = route.positions

    with pytest.raises(ValueError):
        waste_item.target(route)

    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED
    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.position is WASTE_POSITION
    assert route.positions is route_positions
    assert route.positions == route_positions


def test_non_route_value_is_rejected_without_mutating_waste_item() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.PLASTIC)

    with pytest.raises(TypeError):
        waste_item.target(cast(Route, "not a Route"))

    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED
    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.position is WASTE_POSITION


def test_route_subclass_cannot_forge_a_targeting_route() -> None:
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.PLASTIC)
    forged_route = ForgedRoute((WASTE_POSITION,))

    with pytest.raises(TypeError):
        waste_item.target(forged_route)

    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED
    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.position is WASTE_POSITION
