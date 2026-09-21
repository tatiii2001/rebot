from dataclasses import dataclass
from typing import cast

from rebot.domain.position import Position
from rebot.domain.waste_item import WasteCategory


@dataclass(frozen=True, slots=True)
class CompatibleCollectionPoint:
    position: Position
    accepted_categories: frozenset[WasteCategory]

    def __post_init__(self) -> None:
        if type(self.position) is not Position:
            raise TypeError("Collection Point Position must be a Position")
        if type(cast(object, self.accepted_categories)) is not frozenset:
            raise TypeError("Accepted Waste Categories must be a frozenset")
        if not all(type(category) is WasteCategory for category in self.accepted_categories):
            raise TypeError("Accepted Waste Categories must be WasteCategories")

    def accepts(self, category: WasteCategory) -> bool:
        if type(category) is not WasteCategory:
            raise TypeError("Waste Category must be a WasteCategory")
        return category in self.accepted_categories
