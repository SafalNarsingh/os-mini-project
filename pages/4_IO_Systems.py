import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="I/O Systems - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --text-primary: #1e293b;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #374151;
    }
    .metric-value { font-size: 2rem; font-weight: 800; color: #3b82f6; }
    .metric-label { font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ============== DISK SCHEDULING ALGORITHMS ==============

def run_disk_scheduling(requests, head, algorithm, disk_size=200):
    sequence = [head]
    log = []
    total_seek = 0
    
    if algorithm == "FCFS":
        sequence += requests
    elif algorithm == "SSTF":
        temp_req = requests.copy()
        current = head
        while temp_req:
            closest = min(temp_req, key=lambda x: abs(x - current))
            sequence.append(closest)
            temp_req.remove(closest)
            current = closest
    elif algorithm == "SCAN":
        # Simplified SCAN (moving right then left)
        right = sorted([r for r in requests if r >= head])
        left = sorted([r for r in requests if r < head], reverse=True)
        sequence += right + ([disk_size - 1] if right else []) + left
    elif algorithm == "LOOK":
        right = sorted([r for r in requests if r >= head])
        left = sorted([r for r in requests if r < head], reverse=True)
        sequence += right + left

    # Calculate Total Seek
    for i in range(len(sequence) - 1):
        total_seek += abs(sequence[i+1] - sequence[i])
        
    return sequence, total_seek

# ============== SESSION STATE ==============
if 'requests' not in st.session_state:
    st.session_state.requests = [98, 183, 37, 122, 14, 124, 65, 67]
if 'io_results' not in st.session_state:
    st.session_state.io_results = None

# ============== SIDEBAR (Navigation Only) ==============
with st.sidebar:
    st.title("OS Simulator")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("main.py")
    st.divider()
    st.caption("Module: I/O Systems")

# ============== MAIN UI ==============
st.title("💿 I/O Systems & Disk Scheduling")

# I/O CONTROLLER DASHBOARD
with st.container(border=True):
    st.subheader("🎮 I/O Controller Interface")
    c1, c2, c3 = st.columns([1.5, 2, 1], gap="large")
    
    with c1:
        algo = st.selectbox("Scheduling Algorithm", ["FCFS", "SSTF", "SCAN", "LOOK"])
        head_start = st.number_input("Initial Head Position", value=53, min_value=0, max_value=199)
        if st.button("▶ Start Simulation", type="primary", use_container_width=True):
            seq, seek = run_disk_scheduling(st.session_state.requests, head_start, algo)
            st.session_state.io_results = {'seq': seq, 'seek': seek, 'algo': algo}

    with c2:
        st.markdown("**Request Queue Management**")
        with st.form("add_req", clear_on_submit=True):
            f1, f2 = st.columns([2, 1])
            new_t = f1.number_input("Track Number", min_value=0, max_value=199, step=1)
            if f2.form_submit_button("Add"):
                st.session_state.requests.append(new_t)
                st.rerun()
        st.info(f"Queue: {', '.join(map(str, st.session_state.requests))}")

    with c3:
        st.markdown("**System Actions**")
        if st.button("🗑️ Clear Queue", use_container_width=True):
            st.session_state.requests = []
            st.rerun()
        if st.button("🔄 Reset Simulator", type="primary", use_container_width=True):
            st.session_state.requests = [98, 183, 37, 122, 14, 124, 65, 67]
            st.session_state.io_results = None
            st.rerun()

st.divider()

# VISUALIZATION
if st.session_state.io_results:
    res = st.session_state.io_results
    col_graph, col_stats = st.columns([2, 1], gap="large")
    
    with col_graph:
        st.subheader(f"Head Movement Graph ({res['algo']})")
        
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(res['seq']))),
            y=res['seq'],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10, color='#1e3a8a', symbol='circle'),
            hovertemplate='Step %{x}<br>Track: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            xaxis_title="Step Number",
            yaxis_title="Track Position (0-199)",
            yaxis=dict(range=[0, 200], autorange=False),
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_stats:
        st.subheader("Performance Metrics")
        
        m1, m2 = st.columns(2)
        m1.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{res['seek']}</div>
                <div class="metric-label">Total Seek Distance</div>
            </div>
        """, unsafe_allow_html=True)
        
        avg_seek = res['seek'] / (len(res['seq']) - 1) if len(res['seq']) > 1 else 0
        m2.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_seek:.1f}</div>
                <div class="metric-label">Avg Seek/Req</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("**Full Seek Sequence:**")
        st.code(" → ".join(map(str, res['seq'])))
else:
    st.info("Adjust the initial head position and queue, then click 'Start Simulation' to see results.")

st.divider()
st.caption("OS Simulator v2.0 | I/O Systems Module")