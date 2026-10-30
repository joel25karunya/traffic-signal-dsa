"""
Unit tests for Priority Queue, Dynamic Scheduler, and Fixed-Time Scheduler.
"""
import pytest
from src.models import Direction, SimulationConfig, Vehicle
from src.queue_manager import IntersectionQueueManager
from src.priority_scheduler import PriorityQueueScheduler
from src.dynamic_scheduler import DynamicScheduler
from src.fixed_time_scheduler import FixedTimeScheduler


def test_priority_score_calculation():
    """Verify exact priority calculation against manual calculation."""
    config = SimulationConfig(
        queue_weight=1.5,
        waiting_time_weight=0.5,
        emergency_bonus=100.0,
        starvation_threshold_seconds=60.0,
        starvation_bonus=50.0
    )
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # Add 10 vehicles to North arriving at t=0
    for i in range(10):
        iqm.enqueue_vehicle(Vehicle(id=f"N-{i}", direction=Direction.NORTH, arrival_time=0.0))

    # At t=20s: queue_length=10, max_wait=20.0
    # Expected: (10 * 1.5) + (20 * 0.5) + 0 + 0 = 15.0 + 10.0 = 25.0
    breakdown = pq.calculate_direction_priority(Direction.NORTH, iqm, current_time=20.0)
    assert breakdown.queue_length == 10
    assert breakdown.max_wait_time == 20.0
    assert breakdown.queue_contribution == 15.0
    assert breakdown.wait_contribution == 10.0
    assert breakdown.total_score == 25.0
    assert not breakdown.is_emergency
    assert not breakdown.is_starving


def test_heap_selection_and_empty_handling():
    """Verify heapq selects the highest priority approach and handles empty queues safely."""
    config = SimulationConfig(queue_weight=1.0, waiting_time_weight=0.1)
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # Case 1: Empty intersection
    selected, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=0.0)
    assert selected is None
    assert "empty" in reason.lower()

    # Case 2: Only South has vehicles
    iqm.enqueue_vehicle(Vehicle(id="S1", direction=Direction.SOUTH, arrival_time=0.0))
    selected, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=10.0)
    assert selected == Direction.SOUTH

    # Case 3: North has 10 vehicles, South has 1 vehicle, East and West empty
    for i in range(10):
        iqm.enqueue_vehicle(Vehicle(id=f"N-{i}", direction=Direction.NORTH, arrival_time=5.0))

    selected, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=15.0)
    assert selected == Direction.NORTH


def test_deterministic_tie_breaking():
    """Verify deterministic tie-breaking: North (0) < East (1) < South (2) < West (3)."""
    config = SimulationConfig(queue_weight=1.0, waiting_time_weight=1.0)
    pq = PriorityQueueScheduler(config)
    iqm = IntersectionQueueManager()

    # Both North and East have identical queues (1 vehicle, arrived at t=0)
    iqm.enqueue_vehicle(Vehicle(id="N1", direction=Direction.NORTH, arrival_time=0.0))
    iqm.enqueue_vehicle(Vehicle(id="E1", direction=Direction.EAST, arrival_time=0.0))

    # At t=10, both have score = (1*1) + (10*1) = 11.0
    selected, breakdowns, reason = pq.select_next_direction_heap(iqm, current_time=10.0)
    # North should win tie-break over East
    assert selected == Direction.NORTH

    # Test between South and East
    iqm2 = IntersectionQueueManager()
    iqm2.enqueue_vehicle(Vehicle(id="S1", direction=Direction.SOUTH, arrival_time=0.0))
    iqm2.enqueue_vehicle(Vehicle(id="E1", direction=Direction.EAST, arrival_time=0.0))
    selected2, _, _ = pq.select_next_direction_heap(iqm2, current_time=10.0)
    # East (order 1) should win tie-break over South (order 2)
    assert selected2 == Direction.EAST


def test_adaptive_green_duration_clamping():
    """Verify adaptive green times are clamped between min_green and max_green."""
    config = SimulationConfig(min_green_time=10, max_green_time=30, seconds_per_vehicle=2.0)
    dyn = DynamicScheduler(config)

    # 0 vehicles -> min_green (10)
    assert dyn.calculate_adaptive_green_duration(0) == 10

    # 3 vehicles -> 10 + round(3 * 2.0) = 16 (within limits)
    assert dyn.calculate_adaptive_green_duration(3) == 16

    # 50 vehicles -> 10 + round(50 * 2.0) = 110 -> clamped to 30 (max_green)
    assert dyn.calculate_adaptive_green_duration(50) == 30


def test_fixed_time_scheduler_cycle_order():
    """Verify FixedTimeScheduler cycles North -> East -> South -> West consistently."""
    config = SimulationConfig(fixed_green_duration=20)
    fixed = FixedTimeScheduler(config)
    iqm = IntersectionQueueManager()

    # Step 1: North
    rec1, _ = fixed.step_phase(iqm, sim_time=0.0)
    assert rec1.selected_direction == Direction.NORTH
    assert rec1.green_duration == 20

    # Step 2: East
    rec2, _ = fixed.step_phase(iqm, sim_time=25.0)
    assert rec2.selected_direction == Direction.EAST

    # Step 3: South
    rec3, _ = fixed.step_phase(iqm, sim_time=50.0)
    assert rec3.selected_direction == Direction.SOUTH

    # Step 4: West
    rec4, _ = fixed.step_phase(iqm, sim_time=75.0)
    assert rec4.selected_direction == Direction.WEST

    # Step 5: Loops back to North
    rec5, _ = fixed.step_phase(iqm, sim_time=100.0)
    assert rec5.selected_direction == Direction.NORTH
