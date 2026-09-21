from rebot.domain.collect_targeted_waste import collect_targeted_waste as collect_domain_waste
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.waste_item import WasteItem


def collect_targeted_waste(robot: Robot, waste_item: WasteItem) -> RequiredIncident | None:
    return collect_domain_waste(robot, waste_item)
