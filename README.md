# 🚦 Intelligent Traffic Signal Management System Using Data Structures and Algorithms

A college-level software engineering and Data Structures & Algorithms (DSA) project demonstrating dynamic, demand-responsive traffic signal scheduling at a four-way urban intersection.

---

## 📌 1. Problem Statement

Conventional urban traffic intersections predominantly operate using **fixed-time (pre-timed) controllers**. In a fixed-time system, each approach receives a static green light duration according to a rigid cyclical sequence regardless of actual queue lengths. 

This causes two severe real-world problems:
1. **Wasted Green Time:** Vehicles on empty approaches receive green lights while no cars are waiting.
2. **Runaway Congestion:** Busy approaches during rush hours develop lengthy queues, causing excessive vehicular delays, increased idling emissions, and transit unpredictability.

This project implements an **Intelligent Traffic Signal Management System** that continuously monitors vehicle queues, computes road priorities dynamically using greedy heuristic formulas, uses a **Binary Heap Priority Queue (`heapq`)** for signal selection, dynamically allocates green times, safeguards against starvation, and preempts signals for emergency vehicles.

---

## 🎯 2. Project Objectives

1. **Dynamic Green Time Allocation:** Calculate green duration adaptively based on real-time vehicle demand.
2. **Delay & Congestion Reduction:** Lower average vehicle waiting times and peak queue lengths.
3. **Starvation Prevention:** Guarantee that low-volume side streets are never starved indefinitely by high-volume corridors.
4. **Emergency Vehicle Preemption:** Immediately prioritize ambulances and fire engines.
5. **Practical DSA Demonstration:** Showcase direct applications of **FIFO Queues (`collections.deque`)** and **Priority Queues (`heapq`)**.
6. **Empirical Benchmarking:** Fairly compare Dynamic Priority against Fixed-Time Round-Robin scheduling using identical pseudo-random arrival seeds.

---

## 💻 3. Technology Stack

- **Language:** Python 3.11+ (Tested on Python 3.13)
- **Data Structures:** `collections.deque` (FIFO queues), `heapq` (Min/Max Binary Heaps)
- **Frontend / UI:** Streamlit (v1.35+)
- **Visualization:** Scalable Vector Graphics (SVG) with CSS3 Animations
- **Analytics & Plotting:** Plotly Express & Plotly Graph Objects
- **Data Management:** Pandas, standard library `csv`, and `json`
- **Testing:** Pytest (v8.0+)
- **Environment:** Windows PowerShell, VS Code compatible

---

## 🧠 4. Data Structures & Algorithms Used

| Component | DSA Concept | Python Implementation | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Approach Queues** | FIFO Queue | `collections.deque` | $\mathcal{O}(1)$ amortized append/popleft | $\mathcal{O}(N)$ |
| **Approach Prioritization** | Priority Queue | `heapq` (binary heap) | $\mathcal{O}(M \log M)$ selection | $\mathcal{O}(M)$ |
| **Greedy Scheduling** | Greedy Choice | Priority Score Model | $\mathcal{O}(M)$ evaluation | $\mathcal{O}(M)$ |
| **Starvation Guard** | Threshold-based override | Wait time tracker | $\mathcal{O}(1)$ per approach | $\mathcal{O}(1)$ |

*$N$ = number of queued vehicles; $M$ = number of intersection approaches ($M=4$).*

### Priority Formula:
$$\text{Score}_d = (Q_d \times W_q) + (T_{w,d} \times W_w) + B_{emg} + B_{starv}$$
Where:
- $Q_d$: Queue length on approach $d$.
- $W_q$: Configurable weight for queue size (default: $1.0$).
- $T_{w,d}$: Maximum waiting duration among currently queued vehicles.
- $W_w$: Configurable weight for waiting time (default: $0.5$).
- $B_{emg}$: Emergency vehicle preemption bonus (default: $100.0$).
- $B_{starv}$: Starvation override bonus (default: $60.0$, triggered when $T_{w,d} \ge 60$s).

