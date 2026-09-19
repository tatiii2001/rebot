from rebot.domain.validate_supplied_route import Route
from rebot.domain.waste_item import WasteItem


def target_waste_item(waste_item: WasteItem, route: Route) -> None:
    waste_item.target(route)
