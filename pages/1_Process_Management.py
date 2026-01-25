import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import copy

# Page configuration
st.set_page_config(
    page_title="Process Management - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #475569;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
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
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #3b82f6;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        border-left: 3px solid var(--primary);
        padding-left: 0.75rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============== CPU SCHEDULING ALGORITHMS ==============

def fcfs_scheduling(processes):
    """First Come First Serve Scheduling"""
    n = len(processes)
    processes_sorted = sorted(processes, key=lambda x: x['arrival'])
    
    gantt = []
    current_time = 0
    results = []
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FCFS: Starting First Come First Serve scheduling")
    
    for p in processes_sorted:
        if current_time < p['arrival']:
            if current_time < p['arrival']:
                gantt.append({'process': 'IDLE', 'start': current_time, 'end': p['arrival']})
            current_time = p['arrival']
        
        start_time = current_time
        end_time = current_time + p['burst']
        
        waiting_time = start_time - p['arrival']
        turnaround_time = end_time - p['arrival']
        
        gantt.append({'process': p['name'], 'start': start_time, 'end': end_time})
        
        results.append({
            'Process': p['name'],
            'Arrival': p['arrival'],
            'Burst': p['burst'],
            'Priority': p.get('priority', '-'),
            'Start': start_time,
            'Finish': end_time,
            'Waiting': waiting_time,
            'Turnaround': turnaround_time
        })
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCH: {p['name']} started at t={start_time}, will finish at t={end_time}")
        current_time = end_time
    
    return results, gantt, log


def sjf_scheduling(processes):
    """Shortest Job First (Non-preemptive) Scheduling"""
    n = len(processes)
    remaining = copy.deepcopy(processes)
    
    gantt = []
    current_time = 0
    results = []
    log = []
    completed = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SJF: Starting Shortest Job First scheduling (Non-preemptive)")
    
    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        
        if not available:
            next_arrival = min(p['arrival'] for p in remaining)
            gantt.append({'process': 'IDLE', 'start': current_time, 'end': next_arrival})
            current_time = next_arrival
            continue
        
        # Select shortest job
        shortest = min(available, key=lambda x: x['burst'])
        remaining.remove(shortest)
        
        start_time = current_time
        end_time = current_time + shortest['burst']
        
        waiting_time = start_time - shortest['arrival']
        turnaround_time = end_time - shortest['arrival']
        
        gantt.append({'process': shortest['name'], 'start': start_time, 'end': end_time})
        
        results.append({
            'Process': shortest['name'],
            'Arrival': shortest['arrival'],
            'Burst': shortest['burst'],
            'Priority': shortest.get('priority', '-'),
            'Start': start_time,
            'Finish': end_time,
            'Waiting': waiting_time,
            'Turnaround': turnaround_time
        })
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SELECT: {shortest['name']} (burst={shortest['burst']}) - shortest available job")
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCH: {shortest['name']} runs t={start_time} to t={end_time}")
        
        current_time = end_time
    
    return results, gantt, log


def priority_scheduling(processes):
    """Priority Scheduling (Non-preemptive, lower number = higher priority)"""
    n = len(processes)
    remaining = copy.deepcopy(processes)
    
    gantt = []
    current_time = 0
    results = []
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] PRIORITY: Starting Priority scheduling (lower = higher priority)")
    
    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        
        if not available:
            next_arrival = min(p['arrival'] for p in remaining)
            gantt.append({'process': 'IDLE', 'start': current_time, 'end': next_arrival})
            current_time = next_arrival
            continue
        
        # Select highest priority (lowest number)
        highest_priority = min(available, key=lambda x: x['priority'])
        remaining.remove(highest_priority)
        
        start_time = current_time
        end_time = current_time + highest_priority['burst']
        
        waiting_time = start_time - highest_priority['arrival']
        turnaround_time = end_time - highest_priority['arrival']
        
        gantt.append({'process': highest_priority['name'], 'start': start_time, 'end': end_time})
        
        results.append({
            'Process': highest_priority['name'],
            'Arrival': highest_priority['arrival'],
            'Burst': highest_priority['burst'],
            'Priority': highest_priority['priority'],
            'Start': start_time,
            'Finish': end_time,
            'Waiting': waiting_time,
            'Turnaround': turnaround_time
        })
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SELECT: {highest_priority['name']} (priority={highest_priority['priority']}) - highest priority")
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCH: {highest_priority['name']} runs t={start_time} to t={end_time}")
        
        current_time = end_time
    
    return results, gantt, log


