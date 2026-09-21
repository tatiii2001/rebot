from typing import cast

import pytest

from rebot.domain.battery_level import BatteryLevel
from rebot.domain.cleaning_mission import CleaningMission, MissionState
from rebot.domain.collect_targeted_waste import collect_targeted_waste
from rebot.domain.compatible_collection_point import CompatibleCollectionPoint
from rebot.domain.deposit_collected_waste import deposit_collected_waste
from rebot.domain.identity import CleaningMissionIdentity, RobotIdentity
from rebot.domain.position import Position
from rebot.domain.required_incident import RequiredIncident
from rebot.domain.robot import Robot, RobotOperationalState
from rebot.domain.simulated_environment import SimulatedEnvironment
from rebot.domain.start_cleaning_mission import start_cleaning_mission
from rebot.domain.validate_supplied_route import validate_supplied_route
from rebot.domain.waste_item import WasteCategory, WasteItem, WasteLifecycleState

ROBOT_POSITION = Position(0, 0)
WASTE_POSITION = Position(1, 0)
COLLECTION_POINT_POSITION = Position(2, 0)


class ForgedPosition(Position):
    equality_calls = 0
    __hash__ = Position.__hash__

    def __eq__(self, other: object) -> bool:
        type(self).equality_calls += 1
        return isinstance(other, Position)


class ForgedRobot(Robot):
    pass


class ForgedCleaningMission(CleaningMission):
    def __init__(self, pending_mission: CleaningMission, pending_robot: Robot) -> None:
        self.pending_mission = pending_mission
        self.pending_robot = pending_robot

    @property
    def state(self) -> MissionState:
        assert start_cleaning_mission(self.pending_mission, self.pending_robot) is None
        return MissionState.RUNNING

    @property
    def assigned_robot_identity(self) -> RobotIdentity:
        return self.pending_robot.identity

    @property
    def identity(self) -> CleaningMissionIdentity:
        assert self.pending_robot.current_active_mission_identity is not None
        return self.pending_robot.current_active_mission_identity


class ForgedCollectionPoint(CompatibleCollectionPoint):
    def accepts(self, category: WasteCategory) -> bool:
        return True


def _collected_waste_participants(
    battery_level: BatteryLevel,
) -> tuple[CleaningMission, Robot, WasteItem]:
    robot = Robot(RobotIdentity("robot-1"), ROBOT_POSITION, battery_level)
    mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    waste_item = WasteItem(WASTE_POSITION)
    waste_item.classify(WasteCategory.PLASTIC)
    environment = SimulatedEnvironment(ROBOT_POSITION, COLLECTION_POINT_POSITION, frozenset())
    first_route = validate_supplied_route(
        environment, ROBOT_POSITION, WASTE_POSITION, (ROBOT_POSITION, WASTE_POSITION)
    )
    assert first_route is not None
    waste_item.target(first_route)
    robot.follow_validated_route(first_route)
    assert collect_targeted_waste(robot, waste_item) is None
    second_route = validate_supplied_route(
        environment,
        WASTE_POSITION,
        COLLECTION_POINT_POSITION,
        (WASTE_POSITION, COLLECTION_POINT_POSITION),
    )
    assert second_route is not None
    assert robot.follow_validated_route(second_route) is None
    return mission, robot, waste_item


def _collection_point(
    accepted_categories: frozenset[WasteCategory] = frozenset({WasteCategory.PLASTIC}),
) -> CompatibleCollectionPoint:
    return CompatibleCollectionPoint(COLLECTION_POINT_POSITION, accepted_categories)


def _snapshot(
    mission: CleaningMission,
    robot: Robot,
    waste_item: WasteItem,
    collection_point: CompatibleCollectionPoint,
) -> tuple[object, ...]:
    return (
        mission,
        mission.identity,
        mission.assigned_robot_identity,
        mission.state,
        robot,
        robot.identity,
        robot.current_active_mission_identity,
        robot.operational_state,
        robot.position,
        robot.battery_level,
        robot.carried_waste_item,
        waste_item,
        waste_item.lifecycle_state,
        waste_item.position,
        waste_item.category,
        collection_point,
        collection_point.position,
        collection_point.accepted_categories,
    )


def _assert_snapshot_is_preserved(
    mission: CleaningMission,
    robot: Robot,
    waste_item: WasteItem,
    collection_point: CompatibleCollectionPoint,
    snapshot: tuple[object, ...],
) -> None:
    assert snapshot == _snapshot(mission, robot, waste_item, collection_point)
    assert mission.assigned_robot_identity is robot.identity
    assert robot.current_active_mission_identity is mission.identity


