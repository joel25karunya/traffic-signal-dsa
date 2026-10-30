"""
Integration tests for the SimulationEngine, reproducibility, and benchmark fairness.
"""
import pytest
from src.models import Direction, SimulationConfig
from src.simulation import SimulationEngine, run_comparative_benchmark
from src.traffic_engine import TrafficIntensity


def test_simulation_step_and_queue_advancement():
    """Verify single step phase advances simulated time and changes signals."""
    engine = SimulationEngine(scheduler_type="dynamic", seed=42)
    assert engine.state.simulated_time == 0.0
    assert engine.state.current_phase_number == 0

    # Inject vehicles to North
    engine.inject_vehicle(Direction.NORTH, is_emergency=False)
    engine.inject_vehicle(Direction.NORTH, is_emergency=False)

    rec, departed, _ = engine.step_phase(auto_generate_traffic=False)
    assert rec.selected_direction == Direction.NORTH
    assert engine.state.simulated_time > 0.0
    assert engine.state.current_phase_number == 1
    assert engine.state.active_green_direction == Direction.NORTH


def test_seed_reproducibility():
    """Verify identical seeds generate exact same traffic arrival sequences."""
    engine1 = SimulationEngine(scheduler_type="dynamic", seed=999)
    engine2 = SimulationEngine(scheduler_type="dynamic", seed=999)

    arrivals1 = engine1.generate_traffic(intensity=TrafficIntensity.MODERATE)
    arrivals2 = engine2.generate_traffic(intensity=TrafficIntensity.MODERATE)

    assert len(arrivals1) == len(arrivals2)
    for v1, v2 in zip(arrivals1, arrivals2):
        assert v1.id == v2.id
        assert v1.direction == v2.direction
        assert v1.vehicle_type == v2.vehicle_type


def test_simulation_reset_clears_state():
    """Verify reset clears queues, metrics, clock, and counters."""
    engine = SimulationEngine(scheduler_type="dynamic", seed=42)
    engine.inject_vehicle(Direction.EAST)
    engine.step_phase(auto_generate_traffic=False)

    assert engine.queue_mgr.total_waiting_vehicles() >= 0
    assert engine.state.current_phase_number == 1

    engine.reset()
    assert engine.state.simulated_time == 0.0
    assert engine.state.current_phase_number == 0
    assert engine.queue_mgr.total_waiting_vehicles() == 0
    assert len(engine.metrics_tracker.phase_history) == 0


def test_comparative_benchmark_fairness():
    """Verify comparative benchmark feeds identical arrivals to both algorithms."""
    results = run_comparative_benchmark(rounds=6, intensity=TrafficIntensity.MODERATE, seed=123)

    fixed_m = results["fixed"]
    dyn_m = results["dynamic"]

    # Both must have received identical number of total arriving vehicles
    assert fixed_m.total_vehicles_arrived == dyn_m.total_vehicles_arrived
    assert fixed_m.total_vehicles_arrived > 0
    assert "avg_wait_improvement_pct" in results["comparisons"]
    assert "throughput_increase_pct" in results["comparisons"]
