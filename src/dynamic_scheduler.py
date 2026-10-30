"""
Dynamic adaptive priority scheduler using greedy selection, priority queues, and starvation prevention.
"""
from typing import Dict, List, Optional, Tuple
from src.models import Direction, PhaseRecord, SimulationConfig
from src.queue_manager import IntersectionQueueManager
from src.priority_scheduler import PriorityQueueScheduler, PriorityBreakdown


class DynamicScheduler:
    """
    Intelligent dynamic scheduler allocating green signal duration adaptively
    based on real-time vehicle queues, accumulated waiting times, emergency vehicles,
    and starvation prevention thresholds.
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config: SimulationConfig = config or SimulationConfig()
        self.pq_scheduler: PriorityQueueScheduler = PriorityQueueScheduler(self.config)
        self.phase_counter: int = 0
        self.last_served_direction: Optional[Direction] = None

    def update_config(self, config: SimulationConfig) -> None:
        """Propagates updated configuration to priority calculator."""
        self.config = config
        self.pq_scheduler.update_config(config)

    def reset(self) -> None:
        """Resets phase counter and state."""
        self.phase_counter = 0
        self.last_served_direction = None

    def calculate_adaptive_green_duration(self, queue_length: int, has_emergency: bool = False) -> int:
        """
        Calculates green light duration dynamically from queue length and service rate.
        
        Formula:
            green_duration = clamp(
                round(min_green_time + (queue_length * seconds_per_vehicle)),
                min_green_time,
                max_green_time
            )
        """
        if queue_length <= 0:
            return self.config.min_green_time

        # Service rate formula: each vehicle needs roughly `seconds_per_vehicle` seconds
        estimated_seconds = self.config.min_green_time + int(round(queue_length * self.config.seconds_per_vehicle))

        # If emergency vehicle is present, ensure sufficient green window to clear queue
        if has_emergency and self.config.enable_emergency:
            estimated_seconds = max(estimated_seconds, self.config.min_green_time * 2)

        clamped = max(self.config.min_green_time, min(self.config.max_green_time, estimated_seconds))
        return clamped

    def step_phase(
        self,
        queue_mgr: IntersectionQueueManager,
        sim_time: float
    ) -> Tuple[PhaseRecord, List, List[PriorityBreakdown]]:
        """
        Executes one dynamic signal phase:
        1. Evaluates all approaches and selects highest priority via Priority Queue (heapq).
        2. Calculates adaptive green light duration.
        3. Dequeues vehicles up to service capacity.
        4. Logs phase metrics and algorithmic reasoning.
        
        Returns:
            Tuple of:
            - PhaseRecord
            - List of departed Vehicle instances
            - List of PriorityBreakdown for educational UI display
        """
        self.phase_counter += 1

        # Snapshot before service
        lengths_before = queue_mgr.get_all_queue_lengths()
        avg_waits_before = queue_mgr.get_all_average_waits(sim_time)
        max_waits_before = queue_mgr.get_all_max_waits(sim_time)

        # Step 1 & 2: Select direction using Priority Queue with tie-breaking
        selected_dir, breakdowns, reason = self.pq_scheduler.select_next_direction_heap(
            queue_mgr, sim_time, self.last_served_direction
        )

        scores_dict = {b.direction.value: round(b.total_score, 2) for b in breakdowns}

        if selected_dir is None:
            # Intersection is completely empty
            green_duration = self.config.min_green_time
            record = PhaseRecord(
                phase_number=self.phase_counter,
                simulated_timestamp=sim_time,
                selected_direction=Direction.NORTH,  # Default idle
                green_duration=green_duration,
                vehicles_served=0,
                queue_lengths_before=lengths_before,
                queue_lengths_after=lengths_before,
                priority_scores=scores_dict,
                avg_wait_times=avg_waits_before,
                max_wait_times=max_waits_before,
                had_emergency=False,
                scheduler_type="Dynamic-Priority",
                decision_reason="All queues are empty; holding minimum idle interval."
            )
            return record, [], breakdowns

        self.last_served_direction = selected_dir
        target_queue = queue_mgr.get_queue(selected_dir)
        had_emg = target_queue.has_emergency()
        initial_q_len = len(target_queue)

        # Step 3: Adaptive green duration
        green_duration = self.calculate_adaptive_green_duration(initial_q_len, has_emergency=had_emg)

        # Step 4: Service vehicles
        capacity = max(1, int(green_duration / max(0.1, self.config.seconds_per_vehicle)))
        departed_vehicles = target_queue.dequeue_batch(capacity, current_time=sim_time + green_duration)
        vehicles_served = len(departed_vehicles)

        lengths_after = queue_mgr.get_all_queue_lengths()

        record = PhaseRecord(
            phase_number=self.phase_counter,
            simulated_timestamp=sim_time,
            selected_direction=selected_dir,
            green_duration=green_duration,
            vehicles_served=vehicles_served,
            queue_lengths_before=lengths_before,
            queue_lengths_after=lengths_after,
            priority_scores=scores_dict,
            avg_wait_times=avg_waits_before,
            max_wait_times=max_waits_before,
            had_emergency=had_emg,
            scheduler_type="Dynamic-Priority",
            decision_reason=reason
        )

        return record, departed_vehicles, breakdowns
