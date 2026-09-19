from enum import StrEnum
from typing import cast


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


class WasteItem:
    def __init__(self) -> None:
        self._category: WasteCategory | None = None
        self._lifecycle_state = WasteLifecycleState.DETECTED

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
