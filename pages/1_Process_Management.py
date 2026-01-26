import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import copy

# Page configuration
st.set_page_config(
    page_title="Process Management - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --text-primary: #1e293b;
        --border: #e2e8f0;
    }
    .metric-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #334155;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #3b82f6; }
    .metric-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ============== CPU SCHEDULING ALGORITHMS ==============

def fcfs_scheduling(processes):
    processes_sorted = sorted(processes, key=lambda x: x['arrival'])
    gantt, results, log = [], [], []
    current_time = 0
    for p in processes_sorted:
        if current_time < p['arrival']:
            gantt.append({'process': 'IDLE', 'start': current_time, 'end': p['arrival']})
            current_time = p['arrival']
        start_time = current_time
        end_time = current_time + p['burst']
        results.append({
            'Process': p['name'], 'Arrival': p['arrival'], 'Burst': p['burst'],
            'Waiting': start_time - p['arrival'], 'Turnaround': end_time - p['arrival'], 'Finish': end_time
        })
        gantt.append({'process': p['name'], 'start': start_time, 'end': end_time})
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCH: {p['name']} (t={start_time} to t={end_time})")
        current_time = end_time
    return results, gantt, log

def sjf_scheduling(processes):
    remaining = copy.deepcopy(processes)
    gantt, results, log = [], [], []
    current_time = 0
    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        if not available:
            next_arr = min(p['arrival'] for p in remaining)
            gantt.append({'process': 'IDLE', 'start': current_time, 'end': next_arr})
            current_time = next_arr
            continue
        shortest = min(available, key=lambda x: x['burst'])
        remaining.remove(shortest)
        start_time = current_time
        end_time = current_time + shortest['burst']
        results.append({
            'Process': shortest['name'], 'Arrival': shortest['arrival'], 'Burst': shortest['burst'],
            'Waiting': start_time - shortest['arrival'], 'Turnaround': end_time - shortest['arrival'], 'Finish': end_time
        })
        gantt.append({'process': shortest['name'], 'start': start_time, 'end': end_time})
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SJF SELECT: {shortest['name']} (Burst: {shortest['burst']})")
        current_time = end_time
    return results, gantt, log

def round_robin_scheduling(processes, quantum):
    remaining = copy.deepcopy(processes)
    for p in remaining: p['rem'] = p['burst']
    gantt, log = [], []
    results_map = {p['name']: {'arr': p['arrival'], 'burst': p['burst'], 'fin': 0} for p in processes}
    current_time = 0
    ready_queue = []
    
    remaining.sort(key=lambda x: x['arrival'])
    while remaining or ready_queue:
        while remaining and remaining[0]['arrival'] <= current_time:
            ready_queue.append(remaining.pop(0))
        
        if not ready_queue:
            if remaining:
                gantt.append({'process': 'IDLE', 'start': current_time, 'end': remaining[0]['arrival']})
                current_time = remaining[0]['arrival']
            continue
            
        cp = ready_queue.pop(0)
        exec_t = min(quantum, cp['rem'])
        gantt.append({'process': cp['name'], 'start': current_time, 'end': current_time + exec_t})
        cp['rem'] -= exec_t
        current_time += exec_t
        
        while remaining and remaining[0]['arrival'] <= current_time:
            ready_queue.append(remaining.pop(0))
            
        if cp['rem'] > 0: ready_queue.append(cp)
        else: results_map[cp['name']]['fin'] = current_time
            
    res = []
    for name, d in results_map.items():
        tr = d['fin'] - d['arr']
        res.append({'Process': name, 'Arrival': d['arr'], 'Burst': d['burst'], 'Waiting': tr - d['burst'], 'Turnaround': tr, 'Finish': d['fin']})
    return res, gantt, log

# ============== SESSION STATE ==============
if 'processes' not in st.session_state:
    st.session_state.processes = [
        {'name': 'P1', 'arrival': 0, 'burst': 5, 'priority': 1},
        {'name': 'P2', 'arrival': 2, 'burst': 3, 'priority': 2}
    ]
