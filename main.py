import streamlit as st

# Page configuration
st.set_page_config(
    page_title="OS Simulator - Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling (Global)
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
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    
    .stat-value { font-size: 2rem; font-weight: 700; color: var(--primary); }
    .stat-label { font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .tag {
        display: inline-block;
        background-color: #f1f5f9;
        color: var(--secondary);
        font-size: 0.75rem;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 6px;
        margin-right: 5px;
        margin-bottom: 5px;
        border: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR (Minimalist)
with st.sidebar:
    st.title("OS Simulator")
    st.caption("Version 2.0 | Educational Platform")
    st.divider()
    st.info("Select a module from the dashboard to begin your simulation.")

# HEADER
st.markdown("""
<div class="main-header">
    <h1>Operating System Simulator</h1>
    <p>An interactive workspace for visualizing core OS concepts and algorithms.</p>
</div>
""", unsafe_allow_html=True)

# STATISTICS
col1, col2, col3, col4 = st.columns(4)
stats = [("4", "Modules"), ("14", "Algorithms"), ("100%", "Interactive"), ("Live", "Visualization")]
for col, (val, lab) in zip([col1, col2, col3, col4], stats):
    col.markdown(f'<div class="stat-card"><div class="stat-value">{val}</div><div class="stat-label">{lab}</div></div>', unsafe_allow_html=True)

st.divider()

# MODULE SELECTION GRID
st.markdown("### Simulation Modules")
m_col1, m_col2 = st.columns(2, gap="large")

modules = [
    {
        "name": "Process Management",
        "desc": "Simulate CPU scheduling algorithms and visualize execution through Gantt charts.",
        "path": "pages/1_Process_Management.py",
        "tags": ["FCFS", "SJF", "Priority", "Round Robin"],
        "icon": "⚡"
    },
    {
        "name": "Memory Management",
        "desc": "Explore memory allocation strategies, RAM utilization, and fragmentation analysis.",
        "path": "pages/2_Memory_Management.py",
        "tags": ["First Fit", "Best Fit", "Worst Fit", "Compaction"],
        "icon": "🧠"
    },
    {
        "name": "File Systems",
        "desc": "Understand storage mechanisms using different allocation methods and directory trees.",
        "path": "pages/3_File_Systems.py",
        "tags": ["Contiguous", "Linked", "Indexed"],
        "icon": "📁"
    },
    {
        "name": "I/O Systems",
        "desc": "Learn disk scheduling algorithms and analyze seek time optimization metrics.",
        "path": "pages/4_IO_Systems.py",
        "tags": ["SSTF", "SCAN", "C-SCAN", "LOOK"],
        "icon": "💿"
    }
]

for i, mod in enumerate(modules):
    target_col = m_col1 if i % 2 == 0 else m_col2
    with target_col:
        with st.container(border=True):
            st.subheader(f"{mod['icon']} {mod['name']}")
            st.write(mod['desc'])
            tag_html = "".join([f'<span class="tag">{t}</span>' for t in mod['tags']])
            st.markdown(tag_html, unsafe_allow_html=True)
            if st.button(f"Launch {mod['name']}", key=f"nav_{i}", use_container_width=True, type="primary"):
                st.switch_page(mod['path'])

st.divider()
st.caption("Developed as an Educational Platform for Operating System Concepts.")