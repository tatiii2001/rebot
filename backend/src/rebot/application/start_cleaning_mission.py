from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.mission_start_rejection import MissionStartRejection
from rebot.domain.robot import Robot
from rebot.domain.start_cleaning_mission import start_cleaning_mission as start_domain_mission


def start_cleaning_mission(mission: CleaningMission, robot: Robot) -> MissionStartRejection | None:
    return start_domain_mission(mission, robot)