### Adaptive Green Light Duration Formula:
$$G_d = \text{clamp}\left(G_{min} + \text{Round}\left(Q_d \times S_{rate}\right), G_{min}, G_{max}\right)$$
- $G_{min} = 5$s, $G_{max} = 35$s, $S_{rate} = 2.0$ seconds per vehicle.

---

## 📁 5. Folder Structure

```
Microproject/
├── app.py                      # Main Streamlit web application entrypoint
├── requirements.txt            # Project dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Complete project documentation
├── .gitignore                  # Git ignore rules
│
├── src/                        # Core algorithmic and simulation domain logic
│   ├── __init__.py
│   ├── models.py               # Data models (Vehicle, Direction, SignalState, Config)
│   ├── queue_manager.py        # DirectionQueue and IntersectionQueueManager (collections.deque)
│   ├── priority_scheduler.py   # Priority scoring and heapq Priority Queue implementation
│   ├── dynamic_scheduler.py    # Adaptive greedy scheduler with starvation prevention
│   ├── fixed_time_scheduler.py # Traditional pre-timed round-robin controller baseline
│   ├── traffic_engine.py       # Pseudo-random reproducible vehicle arrival generator
│   ├── simulation.py           # Simulation engine and comparative benchmarking
│   ├── metrics.py              # Performance metric tracking and time-series aggregation
│   └── data_export.py          # CSV and JSON report exporters
│
├── ui/                         # Presentation and visualization layer
│   ├── __init__.py
│   ├── styles.py               # Dark mode cyber traffic control center CSS
│   ├── intersection.py         # SVG 4-way intersection renderer with signal heads
│   ├── dashboard.py            # HUD metrics cards, phase stepper, manual injection form
│   ├── analytics.py            # Plotly time-series and comparative charts
│   └── algorithm_visualizer.py # Interactive worked example and formula inspection
│
├── tests/                      # Automated test suite (21 test cases)
│   ├── test_queues.py          # FIFO order, queue lengths, emergency detection
│   ├── test_schedulers.py      # Priority calculations, heap selection, tie-breaking
│   ├── test_fairness.py        # Starvation override and emergency vehicle preemption
│   ├── test_metrics.py         # Average/max wait times, throughput calculations
│   ├── test_simulation.py      # Simulation stepping, seed reproducibility, reset
│   └── test_exports.py         # CSV and JSON export validation
│
├── docs/                       # Detailed academic documentation
│   ├── algorithm_design.md     # Mathematical formulations and complexity analysis
│   ├── architecture.md         # System architecture and layer separation
│   └── test_plan.md            # Comprehensive test plan and verification matrix
│
└── assets/
    └── README.md
```

---

## 🚀 6. Installation & Execution (Windows PowerShell)

### Step 1: Open PowerShell in Project Directory
```powershell
cd path\to\Microproject
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(If script execution is restricted on your system, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
.\.venv\Scripts\streamlit run app.py
```
The browser will automatically open at `http://localhost:8501`.

---

## 🧪 7. Running Automated Tests

To execute the complete 21-test test suite:
```powershell
.\.venv\Scripts\pytest -v
```

