"""
Educational DSA Algorithm Visualizer explaining priority calculations, heap operations, and scheduling decisions.
"""
import streamlit as st
import pandas as pd
from typing import List, Optional
from src.models import Direction, SimulationConfig
from src.priority_scheduler import PriorityBreakdown, PriorityQueueScheduler
from src.queue_manager import IntersectionQueueManager
from src.traffic_engine import TrafficGenerator


def render_algorithm_visualizer(
    breakdowns: Optional[List[PriorityBreakdown]],
    last_phase_record,
    config: SimulationConfig
):
    """
    Renders educational breakdown of the greedy scheduling algorithm and priority queue.
    """
    st.markdown("## 🧠 DSA Algorithm Visualization & Decision Engine")
    st.markdown(
        "Explore how the **Greedy Dynamic Scheduler** and **Priority Queue (Min/Max Heap)** "
        "evaluate road priorities, apply starvation safeguards, and compute optimal green time durations."
    )

    tab1, tab2, tab3 = st.tabs([
        "🔬 Live Decision Inspection",
        "🧮 Interactive Worked Example",
        "📚 DSA Complexity & Heap Analysis"
    ])

    with tab1:
        st.subheader("Last Executed Phase Decision Walkthrough")
        if not last_phase_record:
            st.info("No phase has been executed yet. Run a step from the Live Intersection tab to inspect real decisions.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Phase #", last_phase_record.phase_number)
            with col2:
                st.metric("Selected Direction", last_phase_record.selected_direction.value)
            with col3:
                st.metric("Allocated Green", f"{last_phase_record.green_duration}s")
            with col4:
                st.metric("Vehicles Served", last_phase_record.vehicles_served)

            st.markdown(f"**Algorithmic Decision Log:** `{last_phase_record.decision_reason}`")

            st.markdown("### Step-by-Step Priority Evaluation Matrix")
            if breakdowns:
                data = []
                for b in breakdowns:
                    data.append({
                        "Approach": b.direction.value,
                        "Queue Len (N)": b.queue_length,
                        "Queue Term (N × Wq)": f"{b.queue_contribution:.1f}",
                        "Max Wait (Tw)": f"{b.max_wait_time:.1f}s",
                        "Wait Term (Tw × Ww)": f"{b.wait_contribution:.1f}",
                        "Emergency Bonus": f"+{b.emergency_bonus:.1f}" if b.is_emergency else "0.0",
                        "Starvation Bonus": f"+{b.starvation_bonus:.1f}" if b.is_starving else "0.0",
                        "Tie Order": b.tie_breaker_order,
                        "Final Priority Score": round(b.total_score, 2),
                        "Eligible?": "✅ Yes" if b.queue_length > 0 else "❌ Empty"
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

            st.markdown("### 🚦 Adaptive Green Duration Formula Calculation")
            st.markdown("""
            Once the direction with maximum priority score is popped from the **Priority Queue**, 
            the duration is dynamically computed using the following formula:
            """)
            
            chosen_dir = last_phase_record.selected_direction.value
            initial_q = last_phase_record.queue_lengths_before.get(chosen_dir, 0)
            sec_per_veh = config.seconds_per_vehicle
            min_g = config.min_green_time
            max_g = config.max_green_time

            st.code(
                f"# Configured Parameters:\n"
                f"min_green_time = {min_g}s, max_green_time = {max_g}s, seconds_per_vehicle = {sec_per_veh}s\n\n"
                f"# Selected Approach: {chosen_dir} (Initial Queue = {initial_q} vehicles)\n"
                f"estimated_time = {min_g} + round({initial_q} * {sec_per_veh}) = {min_g + round(initial_q * sec_per_veh)}s\n"
                f"allocated_green_duration = clamp({min_g + round(initial_q * sec_per_veh)}, {min_g}, {max_g}) = {last_phase_record.green_duration}s\n"
                f"service_capacity = int({last_phase_record.green_duration} / {sec_per_veh}) = {int(last_phase_record.green_duration / sec_per_veh)} vehicles\n"
                f"actual_vehicles_served = min(queue_length, capacity) = {last_phase_record.vehicles_served}",
                language="python"
            )

    with tab2:
        st.subheader("Interactive Custom Scenario Simulator")
        st.markdown("Adjust queue lengths and waiting times to test how the priority algorithm behaves:")

        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            q_north = st.number_input("North Queue", min_value=0, max_value=50, value=12)
            w_north = st.number_input("North Max Wait (s)", min_value=0.0, max_value=120.0, value=15.0)
            emg_north = st.checkbox("North Emergency?", value=False)
        with col_w2:
            q_east = st.number_input("East Queue", min_value=0, max_value=50, value=5)
            w_east = st.number_input("East Max Wait (s)", min_value=0.0, max_value=120.0, value=25.0)
            emg_east = st.checkbox("East Emergency?", value=False)
        with col_w3:
            q_south = st.number_input("South Queue", min_value=0, max_value=50, value=18)
            w_south = st.number_input("South Max Wait (s)", min_value=0.0, max_value=120.0, value=40.0)
            emg_south = st.checkbox("South Emergency?", value=False)
        with col_w4:
            q_west = st.number_input("West Queue", min_value=0, max_value=50, value=3)
            w_west = st.number_input("West Max Wait (s)", min_value=0.0, max_value=120.0, value=65.0)  # over starvation threshold!
            emg_west = st.checkbox("West Emergency?", value=False)

        # Run test calculation
        dummy_mgr = IntersectionQueueManager()
        gen = TrafficGenerator(seed=101)

        for d, q_len, w_time, is_emg in [
            (Direction.NORTH, q_north, w_north, emg_north),
            (Direction.EAST, q_east, w_east, emg_east),
            (Direction.SOUTH, q_south, w_south, emg_south),
            (Direction.WEST, q_west, w_west, emg_west)
        ]:
            if q_len > 0:
                # Add vehicles with appropriate arrival times
                v_first = gen.generate_vehicle(d, arrival_time=0.0, force_emergency=is_emg)
                dummy_mgr.enqueue_vehicle(v_first)
                for _ in range(q_len - 1):
                    dummy_mgr.enqueue_vehicle(gen.generate_vehicle(d, arrival_time=max(0.0, w_time - 5.0)))

        pq = PriorityQueueScheduler(config)
        selected, test_breakdowns, reason = pq.select_next_direction_heap(
            dummy_mgr, current_time=max(w_north, w_east, w_south, w_west)
        )

        st.markdown(f"#### 🏆 Selected Direction: **{selected.value if selected else 'None'}**")
        st.info(f"**Decision Reasoning:** {reason}")

        # Show Table
        calc_rows = []
        for b in test_breakdowns:
            calc_rows.append({
                "Direction": b.direction.value,
                "Queue": b.queue_length,
                "Wait Time": f"{b.max_wait_time:.1f}s",
                "Queue Score": f"{b.queue_contribution:.1f}",
                "Wait Score": f"{b.wait_contribution:.1f}",
                "Emergency": f"+{b.emergency_bonus:.1f}" if b.is_emergency else "0.0",
                "Starvation Bonus": f"+{b.starvation_bonus:.1f}" if b.is_starving else "0.0",
                "Total Priority": round(b.total_score, 2),
                "Winner?": "🥇 WINNER" if b.direction == selected else ""
            })
        st.dataframe(pd.DataFrame(calc_rows), use_container_width=True)

    with tab3:
        st.subheader("Data Structures & Complexity Analysis")
        st.markdown("""
        ### 1. FIFO Queue (`collections.deque`)
        - **Enqueue Arrival:** Vehicle enters the tail of the approach queue $\\mathcal{O}(1)$ amortized.
        - **Dequeue Service:** Vehicles depart from the front of the queue $\\mathcal{O}(1)$ during green signal.
        - **Queue Length:** $\\mathcal{O}(1)$ size tracking.
        - **Fairness Guarantee:** Guarantees First-In, First-Out order so earlier arriving vehicles are served first within a lane.

        ### 2. Priority Queue (`heapq`)
        - **Heap Structure:** Python's `heapq` module implements a binary min-heap. To achieve a max-priority queue, we invert the total priority score:
        ```python
        heap_entry = (-priority_score, tie_breaker_index, direction)
        ```
        - **Heap Build:** Transforming the candidate list of eligible approaches into a heap: $\\mathcal{O}(M)$ where $M=4$.
        - **Heap Extraction:** `heapq.heappop()` extracts the maximum priority approach in $\\mathcal{O}(\\log M)$ time.
        
        ### 3. Comparison: Heap vs Linear Scan ($M=4$)
        - With 4 fixed approaches, a linear search requires $M=4$ comparisons.
        - Binary heap requires $\\approx \\lceil \\log_2 4 \\rceil = 2$ comparisons.
        - While both run in $\\mathcal{O}(1)$ for constant $M$, a Priority Queue architecture scales seamlessly to complex smart-city intersections with dozens of approach lanes, turning bays, emergency sensor events, and scheduled transit buses.
        """)
