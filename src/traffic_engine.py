"""
Vehicle arrival generator and traffic pattern simulator.
"""
import random
from enum import Enum
from typing import Dict, List, Optional
from src.models import Direction, Vehicle, VehicleType


class TrafficIntensity(str, Enum):
    LOW = "Low Traffic"
    MODERATE = "Moderate Traffic"
    HEAVY = "Heavy Traffic"
    ASYMMETRIC = "Asymmetric Corridor (N-S Rush Hour)"
    CUSTOM = "Custom Demand"


class TrafficGenerator:
    """
    Simulates stochastic, pseudo-random vehicle arrivals across intersection approaches
    with reproducible seeds and configurable intensities.
    """

    INTENSITY_RANGES = {
        TrafficIntensity.LOW: (1, 3),
        TrafficIntensity.MODERATE: (3, 6),
        TrafficIntensity.HEAVY: (7, 12),
        TrafficIntensity.ASYMMETRIC: {
            Direction.NORTH: (8, 14),
            Direction.SOUTH: (8, 14),
            Direction.EAST: (1, 3),
            Direction.WEST: (1, 3),
        }
    }

    def __init__(self, seed: int = 42):
        self.seed: int = seed
        self.rng: random.Random = random.Random(seed)
        self.vehicle_counter: int = 0

    def set_seed(self, seed: int) -> None:
        """Resets generator with a specific seed for reproducible experiments."""
        self.seed = seed
        self.rng = random.Random(seed)
        self.vehicle_counter = 0

    def generate_vehicle(
        self,
        direction: Direction,
        arrival_time: float,
        force_emergency: bool = False,
        vehicle_type: Optional[VehicleType] = None
    ) -> Vehicle:
        """Creates a single vehicle with a unique ID."""
        self.vehicle_counter += 1
        veh_id = f"V-{direction.value[0]}-{self.vehicle_counter:04d}"

        if force_emergency:
            return Vehicle(
                id=veh_id,
                direction=direction,
                arrival_time=arrival_time,
                vehicle_type=VehicleType.EMERGENCY,
                is_emergency=True
            )

        if vehicle_type is None:
            # Deterministic pseudo-random vehicle category distribution
            roll = self.rng.random()
            if roll < 0.78:
                vtype = VehicleType.CAR
                is_emg = False
            elif roll < 0.88:
                vtype = VehicleType.BUS
                is_emg = False
            elif roll < 0.96:
                vtype = VehicleType.TRUCK
                is_emg = False
            else:
                vtype = VehicleType.EMERGENCY
                is_emg = True
        else:
            vtype = vehicle_type
            is_emg = (vtype == VehicleType.EMERGENCY)

        return Vehicle(
            id=veh_id,
            direction=direction,
            arrival_time=arrival_time,
            vehicle_type=vtype,
            is_emergency=is_emg
        )

    def generate_batch_arrivals(
        self,
        intensity: TrafficIntensity,
        current_time: float,
        custom_counts: Optional[Dict[Direction, int]] = None,
        allow_emergency: bool = True
    ) -> List[Vehicle]:
        """
        Generates arriving vehicles for all 4 approaches according to selected intensity.
        """
        arrivals: List[Vehicle] = []

        for d in Direction.all_directions():
            if intensity == TrafficIntensity.CUSTOM and custom_counts:
                count = max(0, custom_counts.get(d, 0))
            elif intensity == TrafficIntensity.ASYMMETRIC:
                min_c, max_c = self.INTENSITY_RANGES[TrafficIntensity.ASYMMETRIC][d]
                count = self.rng.randint(min_c, max_c)
            else:
                min_c, max_c = self.INTENSITY_RANGES[intensity]
                count = self.rng.randint(min_c, max_c)

            for _ in range(count):
                veh = self.generate_vehicle(d, current_time)
                if not allow_emergency and veh.is_emergency:
                    veh.is_emergency = False
                    veh.vehicle_type = VehicleType.CAR
                arrivals.append(veh)

        return arrivals
