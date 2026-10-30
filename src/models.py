"""
Data models and enumerations for the Intelligent Traffic Signal Management System.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List


class Direction(str, Enum):
    """Four-way intersection approach directions."""
    NORTH = "North"
    EAST = "East"
    SOUTH = "South"
    WEST = "West"

    @classmethod
    def all_directions(cls) -> List["Direction"]:
        return [cls.NORTH, cls.EAST, cls.SOUTH, cls.WEST]

    @property
    def opposite(self) -> "Direction":
        mapping = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return mapping[self]


class SignalState(str, Enum):
    """Traffic signal light states."""
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class VehicleType(str, Enum):
    """Categories of vehicles in simulation."""
    CAR = "Car"
    BUS = "Bus"
    TRUCK = "Truck"
    EMERGENCY = "Emergency"


@dataclass
class Vehicle:
    """Represents a single vehicle arriving at the intersection."""
    id: str
    direction: Direction
    arrival_time: float
    vehicle_type: VehicleType = VehicleType.CAR
    is_emergency: bool = False
    departure_time: Optional[float] = None
    wait_time: Optional[float] = None

    def mark_departed(self, current_time: float) -> float:
        """Records departure and computes total waiting time in seconds."""
        self.departure_time = current_time
        self.wait_time = max(0.0, current_time - self.arrival_time)
        return self.wait_time

    def current_waiting_time(self, current_time: float) -> float:
        """Calculates waiting duration up to the current simulated moment."""
        return max(0.0, current_time - self.arrival_time)


@dataclass
class PhaseRecord:
    """Historical record of an executed signal phase."""
    phase_number: int
    simulated_timestamp: float
    selected_direction: Direction
    green_duration: int
    vehicles_served: int
    queue_lengths_before: Dict[str, int]
    queue_lengths_after: Dict[str, int]
    priority_scores: Dict[str, float]
    avg_wait_times: Dict[str, float]
    max_wait_times: Dict[str, float]
    had_emergency: bool
    scheduler_type: str
    decision_reason: str = ""


@dataclass
class SimulationConfig:
    """Configuration parameters for traffic simulation and scheduling algorithms."""
    min_green_time: int = 5
    max_green_time: int = 35
    seconds_per_vehicle: float = 2.0  # 1 vehicle departs every 2.0s of green light
    yellow_light_duration: int = 3
    all_red_clearance: int = 1
    
    # Priority scoring weights
    queue_weight: float = 1.0
    waiting_time_weight: float = 0.5
    emergency_bonus: float = 100.0
    enable_emergency: bool = True
    
    # Starvation prevention
    starvation_threshold_seconds: float = 60.0
    starvation_bonus: float = 60.0
    
    # Fixed-time scheduling parameter
    fixed_green_duration: int = 20
    
    # Randomness
    random_seed: int = 42
