"""
Queue management module implementing FIFO queues using collections.deque for each intersection approach.
"""
from collections import deque
from typing import Dict, List, Optional, Tuple
from src.models import Direction, Vehicle, VehicleType


class DirectionQueue:
    """
    Manages a single FIFO queue for one approach direction (North, South, East, West).
    
    Time Complexities:
    - Enqueue: O(1) amortized
    - Dequeue: O(1)
    - Queue length: O(1)
    - Peek: O(1)
    """

    def __init__(self, direction: Direction):
        self.direction: Direction = direction
        self._queue: deque[Vehicle] = deque()
        self.total_enqueued: int = 0
        self.total_dequeued: int = 0
        self.max_queue_recorded: int = 0

    def enqueue(self, vehicle: Vehicle) -> None:
        """
        Adds a vehicle to the back of the FIFO queue.
        
        Args:
            vehicle: Vehicle instance with unique ID and arrival timestamp.
        """
        self._queue.append(vehicle)
        self.total_enqueued += 1
        if len(self._queue) > self.max_queue_recorded:
            self.max_queue_recorded = len(self._queue)

    def dequeue(self, current_time: float) -> Optional[Vehicle]:
        """
        Removes and returns the front vehicle from the queue (FIFO order).
        Marks departure timestamp and computes wait time.
        
        Returns:
            The departing Vehicle or None if the queue is empty.
        """
        if not self._queue:
            return None
        vehicle = self._queue.popleft()
        vehicle.mark_departed(current_time)
        self.total_dequeued += 1
        return vehicle

    def dequeue_batch(self, count: int, current_time: float) -> List[Vehicle]:
        """
        Removes up to `count` vehicles from the front of the queue.
        Safely stops if the queue becomes empty.
        """
        departed: List[Vehicle] = []
        for _ in range(count):
            if not self._queue:
                break
            veh = self.dequeue(current_time)
            if veh:
                departed.append(veh)
        return departed

    def peek(self) -> Optional[Vehicle]:
        """Returns the vehicle at the front of the queue without removing it, or None."""
        return self._queue[0] if self._queue else None

    def __len__(self) -> int:
        """Returns the current number of vehicles waiting."""
        return len(self._queue)

    def is_empty(self) -> bool:
        """Checks if queue has 0 vehicles."""
        return len(self._queue) == 0

    def has_emergency(self) -> bool:
        """Checks if any vehicle currently in queue is an emergency vehicle."""
        return any(v.is_emergency for v in self._queue)

    def emergency_count(self) -> int:
        """Counts how many emergency vehicles are waiting."""
        return sum(1 for v in self._queue if v.is_emergency)

    def get_waiting_times(self, current_time: float) -> List[float]:
        """Computes current waiting durations for all vehicles in this queue."""
        return [v.current_waiting_time(current_time) for v in self._queue]

    def average_waiting_time(self, current_time: float) -> float:
        """Calculates current average waiting time of queued vehicles."""
        if not self._queue:
            return 0.0
        total_wait = sum(v.current_waiting_time(current_time) for v in self._queue)
        return total_wait / len(self._queue)

    def max_waiting_time(self, current_time: float) -> float:
        """Calculates waiting time of the oldest vehicle waiting at the front."""
        if not self._queue:
            return 0.0
        return self._queue[0].current_waiting_time(current_time)

    def oldest_arrival_time(self) -> Optional[float]:
        """Returns arrival time of the vehicle waiting longest (front of queue)."""
        if not self._queue:
            return None
        return self._queue[0].arrival_time

    def get_vehicles(self) -> List[Vehicle]:
        """Returns a snapshot list of currently queued vehicles from front to back."""
        return list(self._queue)

    def clear(self) -> None:
        """Empties the queue and resets counters."""
        self._queue.clear()
        self.total_enqueued = 0
        self.total_dequeued = 0
        self.max_queue_recorded = 0


class IntersectionQueueManager:
    """
    Orchestrates the 4 directional queues for the entire intersection:
    North, South, East, West.
    """

    def __init__(self):
        self.queues: Dict[Direction, DirectionQueue] = {
            d: DirectionQueue(d) for d in Direction.all_directions()
        }

    def enqueue_vehicle(self, vehicle: Vehicle) -> None:
        """Places vehicle into its approach queue."""
        self.queues[vehicle.direction].enqueue(vehicle)

    def get_queue(self, direction: Direction) -> DirectionQueue:
        """Returns queue for specified direction."""
        return self.queues[direction]

    def get_all_queue_lengths(self) -> Dict[str, int]:
        """Returns map of direction name to current queue length."""
        return {d.value: len(q) for d, q in self.queues.items()}

    def get_all_average_waits(self, current_time: float) -> Dict[str, float]:
        """Returns map of direction name to average waiting time."""
        return {d.value: q.average_waiting_time(current_time) for d, q in self.queues.items()}

    def get_all_max_waits(self, current_time: float) -> Dict[str, float]:
        """Returns map of direction name to max waiting time."""
        return {d.value: q.max_waiting_time(current_time) for d, q in self.queues.items()}

    def total_waiting_vehicles(self) -> int:
        """Total number of vehicles currently waiting across all four approaches."""
        return sum(len(q) for q in self.queues.values())

    def max_queue_length(self) -> int:
        """Highest current queue length among all four approaches."""
        if not self.queues:
            return 0
        return max(len(q) for q in self.queues.values())

    def reset(self) -> None:
        """Resets all four queues."""
        for q in self.queues.values():
            q.clear()
