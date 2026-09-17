from rebot.domain.cleaning_mission import CleaningMission
from rebot.domain.identity import CleaningMissionIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection
from rebot.domain.robot import Robot


def create_cleaning_mission(
    identity: CleaningMissionIdentity, robot: Robot
) -> CleaningMission | MissionAssignmentRejection:
    return robot.create_cleaning_mission(identity)
