import pytest
from pytest_bdd import given, scenario, then, when

from rebot.application.create_cleaning_mission import create_cleaning_mission
from rebot.application.start_cleaning_mission import start_cleaning_mission
from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.mission_start_rejection import MissionStartRejection
from rebot.domain.robot import Robot, RobotOperationalState


class StartContext:
    def __init__(self) -> None:
        self.robot: Robot | None = None
        self.mission: CleaningMission | None = None
        self.mission_identity: CleaningMissionIdentity | None = None
        self.robot_identity: RobotIdentity | None = None
        self.second_start_result: MissionStartRejection | None = None
        self.start_result: MissionStartRejection | None = None


@pytest.fixture
def start_context() -> StartContext:
    return StartContext()


@scenario(
    "../features/start_cleaning_mission.feature",
    "Start a pending Cleaning Mission with an available Assigned Robot",
)
def test_start_a_pending_cleaning_mission_with_an_available_assigned_robot() -> None:
    pass


@scenario(
    "../features/start_cleaning_mission.feature",
    "Repeat a start after the Cleaning Mission has started successfully",
)
def test_repeat_a_start_after_the_cleaning_mission_has_started_successfully() -> None:
    pass


@scenario(
    "../features/start_cleaning_mission.feature",
    "Start a pending Cleaning Mission with a non-available Assigned Robot",
)
def test_start_a_pending_cleaning_mission_with_a_non_available_assigned_robot() -> None:
    pass


@given('an existing Cleaning Mission has Mission State "pending"')
def existing_pending_mission(start_context: StartContext) -> None:
    start_context.robot_identity = RobotIdentity("robot-1")
    start_context.mission_identity = CleaningMissionIdentity("mission-1")
    start_context.robot = Robot(start_context.robot_identity)
    mission = create_cleaning_mission(start_context.mission_identity, start_context.robot)
    assert isinstance(mission, CleaningMission)
    start_context.mission = mission


@given(
    'the Cleaning Mission has exactly one Assigned Robot with Robot Operational State "available"'
)
def assigned_robot_is_available(start_context: StartContext) -> None:
    assert start_context.robot is not None
    assert start_context.robot.operational_state is RobotOperationalState.AVAILABLE


@given(
    'the Cleaning Mission has exactly one Assigned Robot with Robot Operational State "out of service"'
)
def assigned_robot_is_out_of_service(start_context: StartContext) -> None:
    assert start_context.robot_identity is not None
    assert start_context.mission_identity is not None
    start_context.robot = Robot.out_of_service(start_context.robot_identity)
    mission = create_cleaning_mission(start_context.mission_identity, start_context.robot)
    assert isinstance(mission, CleaningMission)
    start_context.mission = mission


@given("the Cleaning Mission records the Robot Identity of its Assigned Robot")
def mission_records_assigned_robot_identity(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    assert start_context.mission.assigned_robot_identity is start_context.robot.identity


@given("the Assigned Robot records the Cleaning Mission Identity as its Current Active Mission")
def robot_records_current_active_mission_identity(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    assert start_context.robot.current_active_mission_identity is start_context.mission.identity


@given("the Cleaning Mission and Assigned Robot have a reciprocal active assignment")
def mission_and_robot_have_reciprocal_assignment(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    assert start_context.mission.assigned_robot_identity is start_context.robot.identity
    assert start_context.robot.current_active_mission_identity is start_context.mission.identity


@when("the Operator requests to start the Cleaning Mission")
def request_mission_start(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    result = start_cleaning_mission(start_context.mission, start_context.robot)
    if isinstance(result, MissionStartRejection):
        start_context.start_result = result


@when("the Operator requests to start the Cleaning Mission again")
def request_mission_start_again(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    result = start_cleaning_mission(start_context.mission, start_context.robot)
    assert isinstance(result, MissionStartRejection)
    start_context.second_start_result = result


@then("the second start produces one neutral Mission Start Rejection")
def second_start_is_rejected(start_context: StartContext) -> None:
    assert start_context.second_start_result == MissionStartRejection()


@then("the start produces one neutral Mission Start Rejection")
def start_is_rejected(start_context: StartContext) -> None:
    assert start_context.start_result == MissionStartRejection()


@then('the Cleaning Mission has Mission State "running"')
def mission_is_running(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.mission.state is MissionState.RUNNING


@then('the Cleaning Mission has Mission State "pending"')
def mission_is_pending(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.mission.state is MissionState.PENDING


@then('the Assigned Robot has Robot Operational State "executing mission"')
def assigned_robot_is_executing_mission(start_context: StartContext) -> None:
    assert start_context.robot is not None
    assert start_context.robot.operational_state is RobotOperationalState.EXECUTING_MISSION


@then('the Assigned Robot has Robot Operational State "out of service"')
def assigned_robot_remains_out_of_service(start_context: StartContext) -> None:
    assert start_context.robot is not None
    assert start_context.robot.operational_state is RobotOperationalState.OUT_OF_SERVICE


@then("the Cleaning Mission retains its Cleaning Mission Identity")
def mission_retains_identity(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.mission.identity is start_context.mission_identity


@then("the Assigned Robot retains its Robot Identity")
def robot_retains_identity(start_context: StartContext) -> None:
    assert start_context.robot is not None
    assert start_context.robot.identity is start_context.robot_identity


@then("the Cleaning Mission retains its Assigned Robot")
def mission_retains_assigned_robot(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    assert start_context.mission.assigned_robot_identity is start_context.robot.identity


@then("the Cleaning Mission and Assigned Robot retain their reciprocal active assignment")
def mission_and_robot_retain_reciprocal_assignment(start_context: StartContext) -> None:
    assert start_context.mission is not None
    assert start_context.robot is not None
    assert start_context.mission.assigned_robot_identity is start_context.robot.identity
    assert start_context.robot.current_active_mission_identity is start_context.mission.identity
