import pytest
from pytest_bdd import given, parsers, scenario, then, when

from rebot.application.classify_waste_item import classify_waste_item
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState


class ClassificationContext:
    def __init__(self) -> None:
        self.waste_item: WasteItem | None = None
        self.is_processable: bool | None = None


@pytest.fixture
def classification_context() -> ClassificationContext:
    return ClassificationContext()


@scenario(
    "../features/classify_waste_item.feature",
    "Classify a Waste Item as a Known Waste Category",
)
def test_classify_a_waste_item_as_a_known_waste_category() -> None:
    pass


@scenario(
    "../features/classify_waste_item.feature",
    "Classify a Waste Item as unknown",
)
def test_classify_a_waste_item_as_unknown() -> None:
    pass


@given("a detected Waste Item has been selected as the Classification Candidate")
def detected_classification_candidate(classification_context: ClassificationContext) -> None:
    classification_context.waste_item = WasteItem()
    assert classification_context.waste_item.lifecycle_state is WasteLifecycleState.DETECTED
    assert classification_context.waste_item.category is None


@when(parsers.parse('the supplied deterministic classification result is "{category}"'))
def apply_classification_result(
    classification_context: ClassificationContext, category: str
) -> None:
    assert classification_context.waste_item is not None
    classify_waste_item(classification_context.waste_item, WasteCategory(category))


@then(parsers.parse('the Waste Item has Waste Category "{category}"'))
def waste_item_has_category(classification_context: ClassificationContext, category: str) -> None:
    assert classification_context.waste_item is not None
    assert classification_context.waste_item.category is WasteCategory(category)


@then(parsers.parse('the Waste Item has lifecycle state "{lifecycle_state}"'))
def waste_item_has_lifecycle_state(
    classification_context: ClassificationContext, lifecycle_state: str
) -> None:
    assert classification_context.waste_item is not None
    assert classification_context.waste_item.lifecycle_state is WasteLifecycleState(lifecycle_state)


@when("processability is evaluated")
def evaluate_processability(classification_context: ClassificationContext) -> None:
    assert classification_context.waste_item is not None
    classification_context.is_processable = classification_context.waste_item.is_processable()


@then("the Waste Item is Processable Waste under the current MVP policy")
def waste_item_is_processable(classification_context: ClassificationContext) -> None:
    assert classification_context.is_processable is True


@then("the Waste Item is not Processable Waste under the current MVP policy")
def waste_item_is_not_processable(classification_context: ClassificationContext) -> None:
    assert classification_context.is_processable is False
