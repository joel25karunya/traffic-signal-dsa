"""
Metrics calculation, time-series history tracking, and performance analytics.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from src.models import Direction, PhaseRecord, Vehicle


@dataclass
class IntersectionSummaryMetrics:
    """Consolidated snapshot of intersection performance metrics."""
    total_vehicles_arrived: int = 0
    total_vehicles_served: int = 0
    total_vehicles_waiting: int = 0
    average_waiting_time_served: float = 0.0
    max_waiting_time_served: float = 0.0
    current_avg_waiting_time: float = 0.0
    current_max_waiting_time: float = 0.0
    max_queue_recorded: int = 0
    total_simulated_time: float = 0.0
    total_phases_completed: int = 0
    throughput_per_minute: float = 0.0
    throughput_per_second: float = 0.0
    served_per_direction: Dict[str, int] = field(default_factory=dict)
    arrived_per_direction: Dict[str, int] = field(default_factory=dict)
    green_time_per_direction: Dict[str, int] = field(default_factory=dict)


class SimulationMetricsTracker:
    """
    Maintains historical time-series data and computes traffic performance statistics.
    Tracks individual vehicle wait times accurately and avoids approximations.
    """

    def __init__(self):
        self.departed_vehicles: List[Vehicle] = []
        self.phase_history: List[PhaseRecord] = []
        self.timeline_points: List[Dict] = []
        
        # Per-direction counters
        self.arrived_counts: Dict[Direction, int] = {d: 0 for d in Direction.all_directions()}
        self.served_counts: Dict[Direction, int] = {d: 0 for d in Direction.all_directions()}
        self.green_seconds: Dict[Direction, int] = {d: 0 for d in Direction.all_directions()}
        self.max_queue_seen: int = 0

    def reset(self) -> None:
        """Resets all metrics history."""
        self.departed_vehicles.clear()
        self.phase_history.clear()
        self.timeline_points.clear()
        self.arrived_counts = {d: 0 for d in Direction.all_directions()}
        self.served_counts = {d: 0 for d in Direction.all_directions()}
        self.green_seconds = {d: 0 for d in Direction.all_directions()}
        self.max_queue_seen = 0

    def record_arrival(self, vehicle: Vehicle) -> None:
        """Tracks arrival count per direction."""
        self.arrived_counts[vehicle.direction] += 1

    def record_phase(
        self,
        record: PhaseRecord,
        departed: List[Vehicle],
        current_waiting_count: int,
        current_max_wait: float
    ) -> None:
        """
        Records the completion of a signal phase and updates metrics.
        """
        self.phase_history.append(record)
        self.departed_vehicles.extend(departed)

        # Update served counts and green seconds
        self.served_counts[record.selected_direction] += record.vehicles_served
        self.green_seconds[record.selected_direction] += record.green_duration

        # Track peak queue length
        for length in record.queue_lengths_before.values():
            if length > self.max_queue_seen:
                self.max_queue_seen = length

        # Record snapshot in time-series
        avg_wait_so_far = self.compute_average_wait_served()
        self.timeline_points.append({
            "phase": record.phase_number,
            "sim_time": record.simulated_timestamp,
            "direction": record.selected_direction.value,
            "green_duration": record.green_duration,
            "vehicles_served": record.vehicles_served,
            "waiting_vehicles": current_waiting_count,
            "avg_wait_time": avg_wait_so_far,
            "current_max_wait": current_max_wait,
            "North_queue": record.queue_lengths_after.get(Direction.NORTH.value, 0),
            "East_queue": record.queue_lengths_after.get(Direction.EAST.value, 0),
            "South_queue": record.queue_lengths_after.get(Direction.SOUTH.value, 0),
            "West_queue": record.queue_lengths_after.get(Direction.WEST.value, 0),
        })

    def compute_average_wait_served(self) -> float:
        """Computes true average waiting time across all vehicles that have departed."""
        if not self.departed_vehicles:
            return 0.0
        total_wait = sum(v.wait_time for v in self.departed_vehicles if v.wait_time is not None)
        return total_wait / len(self.departed_vehicles)

    def compute_max_wait_served(self) -> float:
        """Finds maximum waiting time among all vehicles that have departed."""
        if not self.departed_vehicles:
            return 0.0
        return max((v.wait_time for v in self.departed_vehicles if v.wait_time is not None), default=0.0)

    def get_summary(
        self,
        current_sim_time: float,
        current_waiting_count: int,
        current_avg_wait: float,
        current_max_wait: float
    ) -> IntersectionSummaryMetrics:
        """
        Assembles consolidated summary metrics.
        """
        total_served = len(self.departed_vehicles)
        total_arrived = sum(self.arrived_counts.values())

        # Safe throughput calculation
        throughput_sec = (total_served / current_sim_time) if current_sim_time > 0 else 0.0
        throughput_min = throughput_sec * 60.0

        return IntersectionSummaryMetrics(
            total_vehicles_arrived=total_arrived,
            total_vehicles_served=total_served,
            total_vehicles_waiting=current_waiting_count,
            average_waiting_time_served=self.compute_average_wait_served(),
            max_waiting_time_served=self.compute_max_wait_served(),
            current_avg_waiting_time=current_avg_wait,
            current_max_waiting_time=current_max_wait,
            max_queue_recorded=self.max_queue_seen,
            total_simulated_time=current_sim_time,
            total_phases_completed=len(self.phase_history),
            throughput_per_minute=throughput_min,
            throughput_per_second=throughput_sec,
            served_per_direction={d.value: self.served_counts[d] for d in Direction.all_directions()},
            arrived_per_direction={d.value: self.arrived_counts[d] for d in Direction.all_directions()},
            green_time_per_direction={d.value: self.green_seconds[d] for d in Direction.all_directions()},
        )
