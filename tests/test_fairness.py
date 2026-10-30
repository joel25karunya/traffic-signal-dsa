"""
Tests for starvation prevention mechanism and emergency vehicle priority preemption.
"""
import pytest
from src.models import Direction, SimulationConfig, Vehicle, VehicleType
from src.queue_manager import IntersectionQueueManager
from src.priority_scheduler import PriorityQueueScheduler
from src.dynamic_scheduler import DynamicScheduler


def test_starvation_prevention_override():
    """
    Test that a low-volume approach is not starved indefinitely by a heavy approach
    when its waiting time exceeds the starvation threshold.
    """
    config = SimulationConfig(
        queue_weight=1.0,
        waiting_time_weight=0.1,
        starvation_threshold_seconds=60.0,
        starvation_bonus=80.0
    )
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # Heavy direction: North has 15 vehicles, arrived recently (t=50s)
    for i in range(15):
        iqm.enqueue_vehicle(Vehicle(id=f"N-{i}", direction=Direction.NORTH, arrival_time=50.0))

    # Starving direction: West has only 1 vehicle, arrived early (t=0s)
    iqm.enqueue_vehicle(Vehicle(id="W-1", direction=Direction.WEST, arrival_time=0.0))

    # Scenario A: At t=55s (West wait = 55s < 60s threshold)
    # North score: (15 * 1.0) + ((55 - 50) * 0.1) = 15.0 + 0.5 = 15.5
    # West score: (1 * 1.0) + (55 * 0.1) = 1.0 + 5.5 = 6.5
    # North wins because threshold is not yet exceeded
    sel_before, _, _ = pq.select_next_direction_heap(iqm, current_time=55.0)
    assert sel_before == Direction.NORTH

    # Scenario B: At t=65s (West wait = 65s >= 60s threshold)
    # North score: (15 * 1.0) + ((65 - 50) * 0.1) = 15.0 + 1.5 = 16.5
    # West score: (1 * 1.0) + (65 * 0.1) + 80.0 (starvation bonus!) = 1.0 + 6.5 + 80.0 = 87.5
    # West MUST win due to starvation override!
    sel_after, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=65.0)
    assert sel_after == Direction.WEST
    assert "starvation override active" in reason.lower()


def test_emergency_vehicle_priority():
    """Verify emergency vehicle preemption elevates direction over larger non-emergency queues."""
    config = SimulationConfig(
        queue_weight=1.0,
        waiting_time_weight=0.1,
        emergency_bonus=100.0,
        enable_emergency=True
    )
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # North has 20 regular cars (score = 20 + 0 = 20)
    for i in range(20):
        iqm.enqueue_vehicle(Vehicle(id=f"N-{i}", direction=Direction.NORTH, arrival_time=10.0))

    # East has only 1 ambulance (score = 1 + 0 + 100 = 101)
    iqm.enqueue_vehicle(Vehicle(
        id="AMB-1",
        direction=Direction.EAST,
        arrival_time=10.0,
        is_emergency=True,
        vehicle_type=VehicleType.EMERGENCY
    ))

    sel, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=10.0)
    assert sel == Direction.EAST
    assert "emergency vehicle preemption" in reason.lower()


def test_emergency_vehicle_disabled():
    """Verify emergency bonus is ignored when emergency handling is disabled in config."""
    config = SimulationConfig(
        queue_weight=1.0,
        waiting_time_weight=0.1,
        emergency_bonus=100.0,
        enable_emergency=False  # Disabled!
    )
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # North has 15 regular cars
    for i in range(15):
        iqm.enqueue_vehicle(Vehicle(id=f"N-{i}", direction=Direction.NORTH, arrival_time=10.0))

    # East has 1 emergency vehicle
    iqm.enqueue_vehicle(Vehicle(id="AMB-1", direction=Direction.EAST, arrival_time=10.0, is_emergency=True))

    sel, _, _ = pq.select_next_direction_heap(iqm, current_time=10.0)
    # North has 15 vs East 1, so North should win
    assert sel == Direction.NORTH
