import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import copy

# Page configuration
st.set_page_config(
    page_title="I/O Systems - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border: #e2e8f0;
    }
    
    .track-marker {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 900;
        color: #2563eb;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #9ca3af;
        text-transform: uppercase;
    }
    
    .request-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
        border: 1px solid #e2e8f0;
    }
    
    .request-item-active {
        background-color: rgba(37, 99, 235, 0.1);
        border-color: rgba(0, 165, 173, 0.3);
    }
    
    .log-container {
        background-color: #111827;
        border-radius: 8px;
        padding: 1rem;
        font-family: monospace;
        font-size: 11px;
        color: #9ca3af;
        max-height: 250px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ============== DISK SCHEDULING ALGORITHMS ==============

def fcfs_disk(requests, head):
    """First Come First Serve Disk Scheduling"""
    sequence = [head] + requests.copy()
    total_seek = 0
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FCFS: Starting FCFS disk scheduling")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    for i in range(1, len(sequence)):
        seek = abs(sequence[i] - sequence[i-1])
        total_seek += seek
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {sequence[i-1]} → {sequence[i]} (seek: {seek})")
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


def sstf_disk(requests, head):
    """Shortest Seek Time First Disk Scheduling"""
    remaining = requests.copy()
    sequence = [head]
    total_seek = 0
    current = head
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SSTF: Starting Shortest Seek Time First scheduling")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    while remaining:
        # Find closest request
        distances = [(abs(r - current), r) for r in remaining]
        distances.sort(key=lambda x: x[0])
        
        closest_dist, closest = distances[0]
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SCAN: Evaluating distances: {[(r, abs(r-current)) for r in remaining]}")
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SELECT: Track {closest} is nearest (distance: {closest_dist})")
        
        sequence.append(closest)
        total_seek += closest_dist
        current = closest
        remaining.remove(closest)
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: Head moved to {closest}")
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


def scan_disk(requests, head, disk_size, direction='right'):
    """SCAN (Elevator) Disk Scheduling"""
    sequence = [head]
    total_seek = 0
    current = head
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SCAN: Starting SCAN algorithm (direction: {direction})")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    
    if direction == 'right':
        # Go right first
        for track in right:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
        
        # Go to end if needed
        if right and current < disk_size - 1:
            seek = abs(disk_size - 1 - current)
            total_seek += seek
            sequence.append(disk_size - 1)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] BOUNDARY: Moving to end: {disk_size - 1}")
            current = disk_size - 1
        
        # Then go left
        for track in left:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
    else:
        # Go left first
        for track in left:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
        
        # Go to start
        if left and current > 0:
            seek = current
            total_seek += seek
            sequence.append(0)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] BOUNDARY: Moving to start: 0")
            current = 0
        
        # Then go right
        for track in right:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


def look_disk(requests, head, direction='right'):
    """LOOK Disk Scheduling (like SCAN but doesn't go to ends)"""
    sequence = [head]
    total_seek = 0
    current = head
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] LOOK: Starting LOOK algorithm (direction: {direction})")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    
    if direction == 'right':
        for track in right:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
        
        for track in left:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
    else:
        for track in left:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
        
        for track in right:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


def cscan_disk(requests, head, disk_size):
    """C-SCAN Disk Scheduling"""
    sequence = [head]
    total_seek = 0
    current = head
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] C-SCAN: Starting Circular SCAN algorithm")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    
    # Go right
    for track in right:
        seek = abs(track - current)
        total_seek += seek
        sequence.append(track)
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
        current = track
    
    # Jump to end then to start
    if right:
        seek = abs(disk_size - 1 - current)
        total_seek += seek
        sequence.append(disk_size - 1)
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] BOUNDARY: Moving to end: {disk_size - 1}")
        current = disk_size - 1
    
    if left:
        seek = current  # Jump to 0
        total_seek += seek
        sequence.append(0)
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] JUMP: Jumping to start: 0")
        current = 0
    
    # Continue from left
    for track in left:
        seek = abs(track - current)
        total_seek += seek
        sequence.append(track)
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
        current = track
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


