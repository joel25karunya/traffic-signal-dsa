"""
Fixed-time round-robin traffic signal scheduler for baseline comparison.
"""
from typing import Dict, List, Optional, Tuple
from src.models import Direction, PhaseRecord, SimulationConfig
from src.queue_manager import IntersectionQueueManager


class FixedTimeScheduler:
    """
    Simulates a traditional pre-timed (fixed-time) signal controller.
    Cycles through approaches in strict sequential order (North -> East -> South -> West),
    allocating a constant green duration regardless of actual traffic demand.
    """

    CYCLE_ORDER: List[Direction] = [
        Direction.NORTH,
        Direction.EAST,
        Direction.SOUTH,
        Direction.WEST,
    ]

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config: SimulationConfig = config or SimulationConfig()
        self.current_cycle_index: int = 0
        self.phase_counter: int = 0

    def reset(self) -> None:
        """Resets cycle pointer and phase counter."""
        self.current_cycle_index = 0
        self.phase_counter = 0

    def step_phase(
        self,
        queue_mgr: IntersectionQueueManager,
        sim_time: float
    ) -> Tuple[PhaseRecord, List]:
        """
        Executes one signal phase under fixed-time round-robin scheduling.
        
        Returns:
            Tuple of (PhaseRecord, list_of_departed_vehicles)
        """
        self.phase_counter += 1
        selected_dir = self.CYCLE_ORDER[self.current_cycle_index]
        self.current_cycle_index = (self.current_cycle_index + 1) % len(self.CYCLE_ORDER)

        green_duration = self.config.fixed_green_duration
        target_queue = queue_mgr.get_queue(selected_dir)

        # Snapshot before service
        lengths_before = queue_mgr.get_all_queue_lengths()
        avg_waits_before = queue_mgr.get_all_average_waits(sim_time)
        max_waits_before = queue_mgr.get_all_max_waits(sim_time)
        had_emg = target_queue.has_emergency()

        # Vehicles served is bounded by available green duration and queue size
        capacity = max(1, int(green_duration / max(0.1, self.config.seconds_per_vehicle)))
        departed_vehicles = target_queue.dequeue_batch(capacity, current_time=sim_time + green_duration)
        vehicles_served = len(departed_vehicles)

        lengths_after = queue_mgr.get_all_queue_lengths()

        # Fixed time does not compute dynamic priority, but we record uniform score
        scores = {d.value: 1.0 if d == selected_dir else 0.0 for d in Direction.all_directions()}

        record = PhaseRecord(
            phase_number=self.phase_counter,
            simulated_timestamp=sim_time,
            selected_direction=selected_dir,
            green_duration=green_duration,
            vehicles_served=vehicles_served,
            queue_lengths_before=lengths_before,
            queue_lengths_after=lengths_after,
            priority_scores=scores,
            avg_wait_times=avg_waits_before,
            max_wait_times=max_waits_before,
            had_emergency=had_emg,
            scheduler_type="Fixed-Time",
            decision_reason=f"Round-robin cyclic order: Approach {selected_dir.value} allocated fixed {green_duration}s."
        )

        return record, departed_vehicles
