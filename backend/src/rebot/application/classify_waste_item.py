from rebot.domain.waste_item import WasteCategory, WasteItem


def classify_waste_item(waste_item: WasteItem, classification_result: WasteCategory) -> None:
    waste_item.classify(classification_result)
