import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Operating System Simulator - Educational Platform v2.0"
    }
)

# Professional CSS styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #475569;
        --accent: #0891b2;
        --background: #f8fafc;
        --surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border: #e2e8f0;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 2rem 2.5rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 2rem;
        border-left: 4px solid var(--accent);
    }
    
    .main-header h1 {
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .main-header p {
        font-size: 0.95rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1.25rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    .module-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary);
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    .tag {
        display: inline-block;
        background-color: #f1f5f9;
        color: var(--secondary);
        font-size: 0.7rem;
        font-weight: 500;
        padding: 3px 8px;
        border-radius: 4px;
        margin: 2px;
        border: 1px solid var(--border);
    }
    
    .coverage-item {
        padding: 10px 14px;
        background-color: #f8fafc;
        border-left: 3px solid var(--primary);
        margin: 8px 0;
        border-radius: 0 4px 4px 0;
    }
    
    .coverage-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    
    .coverage-desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-title">OS Simulator</div>', unsafe_allow_html=True)
    st.caption("Version 2.0 | Educational Platform")
    st.divider()
    
    st.markdown("**MODULES**")
    st.markdown("""
    - Process Management
    - Memory Management
    - File Systems
    - I/O Systems
    """)
    
    st.divider()
    
    st.markdown("**ABOUT**")
    st.caption("An interactive educational tool for understanding Operating System concepts through visualization and simulation.")

# HEADER
st.markdown("""
<div class="main-header">
    <h1>Operating System Simulator</h1>
    <p>Interactive Educational Platform for OS Concepts</p>
</div>
""", unsafe_allow_html=True)

# STATISTICS
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">4</div>
        <div class="stat-label">Modules</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">14</div>
        <div class="stat-label">Algorithms</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">100%</div>
        <div class="stat-label">Interactive</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">Live</div>
        <div class="stat-label">Visualization</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# MODULE SELECTION
st.markdown("### Select Module")

module_cols = st.columns(2, gap="large")

with module_cols[0]:
    with st.container(border=True):
        st.markdown('<div class="module-header">Process Management</div>', unsafe_allow_html=True)
        st.caption("CPU Scheduling & Process States")
        st.markdown("""
        Simulate CPU scheduling algorithms and visualize process execution 
        through Gantt charts. Calculate waiting and turnaround times.
        """)
        
        st.markdown("""
        <span class="tag">FCFS</span>
        <span class="tag">SJF</span>
        <span class="tag">Priority</span>
        <span class="tag">Round Robin</span>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Open Module", use_container_width=True, type="primary", key="btn_process"):
            st.switch_page("pages/1_Process_Management.py")

with module_cols[1]:
    with st.container(border=True):
        st.markdown('<div class="module-header">Memory Management</div>', unsafe_allow_html=True)
        st.caption("Memory Allocation Strategies")
        st.markdown("""
        Explore memory allocation algorithms and visualize RAM utilization.
        Analyze fragmentation and memory efficiency.
        """)
        
        st.markdown("""
        <span class="tag">First Fit</span>
        <span class="tag">Best Fit</span>
        <span class="tag">Worst Fit</span>
        <span class="tag">Compaction</span>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Open Module", use_container_width=True, type="primary", key="btn_memory"):
            st.switch_page("pages/2_Memory_Management.py")

module_cols2 = st.columns(2, gap="large")

with module_cols2[0]:
    with st.container(border=True):
        st.markdown('<div class="module-header">File Systems</div>', unsafe_allow_html=True)
        st.caption("File Allocation & Directory Structure")
        st.markdown("""
        Understand file storage mechanisms using different allocation methods.
        Explore directory structures and disk block management.
        """)
        
        st.markdown("""
        <span class="tag">Contiguous</span>
        <span class="tag">Linked</span>
        <span class="tag">Indexed</span>
        <span class="tag">Directory Tree</span>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Open Module", use_container_width=True, type="primary", key="btn_file"):
            st.switch_page("pages/3_File_Systems.py")

with module_cols2[1]:
    with st.container(border=True):
        st.markdown('<div class="module-header">I/O Systems</div>', unsafe_allow_html=True)
        st.caption("Disk Scheduling & Seek Optimization")
        st.markdown("""
        Learn disk scheduling algorithms and seek time optimization.
        Visualize head movement and compare algorithm efficiency.
        """)
        
        st.markdown("""
        <span class="tag">FCFS</span>
        <span class="tag">SSTF</span>
        <span class="tag">SCAN</span>
        <span class="tag">C-SCAN</span>
        <span class="tag">LOOK</span>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Open Module", use_container_width=True, type="primary", key="btn_io"):
            st.switch_page("pages/4_IO_Systems.py")

st.divider()

# SYLLABUS COVERAGE
st.markdown("### Syllabus Coverage")

syllabus_cols = st.columns(2, gap="large")

with syllabus_cols[0]:
    st.markdown("**Process Management**")
    st.markdown("""
    <div class="coverage-item">
        <div class="coverage-title">Process Scheduling Algorithms</div>
        <div class="coverage-desc">FCFS, SJF, Priority, Round Robin</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Scheduling Metrics</div>
        <div class="coverage-desc">Waiting Time, Turnaround Time, Response Time</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Gantt Chart Visualization</div>
        <div class="coverage-desc">Visual timeline of process execution</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Memory Management**")
    st.markdown("""
    <div class="coverage-item">
        <div class="coverage-title">Memory Allocation Strategies</div>
        <div class="coverage-desc">First Fit, Best Fit, Worst Fit</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Memory Fragmentation</div>
        <div class="coverage-desc">Internal & External Fragmentation Analysis</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Memory Compaction</div>
        <div class="coverage-desc">Defragmentation and consolidation</div>
    </div>
    """, unsafe_allow_html=True)

with syllabus_cols[1]:
    st.markdown("**File Systems**")
    st.markdown("""
    <div class="coverage-item">
        <div class="coverage-title">File Allocation Methods</div>
        <div class="coverage-desc">Contiguous, Linked, Indexed</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Directory Structure</div>
        <div class="coverage-desc">Hierarchical directory tree</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Disk Block Management</div>
        <div class="coverage-desc">Block allocation and free space management</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**I/O Systems**")
    st.markdown("""
    <div class="coverage-item">
        <div class="coverage-title">Disk Scheduling Algorithms</div>
        <div class="coverage-desc">FCFS, SSTF, SCAN, LOOK, C-SCAN, C-LOOK</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Seek Time Optimization</div>
        <div class="coverage-desc">Total seek distance calculation</div>
    </div>
    <div class="coverage-item">
        <div class="coverage-title">Head Movement Visualization</div>
        <div class="coverage-desc">Graphical representation of disk arm movement</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# FOOTER
st.caption("OS Simulator v2.0 | Educational Platform | All algorithms implemented with working visualizations")
