"""
Unit tests for CSV and JSON data export functionality.
"""
import json
import pytest
from src.models import Direction, PhaseRecord, Vehicle
from src.metrics import IntersectionSummaryMetrics
from src.data_export import SimulationDataExporter


def test_csv_phases_export():
    """Verify phase history exports correctly to CSV."""
    p1 = PhaseRecord(
        phase_number=1,
        simulated_timestamp=10.0,
        selected_direction=Direction.NORTH,
        green_duration=20,
        vehicles_served=5,
        queue_lengths_before={"North": 5, "East": 2, "South": 0, "West": 1},
        queue_lengths_after={"North": 0, "East": 2, "South": 0, "West": 1},
        priority_scores={"North": 15.0, "East": 3.0, "South": 0.0, "West": 1.0},
        avg_wait_times={"North": 5.0, "East": 2.0, "South": 0.0, "West": 1.0},
        max_wait_times={"North": 10.0, "East": 4.0, "South": 0.0, "West": 2.0},
        had_emergency=False,
        scheduler_type="Dynamic",
        decision_reason="Highest queue length"
    )

    csv_data = SimulationDataExporter.export_phases_to_csv([p1])
    lines = csv_data.strip().split("\r\n") if "\r\n" in csv_data else csv_data.strip().split("\n")
    assert len(lines) == 2  # Header + 1 record
    assert "phase_number" in lines[0]
    assert "North" in lines[1]
    assert "Dynamic" in lines[1]


def test_json_summary_export():
    """Verify JSON export produces valid JSON structure with metrics."""
    summary = IntersectionSummaryMetrics(
        total_vehicles_arrived=20,
        total_vehicles_served=15,
        total_vehicles_waiting=5,
        average_waiting_time_served=12.5,
        max_waiting_time_served=25.0,
        max_queue_recorded=8,
        total_simulated_time=150.0,
        total_phases_completed=5,
        throughput_per_minute=6.0,
        throughput_per_second=0.1
    )

    json_str = SimulationDataExporter.export_summary_to_json(summary, [], metadata={"test": "run1"})
    parsed = json.loads(json_str)

    assert parsed["metadata"]["test"] == "run1"
    assert parsed["summary_metrics"]["total_vehicles_served"] == 15
    assert parsed["summary_metrics"]["average_waiting_time_served"] == 12.5
    assert parsed["summary_metrics"]["throughput_per_minute"] == 6.0
