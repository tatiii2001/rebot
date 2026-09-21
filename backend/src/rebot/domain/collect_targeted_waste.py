from typing import cast

from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.waste_item import WasteItem, WasteLifecycleState


def collect_targeted_waste(robot: Robot, waste_item: WasteItem) -> RequiredIncident | None:
    if type(robot) is not Robot:
        raise TypeError("Collection Robot must be a Robot")
    if type(waste_item) is not WasteItem:
        raise TypeError("Collection Waste Item must be a WasteItem")
    if waste_item.lifecycle_state is not WasteLifecycleState.TARGETED:
        raise RuntimeError("Waste Item must be targeted to collect")
    if robot.position != waste_item.position:
        raise ValueError("Robot Position must match Waste Item Position to collect")
    if robot.carried_waste_item is not None:
        raise RuntimeError("Robot cannot collect while carrying a Waste Item")
    if robot.battery_level.percentage == 0:
        return RequiredIncident()

    _collect_together(robot, waste_item)
    return None


class _CollectionRobot:
    def _carry_collected_waste_item(self, waste_item: WasteItem) -> None:
        raise NotImplementedError

    @staticmethod
    def apply(robot: _CollectionRobot, waste_item: WasteItem) -> None:
        robot._carry_collected_waste_item(waste_item)


class _CollectionWasteItem:
    def _collect_targeted_waste(self) -> None:
        raise NotImplementedError

    @staticmethod
    def apply(waste_item: _CollectionWasteItem) -> None:
        waste_item._collect_targeted_waste()


def _collect_together(robot: Robot, waste_item: WasteItem) -> None:
    _CollectionWasteItem.apply(cast(_CollectionWasteItem, waste_item))
    _CollectionRobot.apply(cast(_CollectionRobot, robot), waste_item)