def test_successful_deposit_atomically_deposits_the_exact_carried_waste() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    collection_point = _collection_point()
    mission_identity = mission.identity
    assigned_robot_identity = mission.assigned_robot_identity
    robot_identity = robot.identity
    active_mission_identity = robot.current_active_mission_identity
    battery_level = robot.battery_level
    robot_position = robot.position

    incident = deposit_collected_waste(mission, robot, collection_point)

    assert incident is None
    assert waste_item.lifecycle_state is WasteLifecycleState.DEPOSITED
    assert waste_item.position is collection_point.position
    assert robot.carried_waste_item is None
    assert robot.battery_level is battery_level
    assert robot.position is robot_position
    assert mission.state is MissionState.RUNNING
    assert robot.operational_state is RobotOperationalState.EXECUTING_MISSION
    assert mission.identity is mission_identity
    assert mission.assigned_robot_identity is assigned_robot_identity
    assert robot.identity is robot_identity
    assert robot.current_active_mission_identity is active_mission_identity
    assert mission.assigned_robot_identity is robot.identity
    assert robot.current_active_mission_identity is mission.identity


def test_zero_battery_creates_one_required_incident_without_mutating_participants() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(2))
    collection_point = _collection_point()
    snapshot = _snapshot(mission, robot, waste_item, collection_point)

    incident = deposit_collected_waste(mission, robot, collection_point)

    assert incident == RequiredIncident()
    assert incident is not None
    assert incident.concern == "insufficient battery"
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)


@pytest.mark.parametrize(
    "collection_point",
    [
        _collection_point(),
        CompatibleCollectionPoint(WASTE_POSITION, frozenset({WasteCategory.PAPER})),
    ],
)
def test_no_carried_waste_or_an_incompatible_collection_point_preserves_participants(
    collection_point: CompatibleCollectionPoint,
) -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    if collection_point.position is WASTE_POSITION:
        collection_point = CompatibleCollectionPoint(
            COLLECTION_POINT_POSITION, collection_point.accepted_categories
        )
    if collection_point.accepted_categories == frozenset({WasteCategory.PLASTIC}):
        robot_without_waste = Robot(
            RobotIdentity("robot-2"), COLLECTION_POINT_POSITION, BatteryLevel(1)
        )
        pending_mission = robot_without_waste.create_cleaning_mission(
            CleaningMissionIdentity("mission-2")
        )
        assert isinstance(pending_mission, CleaningMission)
        assert start_cleaning_mission(pending_mission, robot_without_waste) is None
        empty_waste = WasteItem(COLLECTION_POINT_POSITION)
        empty_waste.classify(WasteCategory.PLASTIC)
        snapshot = _snapshot(pending_mission, robot_without_waste, empty_waste, collection_point)
        assert (
            deposit_collected_waste(pending_mission, robot_without_waste, collection_point) is None
        )
        _assert_snapshot_is_preserved(
            pending_mission, robot_without_waste, empty_waste, collection_point, snapshot
        )
        return

    snapshot = _snapshot(mission, robot, waste_item, collection_point)
    assert deposit_collected_waste(mission, robot, collection_point) is None
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)


def test_position_mismatch_and_nonreciprocal_participants_preserve_participants() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    distant_collection_point = CompatibleCollectionPoint(
        WASTE_POSITION, frozenset({WasteCategory.PLASTIC})
    )
    snapshot = _snapshot(mission, robot, waste_item, distant_collection_point)

    assert deposit_collected_waste(mission, robot, distant_collection_point) is None
    _assert_snapshot_is_preserved(mission, robot, waste_item, distant_collection_point, snapshot)

    other_mission, other_robot, other_waste_item = _collected_waste_participants(BatteryLevel(3))
    collection_point = _collection_point()
    mission_snapshot = _snapshot(mission, robot, waste_item, collection_point)
    other_snapshot = _snapshot(other_mission, other_robot, other_waste_item, collection_point)

    assert deposit_collected_waste(mission, other_robot, collection_point) is None
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, mission_snapshot)
    _assert_snapshot_is_preserved(
        other_mission, other_robot, other_waste_item, collection_point, other_snapshot
    )


def test_pending_mission_with_an_executing_robot_preserves_participants() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    unrelated_robot = Robot(RobotIdentity("robot-2"), COLLECTION_POINT_POSITION, BatteryLevel(1))
    pending_mission = unrelated_robot.create_cleaning_mission(CleaningMissionIdentity("mission-2"))
    assert isinstance(pending_mission, CleaningMission)
    collection_point = _collection_point()
    snapshot = _snapshot(mission, robot, waste_item, collection_point)
    pending_snapshot = _snapshot(pending_mission, unrelated_robot, waste_item, collection_point)

    assert deposit_collected_waste(pending_mission, robot, collection_point) is None

    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)
    _assert_snapshot_is_preserved(
        pending_mission, unrelated_robot, waste_item, collection_point, pending_snapshot
    )


def test_compatible_collection_point_is_read_only_and_rejects_invalid_runtime_values() -> None:
    collection_point = _collection_point()

    assert collection_point.position is COLLECTION_POINT_POSITION
    assert collection_point.accepted_categories == frozenset({WasteCategory.PLASTIC})
    assert collection_point.accepts(WasteCategory.PLASTIC) is True
    assert collection_point.accepts(WasteCategory.PAPER) is False
    position_attribute = "position"
    accepted_categories_attribute = "accepted_categories"
    with pytest.raises(AttributeError):
        setattr(collection_point, position_attribute, WASTE_POSITION)
    with pytest.raises(AttributeError):
        setattr(collection_point, accepted_categories_attribute, frozenset())
    with pytest.raises(TypeError):
        CompatibleCollectionPoint(
            cast(Position, "not a Position"), frozenset({WasteCategory.PLASTIC})
        )
    with pytest.raises(TypeError):
        CompatibleCollectionPoint(
            COLLECTION_POINT_POSITION, cast(frozenset[WasteCategory], {WasteCategory.PLASTIC})
        )
    with pytest.raises(TypeError):
        CompatibleCollectionPoint(
            COLLECTION_POINT_POSITION, cast(frozenset[WasteCategory], frozenset({"plastic"}))
        )
    with pytest.raises(TypeError):
        collection_point.accepts(cast(WasteCategory, "plastic"))