def clook_disk(requests, head):
    """C-LOOK Disk Scheduling"""
    sequence = [head]
    total_seek = 0
    current = head
    log = []
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] C-LOOK: Starting Circular LOOK algorithm")
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] INIT: Initial head position: {head}")
    
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    
    # Go right
    for track in right:
        seek = abs(track - current)
        total_seek += seek
        sequence.append(track)
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
        current = track
    
    # Jump to leftmost
    if left:
        seek = abs(left[0] - current)
        total_seek += seek
        sequence.append(left[0])
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] JUMP: Jumping to {left[0]}")
        current = left[0]
        
        for track in left[1:]:
            seek = abs(track - current)
            total_seek += seek
            sequence.append(track)
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] MOVE: {current} → {track} (seek: {seek})")
            current = track
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETE: Total seek distance: {total_seek}")
    
    return sequence, total_seek, log


# Initialize session state
if 'disk_size' not in st.session_state:
    st.session_state.disk_size = 200

if 'initial_head' not in st.session_state:
    st.session_state.initial_head = 53

if 'requests' not in st.session_state:
    st.session_state.requests = [98, 183, 37, 122, 14, 124, 65, 67]

if 'sequence' not in st.session_state:
    st.session_state.sequence = None

if 'total_seek' not in st.session_state:
    st.session_state.total_seek = 0

if 'disk_log' not in st.session_state:
    st.session_state.disk_log = [
        f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM: Disk scheduling simulator initialized",
        f"[{datetime.now().strftime('%H:%M:%S')}] CONFIG: Disk size: 200 tracks, Initial head: 53"
    ]

# SIDEBAR
with st.sidebar:
    st.markdown("**OS SIMULATOR**")
    st.caption("v1.2.0 - I/O Systems Module")
    st.divider()
    
    st.markdown("**OS MODULES**")
    modules = ["Process Management", "Memory Management", "File Systems", "I/O Systems"]
    selected_module = st.radio("Select Module:", modules, index=3, label_visibility="collapsed")
    
    if selected_module == "Process Management":
        st.switch_page("pages/1_Process_Management.py")
    elif selected_module == "Memory Management":
        st.switch_page("pages/2_Memory_Management.py")
    elif selected_module == "File Systems":
        st.switch_page("pages/3_File_Systems.py")
    
    st.divider()
    
    st.markdown("**SCHEDULING ALGORITHM**")
    algorithm = st.selectbox(
        "Select Algorithm:",
        ["FCFS (First Come First Serve)", "SSTF (Shortest Seek Time First)", 
         "SCAN (Elevator)", "LOOK", "C-SCAN (Circular SCAN)", "C-LOOK (Circular LOOK)"],
        index=1,
        label_visibility="collapsed"
    )
    
    if "SCAN" in algorithm:
        direction = st.radio("Direction:", ["Right (→)", "Left (←)"], horizontal=True)
        scan_direction = 'right' if "Right" in direction else 'left'
    else:
        scan_direction = 'right'
    
    st.divider()
    
    st.markdown("**INITIAL HEAD POSITION**")
    initial_head = st.number_input("Head:", value=53, min_value=0, max_value=199, label_visibility="collapsed")
    st.session_state.initial_head = initial_head
    
    st.markdown("**DISK SIZE (Tracks)**")
    disk_size = st.number_input("Size:", value=200, min_value=100, max_value=500, label_visibility="collapsed")
    st.session_state.disk_size = disk_size
    
    st.divider()
    
    st.markdown("**ADD REQUEST**")
    with st.form("add_request"):
        new_track = st.number_input("Track #:", value=50, min_value=0, max_value=disk_size-1)
        if st.form_submit_button("Add Request", use_container_width=True):
            if new_track not in st.session_state.requests:
                st.session_state.requests.append(new_track)
                st.session_state.disk_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] REQUEST: Added track {new_track}")
                st.rerun()
    
    st.divider()
    
    if st.button("Run Simulation", use_container_width=True, type="primary"):
        if algorithm == "FCFS (First Come First Serve)":
            seq, seek, log = fcfs_disk(st.session_state.requests, st.session_state.initial_head)
        elif algorithm == "SSTF (Shortest Seek Time First)":
            seq, seek, log = sstf_disk(st.session_state.requests, st.session_state.initial_head)
        elif algorithm == "SCAN (Elevator)":
            seq, seek, log = scan_disk(st.session_state.requests, st.session_state.initial_head, 
                                       st.session_state.disk_size, scan_direction)
        elif algorithm == "LOOK":
            seq, seek, log = look_disk(st.session_state.requests, st.session_state.initial_head, scan_direction)
        elif algorithm == "C-SCAN (Circular SCAN)":
            seq, seek, log = cscan_disk(st.session_state.requests, st.session_state.initial_head, 
                                        st.session_state.disk_size)
        else:
            seq, seek, log = clook_disk(st.session_state.requests, st.session_state.initial_head)
        
        st.session_state.sequence = seq
        st.session_state.total_seek = seek
        st.session_state.disk_log = log + st.session_state.disk_log
        st.rerun()
    
    if st.button("Reset", use_container_width=True):
        st.session_state.requests = [98, 183, 37, 122, 14, 124, 65, 67]
        st.session_state.sequence = None
        st.session_state.total_seek = 0
        st.session_state.disk_log = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM: Simulator reset"]
        st.rerun()

