"""
Interactive Plotly analytics dashboard for traffic metrics, time series, and algorithm comparisons.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from src.metrics import IntersectionSummaryMetrics


def render_traffic_analytics(timeline_points: List[Dict], summary: IntersectionSummaryMetrics):
    """
    Renders charts for queue dynamics, waiting times, and throughput.
    """
    st.markdown("## 📊 Traffic Analytics & System Performance")

    if not timeline_points:
        st.info("No simulation history available yet. Run a few phases to populate analytics charts.")
        return

    df_timeline = pd.DataFrame(timeline_points)

    # 1. Summary Metrics Tiles
    st.subheader("System Aggregates")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Arrived", summary.total_vehicles_arrived)
        st.metric("Total Served", summary.total_vehicles_served)
    with col2:
        st.metric("Currently Waiting", summary.total_vehicles_waiting)
        st.metric("Max Recorded Queue", summary.max_queue_recorded)
    with col3:
        st.metric("Avg Wait Time (Served)", f"{summary.average_waiting_time_served:.1f} s")
        st.metric("Max Wait Time (Served)", f"{summary.max_waiting_time_served:.1f} s")
    with col4:
        st.metric("Throughput (Veh/min)", f"{summary.throughput_per_minute:.1f}")
        st.metric("Simulated Time", f"{summary.total_simulated_time:.0f} s")

    st.markdown("---")

    # 2. Queue Lengths Over Time Chart
    st.subheader("📈 Queue Length Evolution by Approach")
    fig_queues = go.Figure()
    fig_queues.add_trace(go.Scatter(x=df_timeline["sim_time"], y=df_timeline["North_queue"], name="North", line=dict(color="#38BDF8", width=2)))
    fig_queues.add_trace(go.Scatter(x=df_timeline["sim_time"], y=df_timeline["East_queue"], name="East", line=dict(color="#F59E0B", width=2)))
    fig_queues.add_trace(go.Scatter(x=df_timeline["sim_time"], y=df_timeline["South_queue"], name="South", line=dict(color="#10B981", width=2)))
    fig_queues.add_trace(go.Scatter(x=df_timeline["sim_time"], y=df_timeline["West_queue"], name="West", line=dict(color="#EC4899", width=2)))
    fig_queues.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        xaxis_title="Simulated Time (Seconds)",
        yaxis_title="Queued Vehicles",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=30, b=40)
    )
    st.plotly_chart(fig_queues, use_container_width=True)

    # 3. Two columns: Waiting Time Trend & Green Allocation Share
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("⏳ Waiting Time Progression")
        fig_wait = go.Figure()
        fig_wait.add_trace(go.Scatter(
            x=df_timeline["sim_time"],
            y=df_timeline["avg_wait_time"],
            name="Cumulative Avg Wait (Served)",
            line=dict(color="#6366F1", width=2)
        ))
        fig_wait.add_trace(go.Scatter(
            x=df_timeline["sim_time"],
            y=df_timeline["current_max_wait"],
            name="Current Max Wait in Queue",
            line=dict(color="#EF4444", width=2, dash="dash")
        ))
        fig_wait.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            xaxis_title="Simulated Time (s)",
            yaxis_title="Seconds",
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_wait, use_container_width=True)

    with col_c2:
        st.subheader("🟢 Green Signal Allocation by Direction")
        green_data = summary.green_time_per_direction
        fig_pie = px.pie(
            names=list(green_data.keys()),
            values=list(green_data.values()),
            hole=0.45,
            color_discrete_sequence=["#38BDF8", "#F59E0B", "#10B981", "#EC4899"]
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 4. Arrived vs Served by Approach
    st.subheader("🚗 Vehicle Inflow vs Outflow by Approach")
    approaches = list(summary.arrived_per_direction.keys())
    arrived_vals = [summary.arrived_per_direction[a] for a in approaches]
    served_vals = [summary.served_per_direction[a] for a in approaches]

    fig_bar = go.Figure(data=[
        go.Bar(name='Arrived', x=approaches, y=arrived_vals, marker_color='#60A5FA'),
        go.Bar(name='Served', x=approaches, y=served_vals, marker_color='#34D399')
    ])
    fig_bar.update_layout(
        barmode='group',
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        yaxis_title="Vehicle Count",
        margin=dict(l=40, r=40, t=30, b=40)
    )
    st.plotly_chart(fig_bar, use_container_width=True)


def render_algorithm_comparison_view(benchmark_results: Dict[str, Any]):
    """
    Renders side-by-side comparison between Fixed-Time and Dynamic Priority scheduling.
    """
    st.markdown("## ⚖️ Algorithm Comparison: Fixed-Time vs Dynamic Priority")
    st.markdown(
        "Both algorithms were executed against the **EXACT SAME pseudo-random vehicle arrival sequence** "
        "and initial queue states to ensure an honest, mathematically fair comparison."
    )

    fixed = benchmark_results["fixed"]
    dyn = benchmark_results["dynamic"]
    comp = benchmark_results["comparisons"]

    # Comparative Key Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Avg Waiting Time",
            f"{dyn.average_waiting_time_served:.1f} s",
            delta=f"{comp['avg_wait_improvement_pct']:+.1f}% vs Fixed ({fixed.average_waiting_time_served:.1f}s)",
            delta_color="normal" if comp['avg_wait_improvement_pct'] >= 0 else "inverse"
        )
    with c2:
        st.metric(
            "Max Waiting Time",
            f"{dyn.max_waiting_time_served:.1f} s",
            delta=f"{comp['max_wait_improvement_pct']:+.1f}% vs Fixed ({fixed.max_waiting_time_served:.1f}s)",
            delta_color="normal" if comp['max_wait_improvement_pct'] >= 0 else "inverse"
        )
    with c3:
        st.metric(
            "Total Vehicles Served",
            dyn.total_vehicles_served,
            delta=f"{comp['served_increase_pct']:+.1f}% vs Fixed ({fixed.total_vehicles_served})",
            delta_color="normal" if comp['served_increase_pct'] >= 0 else "inverse"
        )
    with c4:
        st.metric(
            "Peak Queue Length",
            dyn.max_queue_recorded,
            delta=f"{comp['max_queue_reduction_pct']:+.1f}% vs Fixed ({fixed.max_queue_recorded})",
            delta_color="normal" if comp['max_queue_reduction_pct'] >= 0 else "inverse"
        )

    st.markdown("---")

    # Detailed Table
    st.subheader("📋 Head-to-Head Benchmark Results Table")
    comp_df = pd.DataFrame([
        {
            "Metric": "Total Vehicles Arrived",
            "Fixed-Time": fixed.total_vehicles_arrived,
            "Dynamic Priority": dyn.total_vehicles_arrived,
            "Difference": f"{dyn.total_vehicles_arrived - fixed.total_vehicles_arrived:+d}",
            "Status": "Identical Input ✅"
        },
        {
            "Metric": "Total Vehicles Served",
            "Fixed-Time": fixed.total_vehicles_served,
            "Dynamic Priority": dyn.total_vehicles_served,
            "Difference": f"{dyn.total_vehicles_served - fixed.total_vehicles_served:+d}",
            "Status": f"{comp['served_increase_pct']:+.1f}% Change"
        },
        {
            "Metric": "Average Waiting Time (s)",
            "Fixed-Time": f"{fixed.average_waiting_time_served:.2f}",
            "Dynamic Priority": f"{dyn.average_waiting_time_served:.2f}",
            "Difference": f"{dyn.average_waiting_time_served - fixed.average_waiting_time_served:+.2f} s",
            "Status": f"{comp['avg_wait_improvement_pct']:+.1f}% Improvement"
        },
        {
            "Metric": "Maximum Waiting Time (s)",
            "Fixed-Time": f"{fixed.max_waiting_time_served:.2f}",
            "Dynamic Priority": f"{dyn.max_waiting_time_served:.2f}",
            "Difference": f"{dyn.max_waiting_time_served - fixed.max_waiting_time_served:+.2f} s",
            "Status": f"{comp['max_wait_improvement_pct']:+.1f}% Improvement"
        },
        {
            "Metric": "Max Queue Length (Vehicles)",
            "Fixed-Time": fixed.max_queue_recorded,
            "Dynamic Priority": dyn.max_queue_recorded,
            "Difference": f"{dyn.max_queue_recorded - fixed.max_queue_recorded:+d}",
            "Status": f"{comp['max_queue_reduction_pct']:+.1f}% Reduction"
        },
        {
            "Metric": "Throughput (Vehicles/min)",
            "Fixed-Time": f"{fixed.throughput_per_minute:.2f}",
            "Dynamic Priority": f"{dyn.throughput_per_minute:.2f}",
            "Difference": f"{dyn.throughput_per_minute - fixed.throughput_per_minute:+.2f}",
            "Status": f"{comp['throughput_increase_pct']:+.1f}% Improvement"
        },
        {
            "Metric": "Total Simulated Duration (s)",
            "Fixed-Time": f"{fixed.total_simulated_time:.1f}",
            "Dynamic Priority": f"{dyn.total_simulated_time:.1f}",
            "Difference": f"{dyn.total_simulated_time - fixed.total_simulated_time:+.1f} s",
            "Status": "Simulated Duration"
        }
    ])
    st.dataframe(comp_df, use_container_width=True)

    # Comparative Bar Charts
    st.subheader("📊 Comparative Performance Visualizations")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        fig_wait_comp = go.Figure(data=[
            go.Bar(name='Fixed-Time', x=['Avg Wait Time', 'Max Wait Time'], y=[fixed.average_waiting_time_served, fixed.max_waiting_time_served], marker_color='#94A3B8'),
            go.Bar(name='Dynamic Priority', x=['Avg Wait Time', 'Max Wait Time'], y=[dyn.average_waiting_time_served, dyn.max_waiting_time_served], marker_color='#00E676')
        ])
        fig_wait_comp.update_layout(
            title="Waiting Times Comparison (Lower is Better)",
            barmode='group',
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            yaxis_title="Seconds",
            margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_wait_comp, use_container_width=True)

    with col_b2:
        fig_srv_comp = go.Figure(data=[
            go.Bar(name='Fixed-Time', x=['Vehicles Served', 'Throughput (veh/min)'], y=[fixed.total_vehicles_served, fixed.throughput_per_minute], marker_color='#94A3B8'),
            go.Bar(name='Dynamic Priority', x=['Vehicles Served', 'Throughput (veh/min)'], y=[dyn.total_vehicles_served, dyn.throughput_per_minute], marker_color='#38BDF8')
        ])
        fig_srv_comp.update_layout(
            title="Throughput & Service Comparison (Higher is Better)",
            barmode='group',
            template="plotly_dark",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            yaxis_title="Value",
            margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_srv_comp, use_container_width=True)
