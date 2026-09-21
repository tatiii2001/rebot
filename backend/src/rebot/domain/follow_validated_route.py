from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.validate_supplied_route import Route


def follow_validated_route(robot: Robot, route: Route) -> RequiredIncident | None:
    if type(robot) is not Robot:
        raise TypeError("Route-following Robot must be a Robot")
    return robot.follow_validated_route(route)
