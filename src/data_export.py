"""
Data export module for generating CSV and JSON reports of simulation runs.
"""
import csv
import io
import json
from typing import Any, Dict, List
from src.models import PhaseRecord, Vehicle
from src.metrics import IntersectionSummaryMetrics


class SimulationDataExporter:
    """
    Exports simulation events, vehicle departure logs, and summary statistics
    to standard CSV and JSON formats using pure Python standard library.
    """

    @staticmethod
    def export_phases_to_csv(phases: List[PhaseRecord]) -> str:
        """
        Converts phase history into a structured CSV string.
        """
        output = io.StringIO()
        fieldnames = [
            "phase_number",
            "simulated_timestamp",
            "selected_direction",
            "green_duration_sec",
            "vehicles_served",
            "queue_north_before",
            "queue_east_before",
            "queue_south_before",
            "queue_west_before",
            "queue_north_after",
            "queue_east_after",
            "queue_south_after",
            "queue_west_after",
            "had_emergency",
            "scheduler_type",
            "decision_reason"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for p in phases:
            writer.writerow({
                "phase_number": p.phase_number,
                "simulated_timestamp": round(p.simulated_timestamp, 1),
                "selected_direction": p.selected_direction.value,
                "green_duration_sec": p.green_duration,
                "vehicles_served": p.vehicles_served,
                "queue_north_before": p.queue_lengths_before.get("North", 0),
                "queue_east_before": p.queue_lengths_before.get("East", 0),
                "queue_south_before": p.queue_lengths_before.get("South", 0),
                "queue_west_before": p.queue_lengths_before.get("West", 0),
                "queue_north_after": p.queue_lengths_after.get("North", 0),
                "queue_east_after": p.queue_lengths_after.get("East", 0),
                "queue_south_after": p.queue_lengths_after.get("South", 0),
                "queue_west_after": p.queue_lengths_after.get("West", 0),
                "had_emergency": p.had_emergency,
                "scheduler_type": p.scheduler_type,
                "decision_reason": p.decision_reason
            })

        return output.getvalue()

    @staticmethod
    def export_departed_vehicles_to_csv(vehicles: List[Vehicle]) -> str:
        """
        Converts individual vehicle transit records into CSV string.
        """
        output = io.StringIO()
        fieldnames = [
            "vehicle_id",
            "direction",
            "vehicle_type",
            "is_emergency",
            "arrival_time",
            "departure_time",
            "wait_time_sec"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for v in vehicles:
            writer.writerow({
                "vehicle_id": v.id,
                "direction": v.direction.value,
                "vehicle_type": v.vehicle_type.value,
                "is_emergency": v.is_emergency,
                "arrival_time": round(v.arrival_time, 2),
                "departure_time": round(v.departure_time, 2) if v.departure_time is not None else "",
                "wait_time_sec": round(v.wait_time, 2) if v.wait_time is not None else ""
            })

        return output.getvalue()

    @staticmethod
    def export_summary_to_json(
        summary: IntersectionSummaryMetrics,
        phases: List[PhaseRecord],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Serializes full simulation state and summary to formatted JSON string.
        """
        data = {
            "metadata": metadata,
            "summary_metrics": {
                "total_vehicles_arrived": summary.total_vehicles_arrived,
                "total_vehicles_served": summary.total_vehicles_served,
                "total_vehicles_waiting": summary.total_vehicles_waiting,
                "average_waiting_time_served": round(summary.average_waiting_time_served, 2),
                "max_waiting_time_served": round(summary.max_waiting_time_served, 2),
                "max_queue_recorded": summary.max_queue_recorded,
                "total_simulated_time_sec": round(summary.total_simulated_time, 1),
                "total_phases_completed": summary.total_phases_completed,
                "throughput_per_minute": round(summary.throughput_per_minute, 2),
                "throughput_per_second": round(summary.throughput_per_second, 3),
                "served_per_direction": summary.served_per_direction,
                "arrived_per_direction": summary.arrived_per_direction,
                "green_time_per_direction": summary.green_time_per_direction,
            },
            "phase_count": len(phases),
            "recent_phases": [
                {
                    "phase": p.phase_number,
                    "direction": p.selected_direction.value,
                    "green_duration": p.green_duration,
                    "vehicles_served": p.vehicles_served,
                    "scores": p.priority_scores,
                    "had_emergency": p.had_emergency
                }
                for p in phases[-20:]  # last 20 phases for summary payload
            ]
        }
        return json.dumps(data, indent=2)
