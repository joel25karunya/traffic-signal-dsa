"""
Priority calculation and Priority Queue (Heapq) implementation for dynamic signal scheduling.
"""
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from src.models import Direction, SimulationConfig
from src.queue_manager import IntersectionQueueManager


@dataclass
class PriorityBreakdown:
    """Detailed score components for algorithmic transparency and educational visualization."""
    direction: Direction
    queue_length: int
    queue_contribution: float
    max_wait_time: float
    wait_contribution: float
    emergency_bonus: float
    is_emergency: bool
    starvation_bonus: float
    is_starving: bool
    total_score: float
    tie_breaker_order: int
    explanation: str


class PriorityQueueScheduler:
    """
    Computes priority scores for all approaches and selects the optimal direction
    using Python's `heapq` priority queue data structure with deterministic tie-breaking.
    
    Priority Formula:
        score = (queue_length * queue_weight)
              + (max_wait_time * waiting_weight)
              + (emergency_bonus if has_emergency and emergency_enabled else 0.0)
              + (starvation_bonus if max_wait_time >= starvation_threshold else 0.0)
              
    Complexity Analysis:
    - Priority evaluation for all approaches: O(M) where M is number of approaches (M=4).
    - Heap build / heapify: O(M)
    - Heap pop (selecting highest priority): O(log M)
    - Total phase selection complexity: O(M log M), which is O(1) for fixed M=4.
    """

    # Deterministic tie-breaker index mapping: North (0), East (1), South (2), West (3)
    TIE_BREAKER_ORDER: Dict[Direction, int] = {
        Direction.NORTH: 0,
        Direction.EAST: 1,
        Direction.SOUTH: 2,
        Direction.WEST: 3,
    }

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config: SimulationConfig = config or SimulationConfig()

    def update_config(self, config: SimulationConfig) -> None:
        """Updates algorithm tuning parameters."""
        self.config = config

    def calculate_direction_priority(
        self,
        direction: Direction,
        queue_mgr: IntersectionQueueManager,
        current_time: float
    ) -> PriorityBreakdown:
        """
        Calculates priority score and detailed breakdown for a single direction.
        """
        q = queue_mgr.get_queue(direction)
        q_len = len(q)
        max_wait = q.max_waiting_time(current_time) if q_len > 0 else 0.0

        # Term 1: Queue length component
        queue_contrib = q_len * self.config.queue_weight

        # Term 2: Waiting time component
        wait_contrib = max_wait * self.config.waiting_time_weight

        # Term 3: Emergency bonus
        has_emg = q.has_emergency()
        emg_active = has_emg and self.config.enable_emergency
        emg_bonus = self.config.emergency_bonus if emg_active else 0.0

        # Term 4: Starvation prevention bonus
        is_starving = q_len > 0 and (max_wait >= self.config.starvation_threshold_seconds)
        starv_bonus = self.config.starvation_bonus if is_starving else 0.0

        total_score = queue_contrib + wait_contrib + emg_bonus + starv_bonus
        tie_order = self.TIE_BREAKER_ORDER[direction]

        # Human-readable explanation of how this score was constructed
        reasons = [
            f"Queue: {q_len} × {self.config.queue_weight:.1f} = {queue_contrib:.1f}",
            f"MaxWait: {max_wait:.1f}s × {self.config.waiting_time_weight:.1f} = {wait_contrib:.1f}"
        ]
        if emg_active:
            reasons.append(f"EMERGENCY BONUS: +{emg_bonus:.1f}")
        if is_starving:
            reasons.append(f"STARVATION PREVENT: +{starv_bonus:.1f} (waited > {self.config.starvation_threshold_seconds:.0f}s)")

        explanation = "; ".join(reasons)

        return PriorityBreakdown(
            direction=direction,
            queue_length=q_len,
            queue_contribution=queue_contrib,
            max_wait_time=max_wait,
            wait_contribution=wait_contrib,
            emergency_bonus=emg_bonus,
            is_emergency=emg_active,
            starvation_bonus=starv_bonus,
            is_starving=is_starving,
            total_score=total_score,
            tie_breaker_order=tie_order,
            explanation=explanation,
        )

    def evaluate_all_directions(
        self,
        queue_mgr: IntersectionQueueManager,
        current_time: float
    ) -> Dict[Direction, PriorityBreakdown]:
        """Calculates priority breakdowns for all four directions."""
        return {
            d: self.calculate_direction_priority(d, queue_mgr, current_time)
            for d in Direction.all_directions()
        }

    def select_next_direction_heap(
        self,
        queue_mgr: IntersectionQueueManager,
        current_time: float,
        last_direction: Optional[Direction] = None
    ) -> Tuple[Optional[Direction], List[PriorityBreakdown], Optional[str]]:
        """
        Uses Python's heapq to select the highest priority eligible direction.
        
        An eligible direction MUST have at least 1 waiting vehicle (queue_length > 0).
        If all queues are empty, returns (None, breakdowns, reason).
        
        Returns:
            Tuple of:
            - Selected Direction (or None if intersection is empty)
            - List of PriorityBreakdown for all directions
            - Explanation string describing the selection decision
        """
        breakdowns = self.evaluate_all_directions(queue_mgr, current_time)
        breakdown_list = list(breakdowns.values())

        # Construct max-heap using heapq.
        # Since heapq is a min-heap, we push (-total_score, tie_order, direction)
        # This guarantees:
        # 1. Largest total_score popped first
        # 2. Ties broken deterministically by tie_breaker_order (North < East < South < West)
        heap_entries = []
        for d, b in breakdowns.items():
            if b.queue_length > 0:  # Only eligible directions
                # Tuple: (-score, tie_order, direction_enum)
                heap_entries.append((-b.total_score, b.tie_breaker_order, d))

        if not heap_entries:
            return None, breakdown_list, "All intersection queues are currently empty. Signals remain in idle red clearance."

        heapq.heapify(heap_entries)
        neg_score, tie_order, best_direction = heapq.heappop(heap_entries)
        best_breakdown = breakdowns[best_direction]

        # Formulate reason
        reason_parts = [f"Selected {best_direction.value} with priority score {best_breakdown.total_score:.2f}."]
        if best_breakdown.is_emergency:
            reason_parts.append("Emergency vehicle preemption active!")
        elif best_breakdown.is_starving:
            reason_parts.append(f"Starvation override active (waited {best_breakdown.max_wait_time:.1f}s).")
        else:
            reason_parts.append(f"Queue: {best_breakdown.queue_length} veh, Max wait: {best_breakdown.max_wait_time:.1f}s.")

        decision_reason = " ".join(reason_parts)
        return best_direction, breakdown_list, decision_reason