def test_deposit_rejects_forged_collection_point_robot_and_position_subclasses() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    collection_point = _collection_point()
    snapshot = _snapshot(mission, robot, waste_item, collection_point)

    with pytest.raises(TypeError):
        CompatibleCollectionPoint(ForgedPosition(2, 0), frozenset({WasteCategory.PLASTIC}))
    with pytest.raises(TypeError):
        deposit_collected_waste(
            mission, robot, ForgedCollectionPoint(COLLECTION_POINT_POSITION, frozenset())
        )
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)

    forged_robot = ForgedRobot(RobotIdentity("robot-2"), COLLECTION_POINT_POSITION, BatteryLevel(1))
    forged_mission = forged_robot.create_cleaning_mission(CleaningMissionIdentity("mission-2"))
    assert isinstance(forged_mission, CleaningMission)
    assert start_cleaning_mission(forged_mission, forged_robot) is None
    forged_snapshot = _snapshot(forged_mission, forged_robot, waste_item, collection_point)

    with pytest.raises(TypeError):
        deposit_collected_waste(forged_mission, forged_robot, collection_point)
    _assert_snapshot_is_preserved(
        forged_mission, forged_robot, waste_item, collection_point, forged_snapshot
    )


def test_deposit_rejects_forged_robot_position_before_invoking_its_equality() -> None:
    robot_position = Position(8, 9)
    waste_position = Position(9, 9)
    forged_position = ForgedPosition(10, 9)
    collection_point = CompatibleCollectionPoint(
        COLLECTION_POINT_POSITION, frozenset({WasteCategory.PLASTIC})
    )
    robot = Robot(RobotIdentity("robot-1"), robot_position, BatteryLevel(3))
    mission = robot.create_cleaning_mission(CleaningMissionIdentity("mission-1"))
    assert isinstance(mission, CleaningMission)
    assert start_cleaning_mission(mission, robot) is None
    waste_item = WasteItem(waste_position)
    waste_item.classify(WasteCategory.PLASTIC)
    environment = SimulatedEnvironment(Position(0, 0), forged_position, frozenset())
    route_to_waste = validate_supplied_route(
        environment, robot_position, waste_position, (robot_position, waste_position)
    )
    assert route_to_waste is not None
    waste_item.target(route_to_waste)
    assert robot.follow_validated_route(route_to_waste) is None
    assert collect_targeted_waste(robot, waste_item) is None
    route_to_forged_position = validate_supplied_route(
        environment, waste_position, forged_position, (waste_position, forged_position)
    )
    assert route_to_forged_position is not None
    assert robot.follow_validated_route(route_to_forged_position) is None
    assert robot.position is forged_position
    ForgedPosition.equality_calls = 0
    snapshot = _snapshot(mission, robot, waste_item, collection_point)

    with pytest.raises(TypeError):
        deposit_collected_waste(mission, robot, collection_point)

    assert ForgedPosition.equality_calls == 0
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)


def test_deposit_rejects_forged_mission_before_its_property_can_start_a_mission() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))
    collection_point = _collection_point()
    pending_robot = Robot(RobotIdentity("robot-2"), Position(3, 0), BatteryLevel(1))
    pending_mission = pending_robot.create_cleaning_mission(CleaningMissionIdentity("mission-2"))
    assert isinstance(pending_mission, CleaningMission)
    forged_mission = ForgedCleaningMission(pending_mission, pending_robot)
    snapshot = _snapshot(mission, robot, waste_item, collection_point)
    pending_snapshot = _snapshot(pending_mission, pending_robot, waste_item, collection_point)

    with pytest.raises(TypeError):
        deposit_collected_waste(forged_mission, robot, collection_point)

    assert pending_mission.state is MissionState.PENDING
    assert pending_robot.operational_state is RobotOperationalState.AVAILABLE
    _assert_snapshot_is_preserved(mission, robot, waste_item, collection_point, snapshot)
    _assert_snapshot_is_preserved(
        pending_mission, pending_robot, waste_item, collection_point, pending_snapshot
    )


def test_deposit_has_no_normal_public_half_transition_or_coordination_bypass() -> None:
    mission, robot, waste_item = _collected_waste_participants(BatteryLevel(3))

    assert not hasattr(waste_item, "deposit")
    assert not hasattr(waste_item, "move_to_collection_point")
    assert not hasattr(robot, "remove_carried_waste_item")
    assert not hasattr(robot, "deposit_together")
    assert not hasattr(mission, "deposit_together")
