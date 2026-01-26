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

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --file-blue: #3b82f6;
        --file-green: #10b981;
        --index-block: #ef4444;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    .tree-item {
        padding: 4px 8px;
        margin: 2px 0;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .tree-item:hover {
        background-color: rgba(37, 99, 235, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'disk_size' not in st.session_state:
    st.session_state.disk_size = 64  # Total blocks

if 'block_size' not in st.session_state:
    st.session_state.block_size = 4  # KB per block

if 'files' not in st.session_state:
    st.session_state.files = {
        'document.txt': {
            'type': 'Text File',
            'size': 12,  # KB
            'blocks': 3,
            'created': '2024-01-15 10:30:00',
            'allocation': 'indexed',
            'index_block': 5,
            'data_blocks': [12, 13, 14],
            'color': '#3b82f6'
        },
        'image.png': {
            'type': 'Image File',
            'size': 20,  # KB
            'blocks': 5,
            'created': '2024-01-15 11:45:00',
            'allocation': 'indexed',
            'index_block': 20,
            'data_blocks': [21, 22, 23, 24, 25],
            'color': '#10b981'
        },
        'report.pdf': {
            'type': 'PDF File',
            'size': 8,  # KB
            'blocks': 2,
            'created': '2024-01-15 14:20:00',
            'allocation': 'indexed',
            'index_block': 40,
            'data_blocks': [41, 42],
            'color': '#f59e0b'
        }
    }

if 'directories' not in st.session_state:
    st.session_state.directories = {
        'Root': {
            'Documents': ['document.txt', 'report.pdf'],
            'Images': ['image.png'],
            'System': []
        }
    }

if 'selected_file' not in st.session_state:
    st.session_state.selected_file = 'document.txt'

if 'file_log' not in st.session_state:
    st.session_state.file_log = [
        f"[{datetime.now().strftime('%H:%M:%S')}] FS_INIT: File system initialized (64 blocks, 4KB/block)",
        f"[{datetime.now().strftime('%H:%M:%S')}] DIR_CREATE: Root directory structure created",
    ]

if 'allocation_method' not in st.session_state:
    st.session_state.allocation_method = "Indexed Allocation"

def get_used_blocks():
    """Get all used block numbers"""
    used = set()
    for file_data in st.session_state.files.values():
        used.add(file_data['index_block'])
        used.update(file_data['data_blocks'])
    return used

def get_free_blocks(count):
    """Get n free blocks"""
    used = get_used_blocks()
    free = []
    for i in range(st.session_state.disk_size):
        if i not in used:
            free.append(i)
            if len(free) >= count:
                break
    return free

def allocate_file_contiguous(name, size_kb, file_type, directory):
    """Contiguous allocation"""
    blocks_needed = (size_kb + st.session_state.block_size - 1) // st.session_state.block_size
    used = get_used_blocks()
    
    # Find contiguous free space
    start_block = -1
    consecutive = 0
    
    for i in range(st.session_state.disk_size):
        if i not in used:
            if consecutive == 0:
                start_block = i
            consecutive += 1
            if consecutive >= blocks_needed:
                break
        else:
            consecutive = 0
            start_block = -1
    
    if consecutive >= blocks_needed:
        data_blocks = list(range(start_block, start_block + blocks_needed))
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        st.session_state.files[name] = {
            'type': file_type,
            'size': size_kb,
            'blocks': blocks_needed,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'allocation': 'contiguous',
            'index_block': start_block,
            'data_blocks': data_blocks,
            'color': random.choice(colors)
        }
        
        # Add to directory
        if directory in st.session_state.directories['Root']:
            st.session_state.directories['Root'][directory].append(name)
        
        st.session_state.file_log.insert(0, 
            f"[{datetime.now().strftime('%H:%M:%S')}] FILE_CREATE: {name} created ({size_kb}KB, {blocks_needed} blocks)")
        st.session_state.file_log.insert(0,
            f"[{datetime.now().strftime('%H:%M:%S')}] ALLOC_CONTIG: Blocks {start_block}-{start_block+blocks_needed-1} allocated")
        return True
    return False

def allocate_file_linked(name, size_kb, file_type, directory):
    """Linked allocation"""
    blocks_needed = (size_kb + st.session_state.block_size - 1) // st.session_state.block_size
    free_blocks = get_free_blocks(blocks_needed)
    
    if len(free_blocks) >= blocks_needed:
        data_blocks = free_blocks[:blocks_needed]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        st.session_state.files[name] = {
            'type': file_type,
            'size': size_kb,
            'blocks': blocks_needed,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'allocation': 'linked',
            'index_block': data_blocks[0],  # First block acts as start
            'data_blocks': data_blocks,
            'color': random.choice(colors)
        }
        
        if directory in st.session_state.directories['Root']:
            st.session_state.directories['Root'][directory].append(name)
        
        st.session_state.file_log.insert(0, 
            f"[{datetime.now().strftime('%H:%M:%S')}] FILE_CREATE: {name} created ({size_kb}KB, {blocks_needed} blocks)")
        st.session_state.file_log.insert(0,
            f"[{datetime.now().strftime('%H:%M:%S')}] ALLOC_LINKED: Blocks linked: {' -> '.join(map(str, data_blocks))}")
        return True
    return False

def allocate_file_indexed(name, size_kb, file_type, directory):
    """Indexed allocation"""
    blocks_needed = (size_kb + st.session_state.block_size - 1) // st.session_state.block_size
    free_blocks = get_free_blocks(blocks_needed + 1)  # +1 for index block
    
    if len(free_blocks) >= blocks_needed + 1:
        index_block = free_blocks[0]
        data_blocks = free_blocks[1:blocks_needed + 1]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
        
        st.session_state.files[name] = {
            'type': file_type,
            'size': size_kb,
            'blocks': blocks_needed,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'allocation': 'indexed',
            'index_block': index_block,
            'data_blocks': data_blocks,
            'color': random.choice(colors)
        }
        
        if directory in st.session_state.directories['Root']:
            st.session_state.directories['Root'][directory].append(name)
        
        st.session_state.file_log.insert(0, 
            f"[{datetime.now().strftime('%H:%M:%S')}] FILE_CREATE: {name} created ({size_kb}KB, {blocks_needed} blocks)")
        st.session_state.file_log.insert(0,
            f"[{datetime.now().strftime('%H:%M:%S')}] ALLOC_INDEX: Index block {index_block} -> Data blocks {data_blocks}")
        return True
    return False

def delete_file(name):
    """Delete a file and free its blocks"""
    if name in st.session_state.files:
        file_data = st.session_state.files[name]
        del st.session_state.files[name]
        
        # Remove from directories
        for dir_name, files in st.session_state.directories['Root'].items():
            if name in files:
                files.remove(name)
        
        st.session_state.file_log.insert(0,
            f"[{datetime.now().strftime('%H:%M:%S')}] FILE_DELETE: {name} deleted, blocks freed: {[file_data['index_block']] + file_data['data_blocks']}")
        return True
    return False

# SIDEBAR
with st.sidebar:
    st.markdown("**OS SIMULATOR**")
    st.caption("v2.0 | File Systems")
    st.divider()
    
    st.markdown("**MODULES**")
    modules = ["Process Management", "Memory Management", "File Systems", "I/O Systems"]
    selected_module = st.radio("Select Module:", modules, index=2, label_visibility="collapsed")
    
    if selected_module == "Process Management":
        st.switch_page("pages/1_Process_Management.py")
    elif selected_module == "Memory Management":
        st.switch_page("pages/2_Memory_Management.py")
    elif selected_module == "I/O Systems":
        st.switch_page("pages/4_IO_Systems.py")
    
    st.divider()
    
    st.markdown("**ALLOCATION METHOD**")
    allocation_method = st.selectbox(
        "Select Method:",
        ["Contiguous Allocation", "Linked Allocation", "Indexed Allocation"],
        index=2,
        label_visibility="collapsed"
    )
    st.session_state.allocation_method = allocation_method
    
    st.divider()
    
    st.markdown("**CREATE FILE**")
    with st.form("create_file_form"):
        new_file_name = st.text_input("File Name", value="newfile.txt")
        new_file_size = st.number_input("Size (KB)", value=8, min_value=1, max_value=100)
        new_file_type = st.selectbox("Type", ["Text File", "PDF File", "Image File", "Binary File"])
        new_file_dir = st.selectbox("Directory", list(st.session_state.directories['Root'].keys()))
        
        if st.form_submit_button("Create File", use_container_width=True):
            if new_file_name in st.session_state.files:
                st.error("File already exists!")
            else:
                if allocation_method == "Contiguous Allocation":
                    success = allocate_file_contiguous(new_file_name, new_file_size, new_file_type, new_file_dir)
                elif allocation_method == "Linked Allocation":
                    success = allocate_file_linked(new_file_name, new_file_size, new_file_type, new_file_dir)
                else:
                    success = allocate_file_indexed(new_file_name, new_file_size, new_file_type, new_file_dir)
                
                if success:
                    st.success(f"Created {new_file_name}")
                    st.rerun()
                else:
                    st.error("Not enough space!")
    
    st.divider()
    
    st.markdown("**DISK CAPACITY**")
    used_blocks = len(get_used_blocks())
    free_blocks = st.session_state.disk_size - used_blocks
    utilization = used_blocks / st.session_state.disk_size
    
    st.progress(utilization)
    st.caption(f"Used: {used_blocks} / Free: {free_blocks} / Total: {st.session_state.disk_size} blocks")
    
    st.divider()
    
    if st.button("Reset File System", use_container_width=True, type="primary"):
        st.session_state.files = {
            'document.txt': {
                'type': 'Text File', 'size': 12, 'blocks': 3,
                'created': '2024-01-15 10:30:00', 'allocation': 'indexed',
                'index_block': 5, 'data_blocks': [12, 13, 14], 'color': '#3b82f6'
            }
        }
        st.session_state.directories = {
            'Root': {'Documents': ['document.txt'], 'Images': [], 'System': []}
        }
        st.session_state.file_log = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM: File system reset"]
        st.rerun()

# MAIN CONTENT
st.markdown("## File Management: Directory & Allocation")
st.caption("Manage files with different allocation strategies. Visualize disk blocks and directory structure.")

st.divider()

# Main Layout
col_tree, col_attr, col_disk = st.columns([1, 1, 2], gap="large")

# Directory Tree
with col_tree:
    st.markdown("### Directory Tree")
    with st.container(border=True):
        st.markdown("**Root/**")
        
        for dir_name, files in st.session_state.directories['Root'].items():
            with st.expander(f"{dir_name}/", expanded=True):
                if files:
                    for file_name in files:
                        is_selected = file_name == st.session_state.selected_file
                        
                        if st.button(f"{file_name}", key=f"file_{file_name}", 
                                    use_container_width=True,
                                    type="primary" if is_selected else "secondary"):
                            st.session_state.selected_file = file_name
                            st.rerun()
                else:
                    st.caption("(empty)")
        
        st.divider()
        
        # File operations
        st.markdown("**Operations:**")
        op_col1, op_col2 = st.columns(2)
        with op_col1:
            if st.button("Delete", use_container_width=True):
                if st.session_state.selected_file:
                    delete_file(st.session_state.selected_file)
                    st.session_state.selected_file = list(st.session_state.files.keys())[0] if st.session_state.files else None
                    st.rerun()
        with op_col2:
            new_dir = st.text_input("New Dir:", label_visibility="collapsed", placeholder="New folder")
            if st.button("Create Dir", use_container_width=True):
                if new_dir and new_dir not in st.session_state.directories['Root']:
                    st.session_state.directories['Root'][new_dir] = []
                    st.session_state.file_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] DIR_CREATE: {new_dir}/ created")
                    st.rerun()

# File Attributes
with col_attr:
    st.markdown("### File Attributes")
    
    if st.session_state.selected_file and st.session_state.selected_file in st.session_state.files:
        file_data = st.session_state.files[st.session_state.selected_file]
        
        with st.container(border=True):
            st.markdown(f"**Name:** {st.session_state.selected_file}")
            st.markdown(f"**Size:** {file_data['size']} KB ({file_data['blocks']} blocks)")
            st.markdown(f"**Type:** {file_data['type']}")
            st.markdown(f"**Created:** {file_data['created']}")
            st.markdown(f"**Allocation:** {file_data['allocation'].title()}")
        
        st.markdown("### Block Mapping")
        with st.container(border=True):
            st.markdown(f"""
            <div style="background-color: #fef2f2; padding: 8px; border-radius: 4px; border: 1px solid #fecaca; margin-bottom: 8px;">
                <span style="color: #ef4444; font-weight: bold;">Index Block:</span> {file_data['index_block']}
            </div>
            """, unsafe_allow_html=True)
            
            for i, block in enumerate(file_data['data_blocks']):
                st.markdown(f"**Block {i}** → Disk Index **{block}**")
    else:
        st.info("Select a file to view attributes")

# Physical Disk Map
with col_disk:
    st.markdown("### Physical Disk Map")
    
    with st.container(border=True):
        # Legend using columns
        leg1, leg2, leg3 = st.columns(3)
        with leg1:
            st.markdown("[Blue] **Data**")
        with leg2:
            st.markdown("[Red] **Index**")
        with leg3:
            st.markdown("[Gray] **Free**")
        
        st.divider()
        
        # Build disk visualization
        used_blocks = get_used_blocks()
        
        # Create mapping of block to file
        block_to_file = {}
        block_is_index = {}
        for fname, fdata in st.session_state.files.items():
            block_to_file[fdata['index_block']] = fname
            block_is_index[fdata['index_block']] = True
            for db in fdata['data_blocks']:
                block_to_file[db] = fname
        
        # Display blocks in grid using Streamlit columns
        num_cols = 8
        rows = (st.session_state.disk_size + num_cols - 1) // num_cols
        
        for row in range(rows):
            cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                block_idx = row * num_cols + col_idx
                if block_idx < st.session_state.disk_size:
                    with cols[col_idx]:
                        if block_idx in block_to_file:
                            fname = block_to_file[block_idx]
                            if block_idx in block_is_index:
                                # Index block - red
                                st.button(f"{block_idx}", key=f"disk_{block_idx}", 
                                         help=f"{fname} Index", disabled=True,
                                         use_container_width=True)
                            else:
                                # Data block - blue
                                st.button(f"{block_idx}", key=f"disk_{block_idx}", 
                                         help=f"{fname} Data", disabled=True,
                                         use_container_width=True)
                        else:
                            # Free block - gray
                            st.caption(f"`{block_idx}`")
        
        # Allocation visualization for selected file
        if st.session_state.selected_file and st.session_state.selected_file in st.session_state.files:
            file_data = st.session_state.files[st.session_state.selected_file]
            st.divider()
            st.markdown(f"**{st.session_state.selected_file} Allocation:**")
            st.info(f"Index Block: **{file_data['index_block']}** → Data Blocks: **{', '.join(map(str, file_data['data_blocks']))}**")

st.divider()

# File Operation Log
st.markdown("### File Operation Log")
with st.container(border=True):
    log_text = "\n".join(st.session_state.file_log[:15])
    st.code(log_text, language="text")

st.divider()
st.caption("OS Simulator v2.0 | File Systems Module")
