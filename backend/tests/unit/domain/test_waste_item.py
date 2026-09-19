from typing import cast

import pytest

from rebot.domain.position import Position
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState

POSITION = Position(1, 1)


def test_detected_waste_item_has_no_category() -> None:
    waste_item = WasteItem(POSITION)

    assert waste_item.category is None
    assert waste_item.lifecycle_state is WasteLifecycleState.DETECTED


def test_classifying_a_waste_item_as_plastic_records_its_category_and_lifecycle_state() -> None:
    waste_item = WasteItem(POSITION)

    waste_item.classify(WasteCategory.PLASTIC)

    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED


def test_rejects_an_arbitrary_string_classification_without_changing_a_detected_waste_item() -> (
    None
):
    waste_item = WasteItem(POSITION)

    with pytest.raises(TypeError):
        waste_item.classify(cast(WasteCategory, "unsupported"))

    assert waste_item.category is None
    assert waste_item.lifecycle_state is WasteLifecycleState.DETECTED


def test_rejects_a_none_classification_without_changing_a_detected_waste_item() -> None:
    waste_item = WasteItem(POSITION)

    with pytest.raises(TypeError):
        waste_item.classify(cast(WasteCategory, None))

    assert waste_item.category is None
    assert waste_item.lifecycle_state is WasteLifecycleState.DETECTED


def test_rejects_reclassification_without_changing_a_classified_waste_item() -> None:
    waste_item = WasteItem(POSITION)
    waste_item.classify(WasteCategory.PLASTIC)

    with pytest.raises(RuntimeError):
        waste_item.classify(WasteCategory.PAPER)

    assert waste_item.category is WasteCategory.PLASTIC
    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED


def test_rejects_processability_evaluation_before_classification_without_changing_a_detected_waste_item() -> (
    None
):
    waste_item = WasteItem(POSITION)

    with pytest.raises(RuntimeError):
        waste_item.is_processable()

    assert waste_item.category is None
    assert waste_item.lifecycle_state is WasteLifecycleState.DETECTED


@pytest.mark.parametrize(
    "category",
    [
        WasteCategory.PLASTIC,
        WasteCategory.PAPER,
        WasteCategory.METAL,
        WasteCategory.GLASS,
        WasteCategory.ORGANIC,
    ],
)
def test_known_waste_categories_are_processable_under_the_current_mvp_policy(
    category: WasteCategory,
) -> None:
    waste_item = WasteItem(POSITION)
    waste_item.classify(category)

    assert waste_item.is_processable() is True


def test_classifying_a_waste_item_as_unknown_records_its_category_and_lifecycle_state() -> None:
    waste_item = WasteItem(POSITION)

    waste_item.classify(WasteCategory.UNKNOWN)

    assert waste_item.category is WasteCategory.UNKNOWN
    assert waste_item.lifecycle_state is WasteLifecycleState.CLASSIFIED


def test_unknown_waste_is_not_processable_under_the_current_mvp_policy() -> None:
    waste_item = WasteItem(POSITION)
    waste_item.classify(WasteCategory.UNKNOWN)

    assert waste_item.is_processable() is False
