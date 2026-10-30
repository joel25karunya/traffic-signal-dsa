"""
Unit tests for metrics calculation, waiting time tracking, and throughput math.
"""
import pytest
from src.models import Direction, PhaseRecord, Vehicle
from src.metrics import SimulationMetricsTracker


def test_vehicle_waiting_time_and_metrics_averages():
    """Verify average and maximum waiting times match manually calculated values."""
    tracker = SimulationMetricsTracker()

    v1 = Vehicle(id="V1", direction=Direction.NORTH, arrival_time=10.0)
    v2 = Vehicle(id="V2", direction=Direction.NORTH, arrival_time=20.0)
    v3 = Vehicle(id="V3", direction=Direction.NORTH, arrival_time=30.0)

    # Departures at simulated time t=50.0
    v1.mark_departed(50.0)  # Wait: 40.0
    v2.mark_departed(50.0)  # Wait: 30.0
    v3.mark_departed(50.0)  # Wait: 20.0

    phase_record = PhaseRecord(
        phase_number=1,
        simulated_timestamp=50.0,
        selected_direction=Direction.NORTH,
        green_duration=20,
        vehicles_served=3,
        queue_lengths_before={"North": 3, "East": 0, "South": 0, "West": 0},
        queue_lengths_after={"North": 0, "East": 0, "South": 0, "West": 0},
        priority_scores={"North": 10.0, "East": 0.0, "South": 0.0, "West": 0.0},
        avg_wait_times={"North": 30.0, "East": 0.0, "South": 0.0, "West": 0.0},
        max_wait_times={"North": 40.0, "East": 0.0, "South": 0.0, "West": 0.0},
        had_emergency=False,
        scheduler_type="Dynamic"
    )

    tracker.record_arrival(v1)
    tracker.record_arrival(v2)
    tracker.record_arrival(v3)
    tracker.record_phase(phase_record, [v1, v2, v3], current_waiting_count=0, current_max_wait=0.0)

    # Expected average wait: (40 + 30 + 20) / 3 = 30.0
    assert tracker.compute_average_wait_served() == 30.0
    assert tracker.compute_max_wait_served() == 40.0
    assert tracker.served_counts[Direction.NORTH] == 3
    assert tracker.max_queue_seen == 3


def test_throughput_math_and_zero_duration_safety():
    """Verify throughput calculations and safety when simulated time is zero."""
    tracker = SimulationMetricsTracker()

    # Zero duration test
    summary_zero = tracker.get_summary(current_sim_time=0.0, current_waiting_count=0, current_avg_wait=0.0, current_max_wait=0.0)
    assert summary_zero.throughput_per_second == 0.0
    assert summary_zero.throughput_per_minute == 0.0

    # 12 vehicles served over 120 seconds
    # Throughput/sec = 12 / 120 = 0.10 veh/s
    # Throughput/min = 0.10 * 60 = 6.0 veh/min
    for i in range(12):
        veh = Vehicle(id=f"V-{i}", direction=Direction.SOUTH, arrival_time=0.0)
        veh.mark_departed(100.0)
        tracker.departed_vehicles.append(veh)

    summary_120 = tracker.get_summary(current_sim_time=120.0, current_waiting_count=0, current_avg_wait=0.0, current_max_wait=0.0)
    assert pytest.approx(summary_120.throughput_per_second, 0.001) == 0.10
    assert pytest.approx(summary_120.throughput_per_minute, 0.001) == 6.0