if 'results' not in st.session_state: st.session_state.results = None
if 'gantt' not in st.session_state: st.session_state.gantt = None

# ============== SIDEBAR (Navigation Only) ==============
with st.sidebar:
    st.title("OS Simulator")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("main.py")
    st.divider()
    st.caption("Module: Process Management")

# ============== MAIN UI ==============
st.title("⚡ CPU Scheduling Visualization")

# TOP CONTROLS
col_config, col_add = st.columns([1, 1.5], gap="large")

with col_config:
    with st.container(border=True):
        st.subheader("⚙️ Algorithm Settings")
        algo = st.selectbox("Select Strategy", ["FCFS", "SJF", "Round Robin (RR)"])
        quantum = 4
        if algo == "Round Robin (RR)":
            quantum = st.number_input("Time Quantum (ms)", value=4, min_value=1)
        
        c1, c2 = st.columns(2)
        if c1.button("▶ Run Simulation", type="primary", use_container_width=True):
            if algo == "FCFS":
                st.session_state.results, st.session_state.gantt, _ = fcfs_scheduling(st.session_state.processes)
            elif algo == "SJF":
                st.session_state.results, st.session_state.gantt, _ = sjf_scheduling(st.session_state.processes)
            else:
                st.session_state.results, st.session_state.gantt, _ = round_robin_scheduling(st.session_state.processes, quantum)
        
        if c2.button("🗑️ Reset", use_container_width=True):
            st.session_state.results = None
            st.session_state.gantt = None
            st.rerun()

with col_add:
    with st.container(border=True):
        st.subheader("➕ Add New Process")
        with st.form("new_process", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            n = f1.text_input("Process Name", value=f"P{len(st.session_state.processes)+1}")
            a = f2.number_input("Arrival", min_value=0, step=1)
            b = f3.number_input("Burst", min_value=1, step=1)
            if st.form_submit_button("Add to Queue", use_container_width=True):
                st.session_state.processes.append({'name': n, 'arrival': a, 'burst': b, 'priority': 1})
                st.rerun()

st.divider()

# TABLE & VISUALIZATION
col_table, col_viz = st.columns([1, 2], gap="large")

with col_table:
    st.subheader("Process Queue")
    df = pd.DataFrame(st.session_state.processes)
    st.dataframe(df[['name', 'arrival', 'burst']], use_container_width=True, hide_index=True)
    
    proc_to_del = st.selectbox("Remove Process", [p['name'] for p in st.session_state.processes])
    if st.button("Delete Selected"):
        st.session_state.processes = [p for p in st.session_state.processes if p['name'] != proc_to_del]
        st.rerun()

with col_viz:
    if st.session_state.gantt:
        st.subheader("Gantt Chart")
        
        fig = go.Figure()
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
        for i, item in enumerate(st.session_state.gantt):
            fig.add_trace(go.Bar(
                x=[item['end'] - item['start']], base=item['start'],
                y=['CPU'], orientation='h', name=item['process'],
                marker_color=colors[i % len(colors)] if item['process'] != 'IDLE' else '#d1d5db',
                text=item['process'], textposition='inside'
            ))
        fig.update_layout(barmode='stack', height=150, showlegend=False, margin=dict(l=10, r=10, t=10, b=30))
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics
        st.subheader("Performance Metrics")
        res_df = pd.DataFrame(st.session_state.results)
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-box"><div class="metric-value">{res_df["Waiting"].mean():.2f}</div><div class="metric-label">Avg Waiting</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-box"><div class="metric-value">{res_df["Turnaround"].mean():.2f}</div><div class="metric-label">Avg Turnaround</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-box"><div class="metric-value">{len(st.session_state.processes)}</div><div class="metric-label">Total Processes</div></div>', unsafe_allow_html=True)
    else:
        st.info("Configure the processes and click 'Run Simulation' to see results.")