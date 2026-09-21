from enum import StrEnum
from typing import cast

from rebot.domain.position import Position
from rebot.domain.validate_supplied_route import Route


class WasteCategory(StrEnum):
    PLASTIC = "plastic"
    PAPER = "paper"
    METAL = "metal"
    GLASS = "glass"
    ORGANIC = "organic"
    UNKNOWN = "unknown"


class WasteLifecycleState(StrEnum):
    DETECTED = "detected"
    CLASSIFIED = "classified"
    TARGETED = "targeted"
    COLLECTED = "collected"


class WasteItem:
    def __init__(self, position: Position) -> None:
        if type(position) is not Position:
            raise TypeError("Waste Item Position must be a Position")

        self._position = position
        self._category: WasteCategory | None = None
        self._lifecycle_state = WasteLifecycleState.DETECTED

    @property
    def position(self) -> Position:
        return self._position

    @property
    def category(self) -> WasteCategory | None:
        return self._category

    @property
    def lifecycle_state(self) -> WasteLifecycleState:
        return self._lifecycle_state

    def classify(self, category: WasteCategory) -> None:
        if self._lifecycle_state is not WasteLifecycleState.DETECTED:
            raise RuntimeError("Waste Item must be detected to classify")
        if not isinstance(cast(object, category), WasteCategory):
            raise TypeError("Classification result must be a WasteCategory")

        self._category = category
        self._lifecycle_state = WasteLifecycleState.CLASSIFIED

    def is_processable(self) -> bool:
        if self._lifecycle_state is not WasteLifecycleState.CLASSIFIED:
            raise RuntimeError("Waste Item must be classified to evaluate processability")

        return self._category in {
            WasteCategory.PLASTIC,
            WasteCategory.PAPER,
            WasteCategory.METAL,
            WasteCategory.GLASS,
            WasteCategory.ORGANIC,
        }

    def target(self, route: Route) -> None:
        if type(route) is not Route:
            raise TypeError("Targeting Route must be a Route")
        if self._lifecycle_state is not WasteLifecycleState.CLASSIFIED:
            raise RuntimeError("Waste Item must be classified to target")
        if not self.is_processable():
            raise RuntimeError("Waste Item must be Processable Waste to target")
        if route.positions[-1] != self._position:
            raise ValueError("Targeting Route destination must match Waste Item Position")

        self._lifecycle_state = WasteLifecycleState.TARGETED

    def _collect_targeted_waste(self) -> None:
        self._lifecycle_state = WasteLifecycleState.COLLECTED
