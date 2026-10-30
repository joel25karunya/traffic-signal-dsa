# Test Plan & Verification Matrix

## 1. Scope and Strategy

The testing strategy validates the correctness, reliability, reproducibility, and safety of all core Data Structures and Algorithms, simulation routines, metric calculations, and data exports.

Testing is automated using `pytest` and covers:
- Unit tests for queue data structures (`collections.deque`).
- Algorithmic verification for priority scoring, tie-breaking, and heap selection (`heapq`).
- Fairness and starvation prevention override testing.
- Emergency vehicle preemption tests.
- Comparative benchmark fairness.
- Data export integrity (CSV and JSON).

---

## 2. Test Verification Matrix

| Test Identifier | File | Objective | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| `test_enqueue_and_fifo_order` | `test_queues.py` | Verify FIFO order | Earlier vehicles depart first; wait times reflect arrival vs departure. |
| `test_queue_length_nonnegative` | `test_queues.py` | Safety & bounds | Dequeuing from empty queue returns `None`; length stays $\ge 0$. |
| `test_batch_dequeue` | `test_queues.py` | Capacity enforcement | Safely dequeues up to capacity without errors if queue has fewer. |
| `test_emergency_flag_detection` | `test_queues.py` | Emergency state | Correctly detects presence and count of emergency vehicles in queue. |
| `test_intersection_queue_manager_dispatch` | `test_queues.py` | Routing | Vehicles route to correct approach queue based on `Direction`. |
| `test_priority_score_calculation` | `test_schedulers.py` | Mathematical accuracy | Matches hand-calculated score: $(Q \times W_q) + (T_w \times W_w)$. |
| `test_heap_selection_and_empty_handling` | `test_schedulers.py` | Heap selection | Highest priority approach is selected; empty junction returns `None`. |
| `test_deterministic_tie_breaking` | `test_schedulers.py` | Tie resolution | Identical scores resolve deterministically: North < East < South < West. |
| `test_adaptive_green_duration_clamping` | `test_schedulers.py` | Adaptive timing bounds | Green times are bounded within $[G_{min}, G_{max}]$. |
| `test_fixed_time_scheduler_cycle_order` | `test_schedulers.py` | Baseline consistency | Cycles North $\rightarrow$ East $\rightarrow$ South $\rightarrow$ West in order. |
| `test_starvation_prevention_override` | `test_fairness.py` | Anti-starvation | Waiting $\ge T_{starv}$ awards bonus $B_{starv}$, preempting heavy queues. |
| `test_emergency_vehicle_priority` | `test_fairness.py` | Emergency preemption | Ambulance approach wins green even against 20 queued regular cars. |
| `test_emergency_vehicle_disabled` | `test_fairness.py` | Config toggle | When disabled in settings, emergency vehicles receive no bonus. |
| `test_vehicle_waiting_time_and_metrics_averages` | `test_metrics.py` | Statistics | True average wait time computed across all departed vehicles. |
| `test_throughput_math_and_zero_duration_safety` | `test_metrics.py` | Throughput | Zero-duration simulations return $0.0$; throughput math is verified. |
| `test_simulation_step_and_queue_advancement` | `test_simulation.py` | Simulation lifecycle | Single step advances simulated time and changes signal states. |
| `test_seed_reproducibility` | `test_simulation.py` | Reproducibility | Identical seeds generate identical vehicle sequences and decisions. |
| `test_simulation_reset_clears_state` | `test_simulation.py` | Reset | Reset restores all queues to 0 and clears metrics and clock. |
| `test_comparative_benchmark_fairness` | `test_simulation.py` | Benchmark integrity | Both algorithms receive identical arrival sequences. |
| `test_csv_phases_export` | `test_exports.py` | Data export | CSV headers and records accurately reflect executed phases. |
| `test_json_summary_export` | `test_exports.py` | JSON serialization | Valid JSON structure contains summary aggregates and metadata. |

---

## 3. Running Automated Tests

Execute the full automated test suite using PowerShell:

```powershell
.\.venv\Scripts\pytest -v
```

All 21 test cases execute in less than 0.50 seconds.