def round_robin_scheduling(processes, quantum):
    """Round Robin Scheduling"""
    n = len(processes)
    remaining = copy.deepcopy(processes)
    for p in remaining:
        p['remaining'] = p['burst']
    
    gantt = []
    current_time = 0
    results = {p['name']: {'arrival': p['arrival'], 'burst': p['burst'], 'priority': p.get('priority', '-'), 
                           'finish': 0, 'waiting': 0} for p in processes}
    log = []
    ready_queue = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] RR: Starting Round Robin scheduling (quantum={quantum}ms)")
    
    # Sort by arrival time
    remaining.sort(key=lambda x: x['arrival'])
    
    while remaining or ready_queue:
        # Add newly arrived processes to ready queue
        while remaining and remaining[0]['arrival'] <= current_time:
            ready_queue.append(remaining.pop(0))
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] QUEUE_ADD: {ready_queue[-1]['name']} added to ready queue")
        
        if not ready_queue:
            if remaining:
                next_arrival = remaining[0]['arrival']
                gantt.append({'process': 'IDLE', 'start': current_time, 'end': next_arrival})
                current_time = next_arrival
            continue
        
        # Get next process from queue
        current_process = ready_queue.pop(0)
        
        # Execute for quantum or remaining time
        exec_time = min(quantum, current_process['remaining'])
        start_time = current_time
        end_time = current_time + exec_time
        
        gantt.append({'process': current_process['name'], 'start': start_time, 'end': end_time})
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] DISPATCH: {current_process['name']} runs for {exec_time}ms (remaining: {current_process['remaining'] - exec_time}ms)")
        
        current_process['remaining'] -= exec_time
        current_time = end_time
        
        # Add newly arrived processes before adding current back
        while remaining and remaining[0]['arrival'] <= current_time:
            ready_queue.append(remaining.pop(0))
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] QUEUE_ADD: {ready_queue[-1]['name']} added to ready queue")
        
        if current_process['remaining'] > 0:
            ready_queue.append(current_process)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] PREEMPT: {current_process['name']} preempted, back to queue")
        else:
            results[current_process['name']]['finish'] = end_time
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: {current_process['name']} finished at t={end_time}")
    
    # Calculate waiting and turnaround times
    final_results = []
    for name, data in results.items():
        turnaround = data['finish'] - data['arrival']
        waiting = turnaround - data['burst']
        final_results.append({
            'Process': name,
            'Arrival': data['arrival'],
            'Burst': data['burst'],
            'Priority': data['priority'],
            'Start': '-',
            'Finish': data['finish'],
            'Waiting': waiting,
            'Turnaround': turnaround
        })
    
    final_results.sort(key=lambda x: x['Process'])
    return final_results, gantt, log


# Initialize session state
if 'processes' not in st.session_state:
    st.session_state.processes = [
        {'name': 'P1', 'arrival': 0, 'burst': 8, 'priority': 2},
        {'name': 'P2', 'arrival': 1, 'burst': 4, 'priority': 1},
        {'name': 'P3', 'arrival': 2, 'burst': 9, 'priority': 3},
        {'name': 'P4', 'arrival': 3, 'burst': 5, 'priority': 2},
    ]

if 'results' not in st.session_state:
    st.session_state.results = None

if 'gantt' not in st.session_state:
    st.session_state.gantt = None

if 'log' not in st.session_state:
    st.session_state.log = []

