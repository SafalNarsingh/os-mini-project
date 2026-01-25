import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import copy

# Page configuration
st.set_page_config(
    page_title="Memory Management - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --allocated: #3b82f6;
        --free: #22c55e;
        --fragmented: #ef4444;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 0.75rem;
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
</style>
""", unsafe_allow_html=True)

# ============== MEMORY ALLOCATION ALGORITHMS ==============

def first_fit(memory_blocks, process_size, process_name):
    """First Fit: Allocate to first block that fits"""
    log = []
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FIRST_FIT: Searching for {process_size}KB block for {process_name}")
    
    for i, block in enumerate(memory_blocks):
        log.append(f"  ↳ Checking Block {i+1}: {block['size']}KB ({block['status']})")
        if block['status'] == 'Free' and block['size'] >= process_size:
            # Allocate
            internal_frag = block['size'] - process_size
            block['status'] = 'Allocated'
            block['process'] = process_name
            block['allocated_size'] = process_size
            block['internal_frag'] = internal_frag
            
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS: Allocated {process_name} to Block {i+1}")
            log.append(f"  ↳ Internal Fragmentation: {internal_frag}KB")
            return True, memory_blocks, log, i+1, internal_frag
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FAILED: No suitable block found for {process_name}")
    return False, memory_blocks, log, -1, 0


def best_fit(memory_blocks, process_size, process_name):
    """Best Fit: Allocate to smallest block that fits"""
    log = []
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] BEST_FIT: Searching for smallest suitable block for {process_name} ({process_size}KB)")
    
    best_idx = -1
    best_size = float('inf')
    
    for i, block in enumerate(memory_blocks):
        log.append(f"  ↳ Checking Block {i+1}: {block['size']}KB ({block['status']})")
        if block['status'] == 'Free' and block['size'] >= process_size:
            if block['size'] < best_size:
                best_size = block['size']
                best_idx = i
                log.append(f"    → Candidate found (size difference: {block['size'] - process_size}KB)")
    
    if best_idx != -1:
        internal_frag = memory_blocks[best_idx]['size'] - process_size
        memory_blocks[best_idx]['status'] = 'Allocated'
        memory_blocks[best_idx]['process'] = process_name
        memory_blocks[best_idx]['allocated_size'] = process_size
        memory_blocks[best_idx]['internal_frag'] = internal_frag
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS: Best fit is Block {best_idx+1} ({best_size}KB)")
        log.append(f"  ↳ Internal Fragmentation: {internal_frag}KB")
        return True, memory_blocks, log, best_idx+1, internal_frag
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FAILED: No suitable block found for {process_name}")
    return False, memory_blocks, log, -1, 0


def worst_fit(memory_blocks, process_size, process_name):
    """Worst Fit: Allocate to largest block that fits"""
    log = []
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] WORST_FIT: Searching for largest suitable block for {process_name} ({process_size}KB)")
    
    worst_idx = -1
    worst_size = -1
    
    for i, block in enumerate(memory_blocks):
        log.append(f"  ↳ Checking Block {i+1}: {block['size']}KB ({block['status']})")
        if block['status'] == 'Free' and block['size'] >= process_size:
            if block['size'] > worst_size:
                worst_size = block['size']
                worst_idx = i
                log.append(f"    → Candidate found (largest so far: {block['size']}KB)")
    
    if worst_idx != -1:
        internal_frag = memory_blocks[worst_idx]['size'] - process_size
        memory_blocks[worst_idx]['status'] = 'Allocated'
        memory_blocks[worst_idx]['process'] = process_name
        memory_blocks[worst_idx]['allocated_size'] = process_size
        memory_blocks[worst_idx]['internal_frag'] = internal_frag
        
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS: Worst fit is Block {worst_idx+1} ({worst_size}KB)")
        log.append(f"  ↳ Internal Fragmentation: {internal_frag}KB")
        return True, memory_blocks, log, worst_idx+1, internal_frag
    
    log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FAILED: No suitable block found for {process_name}")
    return False, memory_blocks, log, -1, 0


# Initialize session state
if 'memory_blocks' not in st.session_state:
    st.session_state.memory_blocks = [
        {'id': 1, 'size': 100, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 2, 'size': 500, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 3, 'size': 200, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 4, 'size': 300, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        {'id': 5, 'size': 600, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
    ]

if 'allocation_log' not in st.session_state:
    st.session_state.allocation_log = [
        f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM: Memory Management initialized",
        f"[{datetime.now().strftime('%H:%M:%S')}] CONFIG: Total memory blocks: 5, Total size: 1700KB"
    ]

if 'process_counter' not in st.session_state:
    st.session_state.process_counter = 1

# SIDEBAR
with st.sidebar:
    st.markdown("**OS SIMULATOR**")
    st.caption("v2.0 | Memory Management")
    st.divider()
    
    st.markdown("**MODULES**")
    modules = ["Process Management", "Memory Management", "File Systems", "I/O Systems"]
    selected_module = st.radio("Select Module:", modules, index=1, label_visibility="collapsed")
    
    if selected_module == "Process Management":
        st.switch_page("pages/1_Process_Management.py")
    elif selected_module == "File Systems":
        st.switch_page("pages/3_File_Systems.py")
    elif selected_module == "I/O Systems":
        st.switch_page("pages/4_IO_Systems.py")
    
    st.divider()
    
    st.markdown("**ALLOCATION ALGORITHM**")
    algorithm = st.selectbox(
        "Select Algorithm:",
        ["First Fit", "Best Fit", "Worst Fit"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("**ALLOCATE MEMORY**")
    with st.form("allocate_form"):
        process_name = st.text_input("Process Name", value=f"P{st.session_state.process_counter}")
        process_size = st.number_input("Size (KB)", value=100, min_value=1, max_value=1000)
        allocate_btn = st.form_submit_button("Allocate", use_container_width=True)
    
    st.divider()
    
    st.markdown("**DEALLOCATE MEMORY**")
    allocated_processes = [b['process'] for b in st.session_state.memory_blocks if b['status'] == 'Allocated']
    if allocated_processes:
        process_to_free = st.selectbox("Select Process:", allocated_processes)
        if st.button("Deallocate", use_container_width=True):
            for block in st.session_state.memory_blocks:
                if block['process'] == process_to_free:
                    block['status'] = 'Free'
                    block['process'] = None
                    block['allocated_size'] = 0
                    block['internal_frag'] = 0
                    st.session_state.allocation_log.insert(0, 
                        f"[{datetime.now().strftime('%H:%M:%S')}] DEALLOC: {process_to_free} freed from Block {block['id']}")
            st.rerun()
    else:
        st.info("No allocated processes")
    
    st.divider()
    
    st.markdown("**MEMORY BLOCKS**")
    with st.form("add_block_form"):
        new_block_size = st.number_input("Block Size (KB)", value=200, min_value=50, max_value=1000)
        if st.form_submit_button("Add Block", use_container_width=True):
            new_id = max(b['id'] for b in st.session_state.memory_blocks) + 1
            st.session_state.memory_blocks.append({
                'id': new_id, 'size': new_block_size, 'status': 'Free', 
                'process': None, 'allocated_size': 0, 'internal_frag': 0
            })
            st.session_state.allocation_log.insert(0, 
                f"[{datetime.now().strftime('%H:%M:%S')}] BLOCK_ADD: New block {new_id} added ({new_block_size}KB)")
            st.rerun()
    
    st.divider()
    
    if st.button("Reset Memory", use_container_width=True, type="primary"):
        st.session_state.memory_blocks = [
            {'id': 1, 'size': 100, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
            {'id': 2, 'size': 500, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
            {'id': 3, 'size': 200, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
            {'id': 4, 'size': 300, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
            {'id': 5, 'size': 600, 'status': 'Free', 'process': None, 'allocated_size': 0, 'internal_frag': 0},
        ]
        st.session_state.allocation_log = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM: Memory reset"]
        st.session_state.process_counter = 1
        st.rerun()

# Handle allocation
if allocate_btn:
    if algorithm == "First Fit":
        success, updated_blocks, log, block_num, frag = first_fit(
            copy.deepcopy(st.session_state.memory_blocks), process_size, process_name)
    elif algorithm == "Best Fit":
        success, updated_blocks, log, block_num, frag = best_fit(
            copy.deepcopy(st.session_state.memory_blocks), process_size, process_name)
    else:
        success, updated_blocks, log, block_num, frag = worst_fit(
            copy.deepcopy(st.session_state.memory_blocks), process_size, process_name)
    
    if success:
        st.session_state.memory_blocks = updated_blocks
        st.session_state.process_counter += 1
        st.toast(f"✅ {process_name} allocated to Block {block_num}")
    else:
        st.toast(f"❌ Failed to allocate {process_name}")
    
    st.session_state.allocation_log = log + st.session_state.allocation_log
    st.rerun()

# MAIN CONTENT
st.markdown("## Memory Management")
st.caption("Simulate memory allocation algorithms with fragmentation analysis and block visualization.")

st.divider()

# Main Layout
col_map, col_table, col_metrics = st.columns([1, 1.5, 1], gap="large")

# Memory Map Visualization
with col_map:
    st.markdown("### RAM Map")
    with st.container(border=True):
        total_size = sum(b['size'] for b in st.session_state.memory_blocks)
        
        for block in st.session_state.memory_blocks:
            height = max(40, int((block['size'] / total_size) * 400))
            
            if block['status'] == 'Allocated':
                color = '#3b82f6'
                label = f"{block['process']}<br>{block['allocated_size']}KB"
                if block['internal_frag'] > 0:
                    # Show internal fragmentation
                    alloc_height = int(height * (block['allocated_size'] / block['size']))
                    frag_height = height - alloc_height
                    st.markdown(f"""
                    <div style="background-color: {color}; height: {alloc_height}px; border-radius: 4px 4px 0 0; 
                                display: flex; align-items: center; justify-content: center; color: white; 
                                font-size: 11px; font-weight: bold; margin: 0;">
                        {block['process']} ({block['allocated_size']}KB)
                    </div>
                    <div style="background-color: #ef4444; height: {frag_height}px; border-radius: 0 0 4px 4px;
                                background-image: repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(255,255,255,0.2) 5px, rgba(255,255,255,0.2) 10px);
                                display: flex; align-items: center; justify-content: center; color: white;
                                font-size: 9px; margin-bottom: 4px;">
                        Frag: {block['internal_frag']}KB
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: {color}; height: {height}px; border-radius: 4px;
                                display: flex; align-items: center; justify-content: center; color: white;
                                font-size: 11px; font-weight: bold; margin-bottom: 4px;">
                        {block['process']} ({block['size']}KB)
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #22c55e; height: {height}px; border-radius: 4px;
                            display: flex; align-items: center; justify-content: center; color: white;
                            font-size: 11px; font-weight: bold; margin-bottom: 4px;">
                    FREE ({block['size']}KB)
                </div>
                """, unsafe_allow_html=True)
        
        # Legend
        st.markdown("""
        <div style="display: flex; gap: 1rem; margin-top: 1rem; font-size: 10px;">
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="width: 12px; height: 12px; background-color: #3b82f6; border-radius: 2px;"></span> Allocated
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="width: 12px; height: 12px; background-color: #22c55e; border-radius: 2px;"></span> Free
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="width: 12px; height: 12px; background-color: #ef4444; border-radius: 2px;"></span> Fragment
            </div>
        </div>
        """, unsafe_allow_html=True)

# Memory Blocks Table
with col_table:
    st.markdown("### Memory Blocks")
    
    table_data = []
    for block in st.session_state.memory_blocks:
        table_data.append({
            'Block': f"Block {block['id']}",
            'Size (KB)': block['size'],
            'Status': block['status'],
            'Process': block['process'] if block['process'] else '-',
            'Allocated': block['allocated_size'] if block['allocated_size'] > 0 else '-',
            'Int. Frag': block['internal_frag'] if block['internal_frag'] > 0 else '-'
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # External Fragmentation Info
    free_blocks = [b for b in st.session_state.memory_blocks if b['status'] == 'Free']
    total_free = sum(b['size'] for b in free_blocks)
    largest_free = max((b['size'] for b in free_blocks), default=0)
    
    st.markdown("### Fragmentation Analysis")
    frag_col1, frag_col2 = st.columns(2)
    with frag_col1:
        st.metric("Total Free Memory", f"{total_free} KB")
        st.metric("# Free Blocks", len(free_blocks))
    with frag_col2:
        st.metric("Largest Free Block", f"{largest_free} KB")
        internal_frag = sum(b['internal_frag'] for b in st.session_state.memory_blocks if b['internal_frag'] > 0)
        st.metric("Total Internal Frag", f"{internal_frag} KB")

# Metrics Panel
with col_metrics:
    st.markdown("### METRICS")
    
    total_memory = sum(b['size'] for b in st.session_state.memory_blocks)
    allocated_memory = sum(b['allocated_size'] for b in st.session_state.memory_blocks if b['status'] == 'Allocated')
    free_memory = total_memory - allocated_memory
    internal_frag = sum(b['internal_frag'] for b in st.session_state.memory_blocks)
    utilization = (allocated_memory / total_memory) * 100 if total_memory > 0 else 0
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{utilization:.1f}%</div>
        <div class="metric-label">Memory Utilization</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #ef4444;">{internal_frag}</div>
        <div class="metric-label">Internal Frag (KB)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_memory}</div>
        <div class="metric-label">Total Memory (KB)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #22c55e;">{free_memory}</div>
        <div class="metric-label">Free Memory (KB)</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Allocation Log
st.markdown("### Allocation Log")
with st.container(border=True):
    log_text = "\n".join(st.session_state.allocation_log[:20])
    st.code(log_text, language="text")

st.divider()
st.caption("OS Simulator v2.0 | Memory Management Module")
