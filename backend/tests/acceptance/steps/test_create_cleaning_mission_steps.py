import pytest
from pytest_bdd import given, scenario, then, when

from rebot.application.create_cleaning_mission import create_cleaning_mission
from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_assignment_rejection import MissionAssignmentRejection
from rebot.domain.position import Position
from rebot.domain.robot import Robot, RobotOperationalState


class CreationContext:
    def __init__(self) -> None:
        self.robot: Robot | None = None
        self.existing_mission: CleaningMission | None = None
        self.result: CleaningMission | MissionAssignmentRejection | None = None


@pytest.fixture
def creation_context() -> CreationContext:
    return CreationContext()


@scenario(
    "../features/create_cleaning_mission.feature",
    "Create a Cleaning Mission with an available Robot",
)
def test_create_cleaning_mission_with_an_available_robot() -> None:
    pass


@scenario(
    "../features/create_cleaning_mission.feature",
    "Reject another Active Mission for the same Robot",
)
def test_reject_another_active_mission_for_the_same_robot() -> None:
    pass


@given("an available Robot records no Current Active Mission")
def available_robot(creation_context: CreationContext) -> None:
    creation_context.robot = Robot(RobotIdentity("robot-1"), Position(0, 0), BatteryLevel(100))
    assert creation_context.robot.operational_state is RobotOperationalState.AVAILABLE
    assert creation_context.robot.current_active_mission_identity is None


@when("a Cleaning Mission is created with the Robot as its Assigned Robot")
def create_first_mission(creation_context: CreationContext) -> None:
    assert creation_context.robot is not None
    creation_context.result = create_cleaning_mission(
        CleaningMissionIdentity("mission-1"), creation_context.robot
    )


@then("exactly one Cleaning Mission is created")
def one_cleaning_mission_is_created(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)


@then('the Cleaning Mission has Mission State "pending"')
def cleaning_mission_is_pending(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)
    assert creation_context.result.state is MissionState.PENDING


@then("the Cleaning Mission has exactly one Assigned Robot")
def cleaning_mission_has_assigned_robot(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)
    assert creation_context.result.assigned_robot_identity is not None


@then("the Cleaning Mission records the Robot Identity of its Assigned Robot")
def cleaning_mission_records_robot_identity(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)
    assert creation_context.robot is not None
    assert creation_context.result.assigned_robot_identity is creation_context.robot.identity


@then("the Robot records the Cleaning Mission Identity as its Current Active Mission")
def robot_records_mission_identity(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)
    assert creation_context.robot is not None
    assert (
        creation_context.robot.current_active_mission_identity is creation_context.result.identity
    )


@then("the Cleaning Mission and Robot have a reciprocal active assignment")
def cleaning_mission_and_robot_are_reciprocal(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, CleaningMission)
    assert creation_context.robot is not None
    assert creation_context.result.assigned_robot_identity is creation_context.robot.identity
    assert (
        creation_context.robot.current_active_mission_identity is creation_context.result.identity
    )


@given('an existing Cleaning Mission has Mission State "pending"')
def existing_pending_mission(creation_context: CreationContext) -> None:
    creation_context.robot = Robot(RobotIdentity("robot-1"), Position(0, 0), BatteryLevel(100))
    result = create_cleaning_mission(CleaningMissionIdentity("mission-1"), creation_context.robot)
    assert isinstance(result, CleaningMission)
    creation_context.existing_mission = result


@given('its Assigned Robot has Robot Operational State "available"')
def assigned_robot_is_available(creation_context: CreationContext) -> None:
    assert creation_context.robot is not None
    assert creation_context.robot.operational_state is RobotOperationalState.AVAILABLE


@given("the Cleaning Mission and Robot have a reciprocal active assignment")
def existing_mission_and_robot_are_reciprocal(creation_context: CreationContext) -> None:
    assert creation_context.existing_mission is not None
    assert creation_context.robot is not None
    assert (
        creation_context.existing_mission.assigned_robot_identity is creation_context.robot.identity
    )
    assert (
        creation_context.robot.current_active_mission_identity
        is creation_context.existing_mission.identity
    )


@when("creation of another Cleaning Mission with the same Robot as its Assigned Robot is attempted")
def create_second_mission(creation_context: CreationContext) -> None:
    assert creation_context.robot is not None
    creation_context.result = create_cleaning_mission(
        CleaningMissionIdentity("mission-2"), creation_context.robot
    )


@then("one neutral Mission Assignment Rejection is produced")
def mission_assignment_rejection_is_produced(creation_context: CreationContext) -> None:
    assert creation_context.result == MissionAssignmentRejection()


@then("no second Cleaning Mission is created")
def no_second_cleaning_mission_is_created(creation_context: CreationContext) -> None:
    assert isinstance(creation_context.result, MissionAssignmentRejection)


@then('the existing Cleaning Mission has Mission State "pending"')
def existing_mission_remains_pending(creation_context: CreationContext) -> None:
    assert creation_context.existing_mission is not None
    assert creation_context.existing_mission.state is MissionState.PENDING


@then('the Robot has Robot Operational State "available"')
def robot_remains_available(creation_context: CreationContext) -> None:
    assert creation_context.robot is not None
    assert creation_context.robot.operational_state is RobotOperationalState.AVAILABLE


@then("the existing Cleaning Mission retains its Assigned Robot")
def existing_mission_retains_assigned_robot(creation_context: CreationContext) -> None:
    assert creation_context.existing_mission is not None
    assert creation_context.robot is not None
    assert (
        creation_context.existing_mission.assigned_robot_identity is creation_context.robot.identity
    )


@then("the Cleaning Mission and Robot retain their reciprocal active assignment")
def existing_mission_and_robot_remain_reciprocal(creation_context: CreationContext) -> None:
    assert creation_context.existing_mission is not None
    assert creation_context.robot is not None
    assert (
        creation_context.existing_mission.assigned_robot_identity is creation_context.robot.identity
    )
    assert (
        creation_context.robot.current_active_mission_identity
        is creation_context.existing_mission.identity
    )


@then('no Cleaning Mission transitions to Mission State "failed"')
def no_cleaning_mission_fails(creation_context: CreationContext) -> None:
    assert creation_context.existing_mission is not None
    assert creation_context.existing_mission.state is MissionState.PENDING
