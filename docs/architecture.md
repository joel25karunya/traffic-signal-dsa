# System Architecture: Intelligent Traffic Signal Management System

## 1. Architectural Overview

The system adheres to a **Clean Modular Layered Architecture**, strictly separating mathematical domain logic, data structures, and state management from the user interface and presentation layer.

```
+-------------------------------------------------------------+
|                      Streamlit Frontend                     |
|  (app.py, dashboard.py, intersection.py, analytics.py)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      Simulation Engine                      |
|                      (simulation.py)                        |
+-------------------------------------------------------------+
        |                     |                     |
        v                     v                     v
+---------------+     +---------------+     +---------------+
| Queue Manager |     | Priority/     |     | Metrics &     |
| (deque FIFO)  |     | Schedulers    |     | Data Export   |
|               |     | (heapq Greedy)|     |               |
+---------------+     +---------------+     +---------------+
        |                     |                     |
        +---------------------+---------------------+
                              v
+-------------------------------------------------------------+
|                      Core Data Models                       |
|         (Direction, Vehicle, PhaseRecord, Config)           |
+-------------------------------------------------------------+
```

---

## 2. Component Breakdown

### A. Domain Models (`src/models.py`)
- `Direction`: Enum for `North`, `East`, `South`, `West` with spatial properties.
- `SignalState`: Enum for `RED`, `YELLOW`, `GREEN`.
- `Vehicle`: Encapsulates vehicle identity, timestamp of arrival, vehicle type, emergency flag, departure timestamp, and wait duration.
- `PhaseRecord`: Immutable snapshot of a completed signal phase.
- `SimulationConfig`: Parameter object controlling algorithm weights, bounds, and thresholds.

### B. Queue Management (`src/queue_manager.py`)
- `DirectionQueue`: Wraps `collections.deque[Vehicle]` with O(1) operations, tracking maximum recorded queue depths, batch service, and emergency flags.
- `IntersectionQueueManager`: Aggregates the 4 directional approaches into a unified intersection manager.

### C. Scheduling & Algorithmic Engines
- `src/priority_scheduler.py`: Calculates priority scores and evaluates approach candidates using `heapq`. Generates transparent scoring breakdowns for educational inspection.
- `src/dynamic_scheduler.py`: Orchestrates the greedy dynamic signal allocation, adaptive green time calculations, and starvation safeguards.
- `src/fixed_time_scheduler.py`: Implements traditional pre-timed cyclic signal control as an empirical baseline.

### D. Traffic Generation & Simulation (`src/traffic_engine.py`, `src/simulation.py`)
- `TrafficGenerator`: Pseudo-random vehicle arrival generator with reproducible seeds and intensity distributions (Low, Moderate, Heavy, Asymmetric).
- `SimulationEngine`: Manages the simulation lifecycle (stepping, pausing, resetting, manual injection).
- `run_comparative_benchmark()`: Executes a controlled head-to-head experiment between Fixed-Time and Dynamic Priority on the identical vehicle arrival stream.

### E. Metrics & Data Export (`src/metrics.py`, `src/data_export.py`)
- `SimulationMetricsTracker`: Tracks departed vehicle wait times, peak queues, and throughput time series.
- `SimulationDataExporter`: Exports phase history and vehicle transit logs to standard CSV and JSON.

### F. User Interface (`ui/`)
- `ui/styles.py`: Cyber traffic management dark mode styling with Google Fonts and CSS custom properties.
- `ui/intersection.py`: Dynamic SVG 4-way crossroad visualization with signal lamps, queued vehicles, and departure flow indicator.
- `ui/dashboard.py`: HUD metrics cards, phase stepping controls, and vehicle injection forms.
- `ui/analytics.py`: Plotly charts for time series and comparative bar charts.
- `ui/algorithm_visualizer.py`: Step-by-step priority calculation matrix and worked scenario simulator.

---

## 3. Design Decisions & Trade-Offs

1. **Simulated Clock vs Wall Clock:**
   - *Decision:* All calculations operate on simulated discrete time rather than Python `time.sleep()`.
   - *Rationale:* Eliminates UI freezing, provides instant batch simulations, and ensures exact reproducibility regardless of computer hardware speed.

2. **Decoupled Schedulers:**
   - Schedulers receive pure domain objects (`IntersectionQueueManager`, `sim_time`) and return pure `PhaseRecord` instances without importing any UI components or frameworks.

3. **Pure Python Standard Library for Data Exports:**
   - Exports utilize Python's built-in `csv` and `json` modules to ensure exports are lightning fast, have zero external dependencies, and match the internal state exactly.
