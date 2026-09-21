from rebot.domain.follow_validated_route import follow_validated_route as follow_domain_route
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot
from rebot.domain.validate_supplied_route import Route


def follow_validated_route(robot: Robot, route: Route) -> RequiredIncident | None:
    return follow_domain_route(robot, route)
