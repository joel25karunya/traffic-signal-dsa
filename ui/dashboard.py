"""
Main control dashboard and live intersection interface.
"""
import streamlit as st
from typing import Optional
from src.models import Direction, SimulationConfig, VehicleType
from src.simulation import SimulationEngine
from src.traffic_engine import TrafficIntensity
from ui.intersection import render_intersection_svg


def render_dashboard(engine: SimulationEngine, config: SimulationConfig):
    """
    Renders the live intersection, HUD metric cards, and manual/automated control center.
    """
    summary = engine.get_summary_metrics()
    state = engine.state

    # 1. Top HUD Control Banner
    active_dir_name = state.active_green_direction.value if state.active_green_direction else "All Red (Clearance)"
    st.markdown(f"""
    <div class="control-banner">
        <div>
            <h1 class="banner-title">🚦 Smart City Traffic Controller</h1>
            <p style="color:#9CA3AF; margin:4px 0 0 0; font-size:13px;">
                Mode: <b style="color:#00F2FE;">{engine.scheduler_type.upper()} PRIORITY</b> | 
                Simulated Clock: <b style="color:#FFFFFF;">{summary.total_simulated_time:.0f}s</b> | 
                Completed Phases: <b style="color:#FFFFFF;">{summary.total_phases_completed}</b>
            </p>
        </div>
        <div>
            <span class="banner-badge">Active Signal: {active_dir_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Key Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vehicles Waiting</div>
            <div class="metric-value" style="color:#00F2FE;">{summary.total_vehicles_waiting}</div>
            <div class="metric-sub">Across 4 approaches</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vehicles Served</div>
            <div class="metric-value" style="color:#00E676;">{summary.total_vehicles_served}</div>
            <div class="metric-sub">Out of {summary.total_vehicles_arrived} arrivals</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Wait Time</div>
            <div class="metric-value">{summary.average_waiting_time_served:.1f}s</div>
            <div class="metric-sub">Completed departures</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Max Queue Peak</div>
            <div class="metric-value">{summary.max_queue_recorded}</div>
            <div class="metric-sub">Highest approach queue</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        last_dur = state.last_phase_record.green_duration if state.last_phase_record else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Green Duration</div>
            <div class="metric-value" style="color:#FFC400;">{last_dur}s</div>
            <div class="metric-sub">Phase #{state.current_phase_number}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 3. Intersection Visualizer & Controls Columns
    col_vis, col_ctrl = st.columns([1.5, 1])

    with col_vis:
        st.subheader("Live 4-Way Road Intersection")
        svg_code = render_intersection_svg(
            queue_mgr=engine.queue_mgr,
            signal_states=state.signal_states,
            active_green_direction=state.active_green_direction,
            green_duration=last_dur,
            departed_vehicles=state.last_departed_vehicles,
            sim_time=state.simulated_time
        )
        st.markdown(svg_code, unsafe_allow_html=True)

        if state.last_phase_record:
            st.caption(f"💡 **Last Algorithmic Phase Reason:** {state.last_phase_record.decision_reason}")

    with col_ctrl:
        st.subheader("Intersection Controller")

        # Step Phase Controls
        st.markdown("##### ⏱️ Phase Stepper")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            auto_gen = st.checkbox("Auto-Generate Traffic", value=True, help="Automatically spawns incoming vehicles before each phase.")
        with col_s2:
            intensity = st.selectbox(
                "Traffic Pattern",
                options=[
                    TrafficIntensity.MODERATE,
                    TrafficIntensity.LOW,
                    TrafficIntensity.HEAVY,
                    TrafficIntensity.ASYMMETRIC
                ]
            )

        step_btn = st.button("🟢 Advance Next Phase (Step)", type="primary", use_container_width=True)
        if step_btn:
            engine.step_phase(auto_generate_traffic=auto_gen, traffic_intensity=intensity)
            st.rerun()

        # Batch Run Button
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            run_5_btn = st.button("⏩ Run 5 Phases", use_container_width=True)
            if run_5_btn:
                for _ in range(5):
                    engine.step_phase(auto_generate_traffic=auto_gen, traffic_intensity=intensity)
                st.rerun()
        with col_b2:
            run_10_btn = st.button("⏭️ Run 10 Phases", use_container_width=True)
            if run_10_btn:
                for _ in range(10):
                    engine.step_phase(auto_generate_traffic=auto_gen, traffic_intensity=intensity)
                st.rerun()

        st.markdown("---")

        # Manual Injection
        st.markdown("##### 🚗 Manual Vehicle Injection")
        with st.form("manual_inject_form"):
            inject_dir = st.selectbox("Approach Direction", options=Direction.all_directions(), format_func=lambda d: d.value)
            veh_type = st.selectbox("Vehicle Type", options=[VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK, VehicleType.EMERGENCY])
            is_emergency = (veh_type == VehicleType.EMERGENCY)
            inject_count = st.number_input("Count to Enqueue", min_value=1, max_value=20, value=1)
            
            submitted = st.form_submit_button("➕ Enqueue Vehicles", use_container_width=True)
            if submitted:
                for _ in range(inject_count):
                    engine.inject_vehicle(inject_dir, is_emergency=is_emergency, vehicle_type=veh_type)
                st.success(f"Enqueued {inject_count} {veh_type.value}(s) into {inject_dir.value} approach queue.")
                st.rerun()

        # Emergency Trigger
        st.markdown("##### 🚨 Emergency Vehicle Quick Override")
        emg_dir = st.selectbox("Dispatch Emergency Vehicle To:", options=Direction.all_directions(), format_func=lambda d: d.value, key="emg_quick_sel")
        if st.button("🚨 Dispatch Ambulance / Fire Engine", use_container_width=True):
            engine.inject_vehicle(emg_dir, is_emergency=True, vehicle_type=VehicleType.EMERGENCY)
            st.warning(f"Emergency vehicle dispatched to {emg_dir.value} approach! Priority will be preempted next phase.")
            st.rerun()
