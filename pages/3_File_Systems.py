import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="File Systems - OS Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --file-blue: #3b82f6;
        --file-green: #10b981;
        --index-block: #ef4444;
    }
    .block-grid {
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 5px;
        margin-top: 10px;
    }
    .disk-block {
        aspect-ratio: 1;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: white;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ============== FILE ALLOCATION LOGIC ==============

def get_used_blocks():
    used = set()
    for f in st.session_state.files.values():
        if f.get('index_block') is not None: used.add(f['index_block'])
        used.update(f['data_blocks'])
    return used

def allocate_file(name, size_kb, method, directory):
    block_size = 4
    blocks_needed = (size_kb + block_size - 1) // block_size
    used = get_used_blocks()
    total_blocks = 64
    
    # Simple check for space
    if len(used) + blocks_needed + (1 if method == "Indexed" else 0) > total_blocks:
        return False, "Not enough disk space"

    available = [i for i in range(total_blocks) if i not in used]
    
    if method == "Indexed":
        idx_block = available.pop(0)
        data_blocks = available[:blocks_needed]
        st.session_state.files[name] = {
            'size': size_kb, 'blocks': blocks_needed, 'allocation': 'Indexed',
            'index_block': idx_block, 'data_blocks': data_blocks, 'created': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    elif method == "Contiguous":
        # Simplified contiguous: find first fit
        start = -1
        for i in range(total_blocks - blocks_needed + 1):
            if all(j not in used for j in range(i, i + blocks_needed)):
                start = i
                break
        if start == -1: return False, "No contiguous space found"
        st.session_state.files[name] = {
            'size': size_kb, 'blocks': blocks_needed, 'allocation': 'Contiguous',
            'index_block': None, 'data_blocks': list(range(start, start + blocks_needed)), 
            'created': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    else: # Linked
        data_blocks = available[:blocks_needed]
        st.session_state.files[name] = {
            'size': size_kb, 'blocks': blocks_needed, 'allocation': 'Linked',
            'index_block': None, 'data_blocks': data_blocks, 'created': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    
    st.session_state.directories[directory].append(name)
    return True, "File created successfully"

# ============== SESSION STATE ==============
if 'files' not in st.session_state:
    st.session_state.files = {
        'readme.txt': {'size': 8, 'blocks': 2, 'allocation': 'Indexed', 'index_block': 5, 'data_blocks': [10, 11], 'created': '2026-01-26 10:00'}
    }
if 'directories' not in st.session_state:
    st.session_state.directories = {'Documents': ['readme.txt'], 'System': [], 'Pictures': []}
if 'selected_file' not in st.session_state: st.session_state.selected_file = 'readme.txt'

# ============== SIDEBAR ==============
with st.sidebar:
    st.title("OS Simulator")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("main.py")
    st.divider()
    st.caption("Module: File Systems")

# ============== MAIN UI ==============
st.title("📁 File Management & Disk Allocation")

# CONTROL CENTER
with st.container(border=True):
    st.subheader("🛠️ File System Control Center")
    c1, c2, c3 = st.columns([1.5, 2, 1], gap="medium")
    
    with c1:
        method = st.selectbox("Allocation Strategy", ["Indexed", "Contiguous", "Linked"])
    
    with c2:
        with st.popover("➕ Create New File", use_container_width=True):
            f_name = st.text_input("Filename", value="new_file.txt")
            f_size = st.number_input("Size (KB)", min_value=1, value=12)
            f_dir = st.selectbox("Target Directory", list(st.session_state.directories.keys()))
            if st.button("Commit to Disk", type="primary"):
                success, msg = allocate_file(f_name, f_size, method, f_dir)
                if success: st.toast(msg)
                else: st.error(msg)
                st.rerun()
                
    with c3:
        if st.button("🗑️ Wipe Disk", type="primary", use_container_width=True):
            st.session_state.files = {}
            st.session_state.directories = {k: [] for k in st.session_state.directories}
            st.rerun()

st.divider()

# VISUALIZATION
col_tree, col_attr, col_disk = st.columns([1, 1, 2], gap="large")

with col_tree:
    st.subheader("Directory Tree")
    for dir_name, files in st.session_state.directories.items():
        with st.expander(f"📂 {dir_name}", expanded=True):
            if not files: st.caption("Empty")
            for f in files:
                if st.button(f"📄 {f}", key=f"btn_{f}", use_container_width=True):
                    st.session_state.selected_file = f
                    st.rerun()

with col_attr:
    st.subheader("File Attributes")
    if st.session_state.selected_file in st.session_state.files:
        f = st.session_state.files[st.session_state.selected_file]
        with st.container(border=True):
            st.markdown(f"**Name:** {st.session_state.selected_file}")
            st.markdown(f"**Method:** {f['allocation']}")
            st.markdown(f"**Size:** {f['size']} KB")
            st.markdown(f"**Blocks:** {f['blocks']}")
            st.markdown(f"**Created:** {f['created']}")
            if f['index_block'] is not None:
                st.error(f"Index Block: {f['index_block']}")
            st.info(f"Data Blocks: {', '.join(map(str, f['data_blocks']))}")
            
            if st.button("Delete File", use_container_width=True):
                # Deletion logic
                name = st.session_state.selected_file
                del st.session_state.files[name]
                for d in st.session_state.directories:
                    if name in st.session_state.directories[d]: st.session_state.directories[d].remove(name)
                st.session_state.selected_file = None
                st.rerun()
    else:
        st.info("Select a file from the tree.")

with col_disk:
    st.subheader("Physical Disk Map (64 Blocks)")
    
    used_blocks = get_used_blocks()
    
    # Visual mapping
    cols = st.columns(8)
    for i in range(64):
        with cols[i % 8]:
            color = "#f3f4f6" # Free
            label = str(i)
            
            # Check if this block belongs to the selected file for highlighting
            sf = st.session_state.files.get(st.session_state.selected_file)
            if sf:
                if i == sf.get('index_block'): color = "#ef4444"
                elif i in sf['data_blocks']: color = "#3b82f6"
                elif i in used_blocks: color = "#9ca3af"
            elif i in used_blocks:
                color = "#9ca3af"
                
            st.markdown(f"""
                <div class="disk-block" style="background:{color};">
                    {label}
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown("""
        <div style="display:flex; gap:10px; margin-top:10px; font-size:12px;">
            <div><span style="color:#ef4444">■</span> Index</div>
            <div><span style="color:#3b82f6">■</span> Selected Data</div>
            <div><span style="color:#9ca3af">■</span> Other Files</div>
            <div><span style="color:#f3f4f6">■</span> Free</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("OS Simulator v2.0 | File Systems Module")