# SIDEBAR
with st.sidebar:
    st.markdown("**OS SIMULATOR**")
    st.caption("v2.0 | Process Management")
    st.divider()
    
    st.markdown("**MODULES**")
    modules = ["Process Management", "Memory Management", "File Systems", "I/O Systems"]
    selected_module = st.radio("Select Module:", modules, index=0, label_visibility="collapsed")
    
    if selected_module == "Memory Management":
        st.switch_page("pages/2_Memory_Management.py")
    elif selected_module == "File Systems":
        st.switch_page("pages/3_File_Systems.py")
    elif selected_module == "I/O Systems":
        st.switch_page("pages/4_IO_Systems.py")
    
    st.divider()
    
    st.markdown("**SCHEDULING ALGORITHM**")
    algorithm = st.selectbox(
        "Select Algorithm:",
        ["First Come First Serve (FCFS)", "Shortest Job First (SJF)", "Priority Scheduling", "Round Robin (RR)"],
        label_visibility="collapsed"
    )
    
    if algorithm == "Round Robin (RR)":
        st.markdown("**TIME QUANTUM (ms)**")
        quantum = st.number_input("Quantum:", value=4, min_value=1, max_value=20, label_visibility="collapsed")
    else:
        quantum = 4
    
    st.divider()
    
    st.markdown("**ADD NEW PROCESS**")
    with st.form("add_process"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name", value=f"P{len(st.session_state.processes)+1}")
            new_arrival = st.number_input("Arrival", value=0, min_value=0)
        with col2:
            new_burst = st.number_input("Burst", value=5, min_value=1)
            new_priority = st.number_input("Priority", value=1, min_value=1)
        
        if st.form_submit_button("Add Process", use_container_width=True):
            st.session_state.processes.append({
                'name': new_name,
                'arrival': new_arrival,
                'burst': new_burst,
                'priority': new_priority
            })
            st.rerun()
    
    st.divider()
    
    if st.button("Reset All", use_container_width=True):
        st.session_state.processes = [
            {'name': 'P1', 'arrival': 0, 'burst': 8, 'priority': 2},
            {'name': 'P2', 'arrival': 1, 'burst': 4, 'priority': 1},
            {'name': 'P3', 'arrival': 2, 'burst': 9, 'priority': 3},
            {'name': 'P4', 'arrival': 3, 'burst': 5, 'priority': 2},
        ]
        st.session_state.results = None
        st.session_state.gantt = None
        st.session_state.log = []
        st.rerun()

# MAIN CONTENT
st.markdown("## CPU Scheduling Visualization")
st.caption("Simulate and visualize CPU scheduling algorithms with Gantt chart and performance metrics.")

# Header buttons
col1, col2, col3 = st.columns([1, 1, 6])
with col1:
    run_sim = st.button("Run Simulation", type="primary", use_container_width=True)
with col2:
    if st.button("Clear Results", use_container_width=True):
        st.session_state.results = None
        st.session_state.gantt = None
        st.session_state.log = []
        st.rerun()

st.divider()

# Process Input Table
st.markdown("### Process Queue")
col_table, col_edit = st.columns([3, 1])

with col_table:
    df = pd.DataFrame(st.session_state.processes)
    df.columns = ['Process', 'Arrival Time', 'Burst Time', 'Priority']
    st.dataframe(df, use_container_width=True, hide_index=True)

with col_edit:
    st.markdown("**Quick Actions**")
    process_to_remove = st.selectbox("Remove Process:", [p['name'] for p in st.session_state.processes])
    if st.button("Remove", use_container_width=True):
        st.session_state.processes = [p for p in st.session_state.processes if p['name'] != process_to_remove]
        st.rerun()

# Run Simulation
if run_sim:
    if algorithm == "First Come First Serve (FCFS)":
        results, gantt, log = fcfs_scheduling(st.session_state.processes)
    elif algorithm == "Shortest Job First (SJF)":
        results, gantt, log = sjf_scheduling(st.session_state.processes)
    elif algorithm == "Priority Scheduling":
        results, gantt, log = priority_scheduling(st.session_state.processes)
    else:
        results, gantt, log = round_robin_scheduling(st.session_state.processes, quantum)
    
    st.session_state.results = results
    st.session_state.gantt = gantt
    st.session_state.log = log

# Display Results
if st.session_state.results:
    st.divider()
    
    # Gantt Chart
    st.markdown("### Execution Gantt Chart")
    with st.container(border=True):
        # Create Gantt chart using Plotly
        colors = {'P1': '#00a5ad', 'P2': '#3b82f6', 'P3': '#f59e0b', 'P4': '#10b981', 
                  'P5': '#8b5cf6', 'P6': '#ef4444', 'P7': '#ec4899', 'IDLE': '#d1d5db'}
        
        fig = go.Figure()
        
        for item in st.session_state.gantt:
            color = colors.get(item['process'], '#6b7280')
            fig.add_trace(go.Bar(
                y=['CPU'],
                x=[item['end'] - item['start']],
                base=item['start'],
                orientation='h',
                name=item['process'],
                text=item['process'],
                textposition='inside',
                marker_color=color,
                hovertemplate=f"<b>{item['process']}</b><br>Start: {item['start']}ms<br>End: {item['end']}ms<extra></extra>"
            ))
        
        fig.update_layout(
            barmode='stack',
            height=120,
            margin=dict(l=20, r=20, t=20, b=40),
            xaxis_title="Time (ms)",
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Time markers
        if st.session_state.gantt:
            max_time = max(g['end'] for g in st.session_state.gantt)
            time_labels = ' | '.join([f"{i}ms" for i in range(0, int(max_time) + 1, max(1, int(max_time)//10))])
            st.caption(f"Timeline: {time_labels}")
    
    # Results and Metrics
    col_results, col_metrics = st.columns([2, 1])
    
    with col_results:
        st.markdown("### Scheduling Results")
        results_df = pd.DataFrame(st.session_state.results)
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    with col_metrics:
        st.markdown("### Performance Metrics")
        
        avg_waiting = sum(r['Waiting'] for r in st.session_state.results) / len(st.session_state.results)
        avg_turnaround = sum(r['Turnaround'] for r in st.session_state.results) / len(st.session_state.results)
        
        total_burst = sum(p['burst'] for p in st.session_state.processes)
        max_time = max(g['end'] for g in st.session_state.gantt)
        cpu_util = (total_burst / max_time) * 100 if max_time > 0 else 0
        
        metric_html = f"""
        <div class="metric-box" style="margin-bottom: 1rem;">
            <div class="metric-value">{avg_waiting:.2f}</div>
            <div class="metric-label">Avg. Waiting Time (ms)</div>
        </div>
        <div class="metric-box" style="margin-bottom: 1rem;">
            <div class="metric-value">{avg_turnaround:.2f}</div>
            <div class="metric-label">Avg. Turnaround Time (ms)</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">{cpu_util:.1f}%</div>
            <div class="metric-label">CPU Utilization</div>
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    # System Log
    st.markdown("### Execution Log")
    with st.container(border=True):
        log_text = "\n".join(st.session_state.log)
        st.code(log_text, language="text")

st.divider()
st.caption("OS Simulator v2.0 | Process Management Module")