All tests execute in under 0.50 seconds:
```
tests/test_exports.py::test_csv_phases_export PASSED                     [  4%]
tests/test_exports.py::test_json_summary_export PASSED                   [  9%]
tests/test_fairness.py::test_starvation_prevention_override PASSED       [ 14%]
tests/test_fairness.py::test_emergency_vehicle_priority PASSED           [ 19%]
tests/test_fairness.py::test_emergency_vehicle_disabled PASSED           [ 23%]
tests/test_metrics.py::test_vehicle_waiting_time_and_metrics_averages PASSED [ 28%]
tests/test_metrics.py::test_throughput_math_and_zero_duration_safety PASSED [ 33%]
tests/test_queues.py::test_enqueue_and_fifo_order PASSED                 [ 38%]
tests/test_queues.py::test_queue_length_nonnegative PASSED               [ 42%]
tests/test_queues.py::test_batch_dequeue PASSED                          [ 47%]
tests/test_queues.py::test_emergency_flag_detection PASSED               [ 52%]
tests/test_queues.py::test_intersection_queue_manager_dispatch PASSED    [ 57%]
tests/test_schedulers.py::test_priority_score_calculation PASSED         [ 61%]
tests/test_schedulers.py::test_heap_selection_and_empty_handling PASSED  [ 66%]
tests/test_schedulers.py::test_deterministic_tie_breaking PASSED         [ 71%]
tests/test_schedulers.py::test_adaptive_green_duration_clamping PASSED   [ 76%]
tests/test_schedulers.py::test_fixed_time_scheduler_cycle_order PASSED   [ 80%]
tests/test_simulation.py::test_simulation_step_and_queue_advancement PASSED [ 85%]
tests/test_simulation.py::test_seed_reproducibility PASSED               [ 90%]
tests/test_simulation.py::test_simulation_reset_clears_state PASSED      [ 95%]
tests/test_simulation.py::test_comparative_benchmark_fairness PASSED     [100%]
```

---

## 🧭 8. Dashboard Navigation Guide

1. **Overview:** Project summary, goals, and architectural breakdown.
2. **Live Intersection:** Real-time visual 4-way intersection SVG, active glowing signals, queued cars, live HUD metrics, manual phase stepper, batch runners, and vehicle injection form.
3. **DSA Algorithm Visualization:** Step-by-step scoring matrix, heap breakdown, adaptive timing math, and interactive scenario simulator.
4. **Traffic Analytics:** Plotly charts showing queue length evolution, waiting time trends, green light allocation pie chart, and inflow vs outflow bar charts.
5. **Algorithm Comparison:** Side-by-side empirical benchmark testing Fixed-Time vs Dynamic Priority against identical traffic seeds with percentage improvements.
6. **Simulation Settings:** Interactive sliders to adjust weights, service rates, signal timing limits, and starvation thresholds.
7. **Simulation History & Exports:** History table of all completed phases, with one-click download buttons for **Phases CSV**, **Departed Vehicles CSV**, and **Summary JSON**.
8. **About the Project:** Academic documentation, mathematical formulas, and presentation notes.

---

## ☁️ 9. Deployment (Render or Streamlit Community Cloud)

Streamlit needs a long-running server, so it cannot run on Vercel's serverless platform.

### Option A: Render (uses the included `render.yaml`)
1. Push this project to a GitHub repository (`.venv` and caches are excluded by `.gitignore`).
2. On render.com choose **New → Blueprint**, connect the repo, and apply. Render reads `render.yaml`.
   Or create a **Web Service** manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
3. The Python version is set by `.python-version` (3.13).
4. Note: free Render services sleep when idle, so the first request after a pause can take about a minute.

### Option B: Streamlit Community Cloud
Go to share.streamlit.io, sign in with GitHub, pick the repo, and set the main file to `app.py`.

---

## ⚠️ 10. Assumptions and Limitations

1. **Educational Simulation:** This software is designed for university-level demonstration of Data Structures & Algorithms. It is **not** certified for controlling actual physical road infrastructure.
2. **Simplified Single-Phase Controller:** For educational clarity, the intersection activates one approach at a time (opposing pairs or turn arrow movements are abstracted into single approach movements).
3. **Deterministic Departures:** Vehicle service rate is modeled as a configurable average parameter ($S_{rate} = 2.0$ seconds/vehicle).
4. **Real-World Safety Disclaimer:** Real-world traffic signal controllers require specialized hardware conflict monitors (NEMA TS2 / ATC), redundant physical relays, pedestrian call buttons, and loop-detector inductive sensors.
