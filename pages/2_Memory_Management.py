import streamlit as st
import pandas as pd
from datetime import datetime
import copy

# Page configuration
st.set_page_config(
    page_title="Memory Management - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --allocated: #3b82f6;
        --free: #22c55e;
        --fragmented: #ef4444;
    }
    .metric-card {
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

# ============== MEMORY ALLOCATION ALGORITHMS ==============

def allocate_memory(blocks, size, name, method):
    log = []
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {method.upper()}: Requesting {size}KB for {name}")
    
    target_idx = -1
    
    if method == "First Fit":
        for i, block in enumerate(blocks):
            if block['status'] == 'Free' and block['size'] >= size:
                target_idx = i
                break
    
    elif method == "Best Fit":
        best_size = float('inf')
        for i, block in enumerate(blocks):
            if block['status'] == 'Free' and block['size'] >= size:
                if block['size'] < best_size:
                    best_size = block['size']
                    target_idx = i
                    
    elif method == "Worst Fit":
        worst_size = -1
        for i, block in enumerate(blocks):
            if block['status'] == 'Free' and block['size'] >= size:
                if block['size'] > worst_size:
                    worst_size = block['size']
                    target_idx = i

    if target_idx != -1:
        frag = blocks[target_idx]['size'] - size
        blocks[target_idx].update({
            'status': 'Allocated', 'process': name, 
            'allocated_size': size, 'internal_frag': frag
        })
        log.append(f"SUCCESS: Allocated to Block {blocks[target_idx]['id']} (Frag: {frag}KB)")
        return True, blocks, log
    
    log.append(f"FAILED: No suitable block found.")
    return False, blocks, log

# ============== SESSION STATE ==============
if 'memory_blocks' not in st.session_state:
    st.session_state.memory_blocks = [
        {'id': 1, 'size': 100, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 2, 'size': 500, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 3, 'size': 200, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 4, 'size': 300, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 5, 'size': 600, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
    ]
if 'mem_log' not in st.session_state: st.session_state.mem_log = []
if 'p_count' not in st.session_state: st.session_state.p_count = 1

# ============== SIDEBAR (Navigation Only) ==============
with st.sidebar:
    st.title("OS Simulator")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("main.py")
    st.divider()
    st.caption("Module: Memory Management")

# ============== MAIN UI ==============
st.title("🧠 Memory Management & Allocation")

# MANAGEMENT DASHBOARD
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3, gap="large")

with ctrl_col1:
    with st.container(border=True):
        st.subheader("📥 Allocate Process")
        method = st.selectbox("Search Strategy", ["First Fit", "Best Fit", "Worst Fit"])
        p_name = st.text_input("Process Name", value=f"P{st.session_state.p_count}")
        p_size = st.number_input("Required Size (KB)", min_value=1, value=150)
        if st.button("Allocate", type="primary", use_container_width=True):
            success, new_blocks, logs = allocate_memory(
                copy.deepcopy(st.session_state.memory_blocks), p_size, p_name, method
            )
            st.session_state.mem_log = logs + st.session_state.mem_log
            if success:
                st.session_state.memory_blocks = new_blocks
                st.session_state.p_count += 1
                st.toast(f"Allocated {p_name}")
            else:
                st.error("Insufficient Memory")
            st.rerun()

with ctrl_col2:
    with st.container(border=True):
        st.subheader("📤 Deallocate Process")
        allocated = [b['process'] for b in st.session_state.memory_blocks if b['status'] == 'Allocated']
        if allocated:
            to_free = st.selectbox("Select Process", allocated)
            if st.button("Free Memory", use_container_width=True):
                for b in st.session_state.memory_blocks:
                    if b['process'] == to_free:
                        b.update({'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0})
                st.session_state.mem_log.insert(0, f"DEALLOCATED: {to_free} released")
                st.rerun()
        else:
            st.info("No active allocations.")

with ctrl_col3:
    with st.container(border=True):
        st.subheader("🛠️ System Config")
        new_b_size = st.number_input("New Block Size", value=200, min_value=10)
        if st.button("Add Memory Block", use_container_width=True):
            new_id = max(b['id'] for b in st.session_state.memory_blocks) + 1
            st.session_state.memory_blocks.append({
                'id': new_id, 'size': new_b_size, 'status': 'Free', 
                'process': None, 'allocated_size': 0, 'internal_frag': 0
            })
            st.rerun()
        if st.button("Reset RAM", type="primary", use_container_width=True):
            st.session_state.memory_blocks = []
            st.session_state.p_count = 1
            st.rerun()

st.divider()

# VISUALIZATION AREA
vis_col1, vis_col2 = st.columns([1, 2], gap="large")

with vis_col1:
    st.subheader("RAM Map Visualization")
    
    total_mem = sum(b['size'] for b in st.session_state.memory_blocks)
    for b in st.session_state.memory_blocks:
        h = max(30, int((b['size']/total_mem)*500))
        color = "#3b82f6" if b['status'] == 'Allocated' else "#22c55e"
        label = f"{b['process']} ({b['allocated_size']}KB)" if b['status'] == 'Allocated' else f"FREE ({b['size']}KB)"
        
        st.markdown(f"""
            <div style="background:{color}; height:{h}px; border:1px solid white; border-radius:4px; 
            display:flex; align-items:center; justify-content:center; color:white; font-size:12px; font-weight:bold; margin-bottom:2px;">
                {label}
            </div>
        """, unsafe_allow_html=True)

with vis_col2:
    st.subheader("Fragmentation & Metrics")
    m1, m2, m3 = st.columns(3)
    
    total_alloc = sum(b['allocated_size'] for b in st.session_state.memory_blocks)
    total_frag = sum(b['internal_frag'] for b in st.session_state.memory_blocks)
    util = (total_alloc / total_mem * 100) if total_mem > 0 else 0
    
    m1.markdown(f'<div class="metric-card"><div class="metric-value">{util:.1f}%</div><div class="metric-label">Utilization</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ef4444">{total_frag}KB</div><div class="metric-label">Internal Frag</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-value">{total_mem}KB</div><div class="metric-label">Total RAM</div></div>', unsafe_allow_html=True)
    
    st.dataframe(pd.DataFrame(st.session_state.memory_blocks), use_container_width=True, hide_index=True)
    
    st.subheader("System Log")
    st.code("\n".join(st.session_state.mem_log[:10]))

st.divider()
st.caption("OS Simulator v2.0 | Memory Management Module")