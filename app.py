"""
Intelligent Traffic Signal Management System Using Data Structures and Algorithms
Main Streamlit Application Entrypoint.
"""
import streamlit as st
from datetime import datetime
from src.models import SimulationConfig, Direction
from src.simulation import SimulationEngine, run_comparative_benchmark
from src.traffic_engine import TrafficIntensity
from src.data_export import SimulationDataExporter
from ui.styles import apply_custom_styles
from ui.dashboard import render_dashboard
from ui.analytics import render_traffic_analytics, render_algorithm_comparison_view
from ui.algorithm_visualizer import render_algorithm_visualizer

# Page configuration
st.set_page_config(
    page_title="Intelligent Traffic Signal Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Cyber Traffic Control Styling
st.markdown(apply_custom_styles(), unsafe_allow_html=True)

# Session State Initialization
if "config" not in st.session_state:
    st.session_state.config = SimulationConfig()

if "engine" not in st.session_state:
    st.session_state.engine = SimulationEngine(
        config=st.session_state.config,
        scheduler_type="dynamic",
        seed=st.session_state.config.random_seed
    )

if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None

engine: SimulationEngine = st.session_state.engine
config: SimulationConfig = st.session_state.config

# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #00F2FE; margin-bottom: 4px;">🚦 TRAFFIC CONTROL</h2>
    <span style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.1em;">DSA Simulation Engine</span>
</div>
""", unsafe_allow_html=True)

section = st.sidebar.radio(
    "Navigation Sections",
    options=[
        "1. Overview",
        "2. Live Intersection",
        "3. DSA Algorithm Visualization",
        "4. Traffic Analytics",
        "5. Algorithm Comparison",
        "6. Simulation Settings",
        "7. Simulation History & Exports",
        "8. About the Project"
    ],
    index=1
)

st.sidebar.markdown("---")

# Quick Controls in Sidebar
st.sidebar.markdown("### 🎛️ Controller Mode")
sched_mode = st.sidebar.selectbox(
    "Active Scheduling Strategy",
    options=["Dynamic-Priority (Greedy)", "Fixed-Time (Round-Robin)"],
    index=0 if engine.scheduler_type == "dynamic" else 1
)
new_sched = "dynamic" if "Dynamic" in sched_mode else "fixed"
if new_sched != engine.scheduler_type:
    engine.set_scheduler_type(new_sched)
    st.sidebar.success(f"Switched scheduler to: {new_sched.upper()}")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Status")
quick_summary = engine.get_summary_metrics()
st.sidebar.write(f"⏱️ **Clock:** `{quick_summary.total_simulated_time:.0f}s`")
st.sidebar.write(f"🚗 **Waiting:** `{quick_summary.total_vehicles_waiting} vehicles`")
st.sidebar.write(f"✅ **Served:** `{quick_summary.total_vehicles_served} vehicles`")
st.sidebar.write(f"⏳ **Avg Wait:** `{quick_summary.average_waiting_time_served:.1f}s`")

# Global Reset Action
with st.sidebar.expander("⚠️ Reset Simulation"):
    st.warning("This clears all active queues and simulation history.")
    if st.button("Confirm Reset", type="secondary", use_container_width=True):
        engine.reset()
        st.session_state.benchmark_results = None
        st.rerun()

# ----------------- SECTION ROUTING -----------------

if section == "1. Overview":
    st.markdown("""
    # 🚦 Intelligent Traffic Signal Management System
    ### Practical Demonstration of Data Structures & Algorithms (DSA) in Urban Mobility

    Welcome to the **Intelligent Traffic Signal Management System**, a modular simulation platform engineered 
    to resolve urban intersection congestion using classic and greedy algorithms, FIFO queues, 
    and binary heap priority queues.
    """)

    st.markdown("""
    <div class="glass-panel">
        <h3 style="color:#00F2FE;">🎯 Project Objectives</h3>
        <ol style="line-height: 1.8; color:#D1D5DB;">
            <li><b>Dynamic Signal Allocation:</b> Dynamically allocate green-light durations based on real-time vehicle demand instead of rigid pre-timed cycles.</li>
            <li><b>Congestion Mitigation:</b> Reduce average vehicle waiting times, eliminate runaway queues, and increase junction throughput.</li>
            <li><b>Starvation Prevention:</b> Guarantee fairness so low-density side streets are never blocked indefinitely by high-density corridors.</li>
            <li><b>Emergency Preemption:</b> Provide priority preemption for emergency vehicles (ambulances, fire engines).</li>
            <li><b>DSA Rigor:</b> Demonstrate practical implementations of <code>collections.deque</code> (FIFO Queues) and <code>heapq</code> (Priority Queues).</li>
            <li><b>Empirical Benchmarking:</b> Fairly evaluate Dynamic Priority against standard Fixed-Time Round-Robin scheduling using identical vehicle arrival seeds.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🧩 Data Structures Employed
        - **FIFO Queues (`collections.deque`):**
          - Maintains vehicles for each approach (North, East, South, West).
          - $\\mathcal{O}(1)$ amortized insertion and extraction, strictly preserving arrival sequence.
        - **Priority Queue (`heapq`):**
          - Evaluates approach scores and selects the highest priority direction in $\\mathcal{O}(\\log M)$ time.
          - Deterministic tie-breaking ensures identical runs produce identical decisions.
        """)
    with col2:
        st.markdown("""
        ### ⚙️ Core Algorithms
        - **Greedy Priority Scoring:**
          Calculates priority score as a weighted sum of queue length and accumulated vehicle wait times.
        - **Adaptive Green Time Formula:**
          Estimates optimal green duration from queue depth and vehicle service rates.
        - **Starvation Override Policy:**
          Boosts direction priority when maximum waiting time crosses a configured safety threshold.
        """)

    st.info("👉 Navigate to **2. Live Intersection** on the sidebar to interact with the real-time simulation!")

elif section == "2. Live Intersection":
    render_dashboard(engine, config)

elif section == "3. DSA Algorithm Visualization":
    render_algorithm_visualizer(
        breakdowns=engine.state.last_priority_breakdowns,
        last_phase_record=engine.state.last_phase_record,
        config=config
    )

elif section == "4. Traffic Analytics":
    render_traffic_analytics(
        timeline_points=engine.metrics_tracker.timeline_points,
        summary=engine.get_summary_metrics()
    )

elif section == "5. Algorithm Comparison":
    st.markdown("### 🔬 Run Comparative Benchmark")
    st.markdown(
        "Generate a mathematically rigorous, side-by-side comparison between **Fixed-Time Round-Robin** "
        "and **Dynamic Priority** scheduling. Both algorithms are tested on the exact same pseudo-random vehicle arrivals."
    )

    col_cp1, col_cp2, col_cp3 = st.columns(3)
    with col_cp1:
        bench_rounds = st.slider("Simulation Phases (Rounds)", min_value=5, max_value=30, value=12)
    with col_cp2:
        bench_intensity = st.selectbox(
            "Traffic Demand Pattern",
            options=[
                TrafficIntensity.ASYMMETRIC,
                TrafficIntensity.MODERATE,
                TrafficIntensity.HEAVY,
                TrafficIntensity.LOW
            ]
        )
    with col_cp3:
        bench_seed = st.number_input("Benchmark Seed", min_value=1, max_value=9999, value=42)

    if st.button("🚀 Run Head-to-Head Benchmark", type="primary", use_container_width=True):
        with st.spinner("Simulating both algorithms on identical traffic streams..."):
            st.session_state.benchmark_results = run_comparative_benchmark(
                rounds=bench_rounds,
                intensity=bench_intensity,
                config=config,
                seed=bench_seed
            )
            st.success("Benchmark completed successfully!")

    if st.session_state.benchmark_results:
        render_algorithm_comparison_view(st.session_state.benchmark_results)
    else:
        st.info("Click 'Run Head-to-Head Benchmark' above to generate empirical comparison metrics.")

elif section == "6. Simulation Settings":
    st.markdown("## ⚙️ Simulation & Algorithm Parameters")
    st.markdown("Fine-tune priority scoring weights, green duration limits, and starvation thresholds:")

    with st.form("settings_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 🚥 Signal Timing Limits")
            new_min_green = st.slider("Minimum Green Time (s)", 3, 15, config.min_green_time)
            new_max_green = st.slider("Maximum Green Time (s)", 15, 60, config.max_green_time)
            new_service_rate = st.slider("Service Rate (Seconds per Vehicle)", 0.5, 4.0, config.seconds_per_vehicle, step=0.1)
            new_fixed_green = st.slider("Fixed-Time Green Duration (s)", 10, 45, config.fixed_green_duration)

        with col_c2:
            st.markdown("#### ⚖️ Priority Scoring & Starvation")
            new_q_weight = st.slider("Queue Length Weight (Wq)", 0.1, 5.0, config.queue_weight, step=0.1)
            new_w_weight = st.slider("Waiting Time Weight (Ww)", 0.1, 3.0, config.waiting_time_weight, step=0.1)
            new_emg_bonus = st.slider("Emergency Priority Bonus", 10.0, 200.0, config.emergency_bonus, step=10.0)
            new_starv_thresh = st.slider("Starvation Threshold (s)", 20.0, 120.0, config.starvation_threshold_seconds, step=5.0)
            new_starv_bonus = st.slider("Starvation Override Bonus", 10.0, 150.0, config.starvation_bonus, step=10.0)
            enable_emg = st.checkbox("Enable Emergency Vehicle Preemption", value=config.enable_emergency)

        saved = st.form_submit_button("💾 Save & Apply Parameters", type="primary", use_container_width=True)
        if saved:
            config.min_green_time = new_min_green
            config.max_green_time = new_max_green
            config.seconds_per_vehicle = new_service_rate
            config.fixed_green_duration = new_fixed_green
            config.queue_weight = new_q_weight
            config.waiting_time_weight = new_w_weight
            config.emergency_bonus = new_emg_bonus
            config.starvation_threshold_seconds = new_starv_thresh
            config.starvation_bonus = new_starv_bonus
            config.enable_emergency = enable_emg
            engine.update_config(config)
            st.success("Simulation configuration updated successfully!")

elif section == "7. Simulation History & Exports":
    st.markdown("## 📜 Simulation History & Data Export")
    st.markdown("Review phase-by-phase execution logs and download data in standard CSV and JSON formats:")

    phases = engine.metrics_tracker.phase_history
    if not phases:
        st.info("No phases recorded yet. Advance the simulation from Live Intersection to generate history.")
    else:
        st.markdown(f"**Total Phases Recorded:** `{len(phases)}`")

        # Export Buttons
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            csv_phases = SimulationDataExporter.export_phases_to_csv(phases)
            st.download_button(
                label="📥 Download Phases CSV",
                data=csv_phases,
                file_name=f"traffic_phases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_e2:
            csv_vehicles = SimulationDataExporter.export_departed_vehicles_to_csv(engine.metrics_tracker.departed_vehicles)
            st.download_button(
                label="📥 Download Departed Vehicles CSV",
                data=csv_vehicles,
                file_name=f"departed_vehicles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_e3:
            json_summary = SimulationDataExporter.export_summary_to_json(
                summary=engine.get_summary_metrics(),
                phases=phases,
                metadata={"exported_at": str(datetime.now()), "scheduler": engine.scheduler_type}
            )
            st.download_button(
                label="📥 Download Summary JSON",
                data=json_summary,
                file_name=f"simulation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        st.markdown("### Completed Signal Phases")
        history_rows = []
        for p in reversed(phases):  # Most recent first
            history_rows.append({
                "Phase #": p.phase_number,
                "Sim Time": f"{p.simulated_timestamp:.1f}s",
                "Direction": p.selected_direction.value,
                "Green (s)": p.green_duration,
                "Vehicles Served": p.vehicles_served,
                "North Queue (Before/After)": f"{p.queue_lengths_before.get('North',0)} ➔ {p.queue_lengths_after.get('North',0)}",
                "East Queue (Before/After)": f"{p.queue_lengths_before.get('East',0)} ➔ {p.queue_lengths_after.get('East',0)}",
                "South Queue (Before/After)": f"{p.queue_lengths_before.get('South',0)} ➔ {p.queue_lengths_after.get('South',0)}",
                "West Queue (Before/After)": f"{p.queue_lengths_before.get('West',0)} ➔ {p.queue_lengths_after.get('West',0)}",
                "Emergency?": "🚨 Yes" if p.had_emergency else "No",
                "Scheduler": p.scheduler_type
            })
        st.dataframe(history_rows, use_container_width=True)

elif section == "8. About the Project":
    st.markdown("""
    # 📚 About the Project: Academic & DSA Documentation

    ### College Software Project: Intelligent Traffic Signal Management System
    **Course:** Data Structures and Algorithms (DSA) / Software Engineering  
    **Architecture:** Clean Modular Architecture (Domain Engine, Priority Schedulers, Metric Tracking, UI)

    ---

    ### 1. Data Structures and Algorithmic Analysis

    | Component | Data Structure | Python Module | Operation | Time Complexity | Space Complexity |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Approach Queues** | FIFO Queue | `collections.deque` | `append()` (Arrival) | $\\mathcal{O}(1)$ amortized | $\\mathcal{O}(N)$ |
    | | | | `popleft()` (Departure) | $\\mathcal{O}(1)$ | |
    | | | | `len()` (Queue Size) | $\\mathcal{O}(1)$ | |
    | **Signal Selection** | Priority Queue | `heapq` | `heapify()` | $\\mathcal{O}(M)$ | $\\mathcal{O}(M)$ |
    | | | | `heappop()` | $\\mathcal{O}(\\log M)$ | |
    | **Scheduler Strategy** | Greedy Policy | Python Math | Priority & Green Calc | $\\mathcal{O}(M \\log M)$ | $\\mathcal{O}(M)$ |

    *$N$ = number of vehicles in queue; $M$ = number of intersection approaches ($M=4$).*

    ---

    ### 2. Algorithmic Formulations

    #### Priority Scoring Formula:
    $$\\text{Score}_d = (Q_d \\cdot W_q) + (T_{w,d} \\cdot W_w) + B_{emg} + B_{starv}$$
    Where:
    - $Q_d$: Queue length on direction $d$.
    - $W_q$: Queue weight (default $1.0$).
    - $T_{w,d}$: Maximum waiting time among vehicles on approach $d$.
    - $W_w$: Waiting time weight (default $0.5$).
    - $B_{emg}$: Emergency preemption bonus ($100.0$ if emergency vehicle waiting).
    - $B_{starv}$: Starvation override bonus ($60.0$ if $T_{w,d} \\ge \\text{Threshold}$).

    #### Adaptive Green Light Formula:
    $$G_d = \\text{clamp}\\left(\\text{Round}\\left(G_{min} + \\frac{Q_d}{R_{service}}\\right), G_{min}, G_{max}\\right)$$

    ---

    ### 3. Starvation Prevention Guarantee
    In standard greedy scheduling, a high-density primary boulevard could starve a low-density cross street indefinitely. 
    Our system introduces a configurable **Starvation Threshold ($T_{starv}$)**:
    - If a non-empty queue waits longer than $T_{starv}$ seconds, its priority is boosted with $B_{starv}$, 
      ensuring bounded maximum waiting time and guaranteeing fair service.

    ---

    ### 4. Assumptions and Real-World Limitations
    - **Simulation Model:** This application is designed for educational and algorithmic demonstration. 
    - **Simplification:** Yellow clearance intervals and single-movement safety phases are modeled in discrete simulated seconds.
    - **Disclaimer:** This software is an educational simulation and is **not certified** for controlling real physical traffic infrastructure. Real traffic systems require hardware fail-safes, conflict monitors (green-conflict monitoring), and compliance with NEMA TS2 or 2070 standards.
    """)
