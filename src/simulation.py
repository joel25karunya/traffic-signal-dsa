"""
Simulation engine orchestrating queue operations, signal controllers, and timing.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from src.models import Direction, PhaseRecord, SignalState, SimulationConfig, Vehicle
from src.queue_manager import IntersectionQueueManager
from src.dynamic_scheduler import DynamicScheduler
from src.fixed_time_scheduler import FixedTimeScheduler
from src.traffic_engine import TrafficGenerator, TrafficIntensity
from src.metrics import SimulationMetricsTracker, IntersectionSummaryMetrics
from src.priority_scheduler import PriorityBreakdown


@dataclass
class SimulationState:
    """Current live state of the intersection simulation."""
    simulated_time: float = 0.0
    active_green_direction: Optional[Direction] = None
    signal_states: Dict[str, SignalState] = None
    current_phase_number: int = 0
    current_green_remaining: int = 0
    last_phase_record: Optional[PhaseRecord] = None
    last_priority_breakdowns: List[PriorityBreakdown] = None
    last_departed_vehicles: List[Vehicle] = None
    is_paused: bool = True

    def __post_init__(self):
        if self.signal_states is None:
            self.signal_states = {d.value: SignalState.RED for d in Direction.all_directions()}
        if self.last_priority_breakdowns is None:
            self.last_priority_breakdowns = []
        if self.last_departed_vehicles is None:
            self.last_departed_vehicles = []


class SimulationEngine:
    """
    Core simulation controller decoupling domain logic from the Streamlit UI.
    Supports single-step stepping, automated batch runs, manual vehicle injection,
    and fair head-to-head algorithm benchmarking.
    """

    def __init__(
        self,
        config: Optional[SimulationConfig] = None,
        scheduler_type: str = "dynamic",
        seed: int = 42
    ):
        self.config: SimulationConfig = config or SimulationConfig()
        self.scheduler_type: str = scheduler_type.lower()
        self.seed: int = seed

        self.queue_mgr: IntersectionQueueManager = IntersectionQueueManager()
        self.generator: TrafficGenerator = TrafficGenerator(seed=self.seed)
        self.metrics_tracker: SimulationMetricsTracker = SimulationMetricsTracker()

        # Schedulers
        self.dynamic_scheduler: DynamicScheduler = DynamicScheduler(self.config)
        self.fixed_scheduler: FixedTimeScheduler = FixedTimeScheduler(self.config)

        self.state: SimulationState = SimulationState()
        self.update_signal_states(None)

    def update_config(self, config: SimulationConfig) -> None:
        """Applies updated config to schedulers."""
        self.config = config
        self.dynamic_scheduler.update_config(config)
        self.fixed_scheduler.config = config

    def set_scheduler_type(self, scheduler_type: str) -> None:
        """Switches between 'dynamic' and 'fixed'."""
        self.scheduler_type = scheduler_type.lower()

    def update_signal_states(self, green_dir: Optional[Direction]) -> None:
        """Sets active green direction and turns all others to red."""
        self.state.active_green_direction = green_dir
        for d in Direction.all_directions():
            if d == green_dir:
                self.state.signal_states[d.value] = SignalState.GREEN
            else:
                self.state.signal_states[d.value] = SignalState.RED

    def inject_vehicle(
        self,
        direction: Direction,
        is_emergency: bool = False,
        vehicle_type: Optional[Any] = None
    ) -> Vehicle:
        """Manually adds a vehicle to a specific approach."""
        vehicle = self.generator.generate_vehicle(
            direction=direction,
            arrival_time=self.state.simulated_time,
            force_emergency=is_emergency,
            vehicle_type=vehicle_type
        )
        self.queue_mgr.enqueue_vehicle(vehicle)
        self.metrics_tracker.record_arrival(vehicle)
        return vehicle

    def inject_batch(self, counts: Dict[Direction, int], allow_emergency: bool = True) -> List[Vehicle]:
        """Manually injects specific counts of vehicles into directions."""
        arrived = []
        for d, count in counts.items():
            for _ in range(max(0, count)):
                veh = self.inject_vehicle(d, is_emergency=False)
                arrived.append(veh)
        return arrived

    def generate_traffic(
        self,
        intensity: TrafficIntensity = TrafficIntensity.MODERATE,
        custom_counts: Optional[Dict[Direction, int]] = None
    ) -> List[Vehicle]:
        """Generates random vehicle arrivals and enqueues them."""
        arrivals = self.generator.generate_batch_arrivals(
            intensity=intensity,
            current_time=self.state.simulated_time,
            custom_counts=custom_counts,
            allow_emergency=self.config.enable_emergency
        )
        for veh in arrivals:
            self.queue_mgr.enqueue_vehicle(veh)
            self.metrics_tracker.record_arrival(veh)
        return arrivals

    def step_phase(
        self,
        auto_generate_traffic: bool = False,
        traffic_intensity: TrafficIntensity = TrafficIntensity.MODERATE
    ) -> Tuple[PhaseRecord, List[Vehicle], List[PriorityBreakdown]]:
        """
        Advances the simulation by exactly one traffic signal phase.
        """
        # Step A: Optional incoming vehicle arrivals
        if auto_generate_traffic:
            self.generate_traffic(intensity=traffic_intensity)

        # Step B: Select and execute phase via active scheduler
        breakdowns: List[PriorityBreakdown] = []
        if self.scheduler_type == "fixed":
            phase_record, departed = self.fixed_scheduler.step_phase(
                self.queue_mgr, self.state.simulated_time
            )
            # Evaluate priority breakdowns for informational display
            breakdown_dict = self.dynamic_scheduler.pq_scheduler.evaluate_all_directions(
                self.queue_mgr, self.state.simulated_time
            )
            breakdowns = list(breakdown_dict.values())
        else:
            phase_record, departed, breakdowns = self.dynamic_scheduler.step_phase(
                self.queue_mgr, self.state.simulated_time
            )

        # Step C: Update intersection signal light states
        self.update_signal_states(phase_record.selected_direction)

        # Step D: Advance simulated clock
        total_phase_seconds = phase_record.green_duration + self.config.yellow_light_duration + self.config.all_red_clearance
        self.state.simulated_time += total_phase_seconds
        self.state.current_phase_number = phase_record.phase_number
        self.state.last_phase_record = phase_record
        self.state.last_priority_breakdowns = breakdowns
        self.state.last_departed_vehicles = departed

        # Step E: Record metrics
        waiting_count = self.queue_mgr.total_waiting_vehicles()
        curr_max_wait = max((q.max_waiting_time(self.state.simulated_time) for q in self.queue_mgr.queues.values()), default=0.0)
        self.metrics_tracker.record_phase(phase_record, departed, waiting_count, curr_max_wait)

        return phase_record, departed, breakdowns

    def get_summary_metrics(self) -> IntersectionSummaryMetrics:
        """Returns consolidated metrics up to current simulated moment."""
        waiting_count = self.queue_mgr.total_waiting_vehicles()
        curr_avg_wait = 0.0
        if waiting_count > 0:
            total_w = sum(sum(q.get_waiting_times(self.state.simulated_time)) for q in self.queue_mgr.queues.values())
            curr_avg_wait = total_w / waiting_count

        curr_max_wait = max((q.max_waiting_time(self.state.simulated_time) for q in self.queue_mgr.queues.values()), default=0.0)

        return self.metrics_tracker.get_summary(
            current_sim_time=self.state.simulated_time,
            current_waiting_count=waiting_count,
            current_avg_wait=curr_avg_wait,
            current_max_wait=curr_max_wait
        )

    def reset(self, new_seed: Optional[int] = None) -> None:
        """Completely resets simulation state and metrics."""
        if new_seed is not None:
            self.seed = new_seed
        self.generator.set_seed(self.seed)
        self.queue_mgr.reset()
        self.metrics_tracker.reset()
        self.dynamic_scheduler.reset()
        self.fixed_scheduler.reset()
        self.state = SimulationState(simulated_time=0.0)
        self.update_signal_states(None)


def run_comparative_benchmark(
    rounds: int = 15,
    intensity: TrafficIntensity = TrafficIntensity.MODERATE,
    config: Optional[SimulationConfig] = None,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Executes a side-by-side benchmark comparing Fixed-Time vs Dynamic-Priority
    under the EXACT SAME vehicle arrival sequences and initial parameters.
    """
    cfg = config or SimulationConfig(random_seed=seed)

    # 1. Pre-generate identical batches of vehicle arrival counts for each round
    rng = TrafficGenerator(seed=seed)
    arrival_batches: List[List[Tuple[Direction, bool]]] = []
    
    sim_dummy = TrafficGenerator(seed=seed)
    for r in range(rounds):
        batch = sim_dummy.generate_batch_arrivals(intensity, current_time=r * 25.0, allow_emergency=cfg.enable_emergency)
        arrival_batches.append([(v.direction, v.is_emergency) for v in batch])

    # 2. Run Fixed-Time Engine
    fixed_engine = SimulationEngine(config=cfg, scheduler_type="fixed", seed=seed)
    for r in range(rounds):
        # Inject identical vehicles
        for direction, is_emg in arrival_batches[r]:
            fixed_engine.inject_vehicle(direction, is_emergency=is_emg)
        fixed_engine.step_phase(auto_generate_traffic=False)

    fixed_metrics = fixed_engine.get_summary_metrics()

    # 3. Run Dynamic-Priority Engine
    dynamic_engine = SimulationEngine(config=cfg, scheduler_type="dynamic", seed=seed)
    for r in range(rounds):
        # Inject identical vehicles
        for direction, is_emg in arrival_batches[r]:
            dynamic_engine.inject_vehicle(direction, is_emergency=is_emg)
        dynamic_engine.step_phase(auto_generate_traffic=False)

    dynamic_metrics = dynamic_engine.get_summary_metrics()

    # 4. Compute differences and percentage improvements
    # For waiting times and queue lengths, lower is better: improvement = (fixed - dynamic) / fixed * 100
    # For served vehicles and throughput, higher is better: improvement = (dynamic - fixed) / fixed * 100
    def pct_reduction(fixed_val: float, dyn_val: float) -> Optional[float]:
        if fixed_val == 0:
            return 0.0 if dyn_val == 0 else -100.0
        return ((fixed_val - dyn_val) / fixed_val) * 100.0

    def pct_increase(fixed_val: float, dyn_val: float) -> Optional[float]:
        if fixed_val == 0:
            return 0.0 if dyn_val == 0 else 100.0
        return ((dyn_val - fixed_val) / fixed_val) * 100.0

    return {
        "fixed": fixed_metrics,
        "dynamic": dynamic_metrics,
        "fixed_engine": fixed_engine,
        "dynamic_engine": dynamic_engine,
        "comparisons": {
            "avg_wait_improvement_pct": pct_reduction(
                fixed_metrics.average_waiting_time_served,
                dynamic_metrics.average_waiting_time_served
            ),
            "max_wait_improvement_pct": pct_reduction(
                fixed_metrics.max_waiting_time_served,
                dynamic_metrics.max_waiting_time_served
            ),
            "max_queue_reduction_pct": pct_reduction(
                float(fixed_metrics.max_queue_recorded),
                float(dynamic_metrics.max_queue_recorded)
            ),
            "served_increase_pct": pct_increase(
                float(fixed_metrics.total_vehicles_served),
                float(dynamic_metrics.total_vehicles_served)
            ),
            "throughput_increase_pct": pct_increase(
                fixed_metrics.throughput_per_minute,
                dynamic_metrics.throughput_per_minute
            )
        }
    }