# MAIN CONTENT
st.markdown("## Disk Scheduling & Seek Analysis")
st.markdown("Simulate disk scheduling algorithms with head movement visualization and seek time analysis.")

st.divider()

# Track Layout - Using Plotly for reliable rendering
st.markdown("### Disk Track Layout")
with st.container(border=True):
    # Create track visualization with Plotly
    fig_track = go.Figure()
    
    # Add track line
    fig_track.add_trace(go.Scatter(
        x=[0, st.session_state.disk_size - 1],
        y=[0, 0],
        mode='lines',
        line=dict(color='#9ca3af', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add request markers
    fig_track.add_trace(go.Scatter(
        x=st.session_state.requests,
        y=[0] * len(st.session_state.requests),
        mode='markers',
        marker=dict(size=12, color='#6b7280', symbol='circle'),
        name='Pending Requests',
        hovertemplate='Track %{x}<extra></extra>'
    ))
    
    # Add head position
    fig_track.add_trace(go.Scatter(
        x=[st.session_state.initial_head],
        y=[0],
        mode='markers+text',
        marker=dict(size=18, color='#2563eb', symbol='triangle-up'),
        text=[f'Head: {st.session_state.initial_head}'],
        textposition='top center',
        name='Head Position',
        hovertemplate='Head at Track %{x}<extra></extra>'
    ))
    
    fig_track.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title='Track Number',
            range=[-5, st.session_state.disk_size + 5],
            showgrid=True,
            gridcolor='#e5e7eb'
        ),
        yaxis=dict(visible=False, range=[-0.5, 0.5]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    
    st.plotly_chart(fig_track, use_container_width=True)
    
    # Show request queue
    st.caption(f"**Request Queue:** {', '.join(map(str, st.session_state.requests))}")

st.divider()

# Results Section
col_graph, col_metrics = st.columns([3, 1], gap="large")

with col_graph:
    st.markdown("### Head Movement Graph")
    with st.container(border=True):
        if st.session_state.sequence:
            # Create movement graph
            fig = go.Figure()
            
            # Line plot
            fig.add_trace(go.Scatter(
                x=list(range(len(st.session_state.sequence))),
                y=st.session_state.sequence,
                mode='lines+markers',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=10, color='#2563eb'),
                hovertemplate='<b>Step %{x}</b><br>Track: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                height=350,
                margin=dict(l=40, r=20, t=20, b=40),
                xaxis_title="Request Order",
                yaxis_title="Track Number",
                yaxis=dict(range=[0, st.session_state.disk_size]),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
                yaxis_gridcolor='#e5e7eb'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sequence display
            st.markdown("**Seek Sequence:**")
            st.code(" → ".join(map(str, st.session_state.sequence)))
        else:
            st.info("Click 'Run Simulation' to see the head movement graph")

with col_metrics:
    st.markdown("### Performance")
    
    if st.session_state.sequence:
        avg_seek = st.session_state.total_seek / (len(st.session_state.sequence) - 1) if len(st.session_state.sequence) > 1 else 0
        
        st.metric("Total Seek Distance", f"{st.session_state.total_seek} tracks")
        st.metric("Avg. Seek per Request", f"{avg_seek:.1f} tracks")
        
        efficiency = max(0, 100 - (st.session_state.total_seek / (st.session_state.disk_size * len(st.session_state.requests)) * 100))
        st.metric("Efficiency Rating", f"{efficiency:.0f}%")
    
    # Request Queue
    st.markdown("### Request Queue")
    with st.container(border=True):
        for i, req in enumerate(st.session_state.requests):
            if i == 0:
                st.success(f"▶ Next: Track {req}")
            else:
                st.text(f"  Track {req}")

st.divider()

# Algorithm Log
st.markdown("### Algorithm Log")
with st.container(border=True):
    log_text = "\n".join(st.session_state.disk_log[:25])
    st.code(log_text, language="text")

st.divider()
st.caption("OS Simulator | I/O Systems & Disk Scheduling | v1.2.0")
