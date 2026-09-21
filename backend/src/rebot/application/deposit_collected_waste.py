from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.compatible_collection_point import CompatibleCollectionPoint
from rebot.domain.deposit_collected_waste import deposit_collected_waste as deposit_domain_waste
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot


def deposit_collected_waste(
    mission: CleaningMission, robot: Robot, collection_point: CompatibleCollectionPoint
) -> RequiredIncident | None:
    return deposit_domain_waste(mission, robot, collection_point)
