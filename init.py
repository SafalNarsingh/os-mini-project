import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="OS Scheduler", layout="wide")

st.markdown("""
    <style>
    /* 1. Compact Layout (No Scroll) */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; }
    
    /* 2. B&W Theme */
    :root { --primary-color: #000000; --background-color: #ffffff; --text-color: #000000; }
    @media (prefers-color-scheme: dark) {
        :root { --primary-color: #ffffff; --background-color: #0e1117; --text-color: #ffffff; }
    }
    
    /* 3. Compact Elements */
    .stButton > button { border: 2px solid var(--text-color); background: transparent; color: var(--text-color); width: 100%; height: 3em; }
    .stButton > button:hover { background: var(--text-color); color: var(--background-color); }
    header[data-testid="stHeader"], footer { display: none; }
    h1 { font-size: 1.8rem; margin: 0; }
    h3 { font-size: 1.2rem; margin: 0; }
    div[data-testid="stMetric"] { background-color: rgba(128,128,128,0.1); padding: 5px; border-radius: 5px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {'Task': 'P1', 'Arrival': 0, 'Burst': 5, 'Priority': 1},
        {'Task': 'P2', 'Arrival': 2, 'Burst': 3, 'Priority': 2},
        {'Task': 'P3', 'Arrival': 4, 'Burst': 1, 'Priority': 3}
    ]
if 'show_add_form' not in st.session_state: st.session_state.show_add_form = False

# --- 3. SCHEDULING ALGORITHMS (SIMULATION ENGINE) ---
def solve_scheduler(tasks, algo, quantum):
    queue = []
    for t in tasks:
        queue.append({**t, 'Remaining': t['Burst'], 'Original_Priority': t['Priority']})
    
    timeline = [] 
    time = 0
    completed = 0
    n = len(queue)
    rr_queue = [] 
    
    while completed < n:
        available = [t for t in queue if t['Arrival'] <= time and t['Remaining'] > 0]
        
        if not available:
            time += 1
            continue

        selected = None
        
        if algo == "First-Come, First-Serve (FCFS)":
            available.sort(key=lambda x: x['Arrival'])
            selected = available[0]
            run_time = selected['Remaining']
            
        elif algo == "Shortest Job First (SJF)":
            available.sort(key=lambda x: (x['Burst'], x['Arrival']))
            selected = available[0]
            run_time = selected['Remaining']
            
        elif algo == "Priority Scheduling":
            available.sort(key=lambda x: (x['Priority'], x['Arrival']))
            selected = available[0]
            run_time = selected['Remaining']
            
        elif algo == "Round Robin (RR)":
            for t in available:
                if t not in rr_queue:
                    rr_queue.append(t)
            
            if not rr_queue:
                time += 1
                continue
                
            selected = rr_queue.pop(0) 
            run_time = min(selected['Remaining'], quantum)
            
        elif algo == "Multilevel Queue":
            q1 = [t for t in available if t['Priority'] <= 2]
            q2 = [t for t in available if t['Priority'] > 2]
            
            if q1:
                q1.sort(key=lambda x: x['Arrival'])
                selected = q1[0]
                run_time = min(selected['Remaining'], quantum)
            elif q2:
                q2.sort(key=lambda x: x['Arrival'])
                selected = q2[0]
                run_time = selected['Remaining']
            else:
                time +=1
                continue

        if selected:
            start_time = time
            finish_time = time + run_time
            
            timeline.append({
                'Task': selected['Task'], 
                'Start': start_time, 
                'Finish': finish_time, 
                'Priority': selected['Original_Priority']
            })
            
            selected['Remaining'] -= run_time
            time += run_time
            
            if selected['Remaining'] == 0:
                completed += 1
            else:
                if algo == "Round Robin (RR)" or (algo == "Multilevel Queue" and selected['Original_Priority'] <= 2):
                    if algo == "Round Robin (RR)":
                        new_arrivals = [t for t in queue if t['Arrival'] > start_time and t['Arrival'] <= finish_time and t['Remaining'] > 0 and t not in rr_queue and t != selected]
                        rr_queue.extend(new_arrivals)
                        rr_queue.append(selected)

    df = pd.DataFrame(timeline)
    if not df.empty:
        base = datetime.today()
        df['Start_Date'] = df['Start'].apply(lambda x: base + timedelta(hours=x))
        df['Finish_Date'] = df['Finish'].apply(lambda x: base + timedelta(hours=x))
        df['Duration'] = df['Finish'] - df['Start']
    return df

# --- 4. TOP BAR (Adjusted for Side-by-Side Buttons) ---
# Columns: Title (3) | Metrics (4) | Actions (3)
c_title, c_metrics, c_actions = st.columns([3, 4, 3], gap="small")

with c_title:
    st.title("◾ OS Scheduler")

with c_metrics:
    if st.session_state.tasks:
        avg_burst = sum(t['Burst'] for t in st.session_state.tasks) / len(st.session_state.tasks)
        st.markdown(f"**Tasks:** {len(st.session_state.tasks)} | **Avg Burst:** {avg_burst:.1f}")
    else:
        st.write("Ready to schedule")

with c_actions:
    # Create two columns INSIDE the actions column to force buttons side-by-side
    b1, b2 = st.columns(2)
    with b1:
        if st.button("➕ Add"): 
            st.session_state.show_add_form = not st.session_state.show_add_form
    with b2:
        if st.button("🗑 Reset"): 
            st.session_state.tasks = []
            st.rerun()

st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

# --- 5. INPUT FORM ---
if st.session_state.show_add_form:
    with st.container():
        f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 1])
        with f1: name = st.text_input("Name", value=f"P{len(st.session_state.tasks)+1}")
        with f2: arr = st.number_input("Arr.", min_value=0, value=0)
        with f3: burst = st.number_input("Burst", min_value=1, value=1)
        with f4: prio = st.number_input("Prio", min_value=1, value=1, help="Lower # = Higher Priority")
        with f5: 
            st.write("")
            st.write("")
            if st.button("Save"):
                st.session_state.tasks.append({'Task': name, 'Arrival': arr, 'Burst': burst, 'Priority': prio})
                st.session_state.show_add_form = False
                st.rerun()
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

# --- 6. MAIN CONTENT ---
col_left, col_right = st.columns([1, 2.5], gap="medium")

with col_left:
    st.subheader("Configuration")
    
    algo_choice = st.selectbox(
        "Algorithm", 
        ["First-Come, First-Serve (FCFS)", "Shortest Job First (SJF)", "Priority Scheduling", "Round Robin (RR)", "Multilevel Queue"]
    )
    
    quantum = 2
    if algo_choice in ["Round Robin (RR)", "Multilevel Queue"]:
        quantum = st.number_input("Time Quantum", min_value=1, value=2)
        if algo_choice == "Multilevel Queue":
            st.caption("Q1 (Prio ≤ 2): RR | Q2 (Prio > 2): FCFS")
    
    st.markdown("---")
    st.subheader("Queue")
    if st.session_state.tasks:
        st.dataframe(pd.DataFrame(st.session_state.tasks), use_container_width=True, height=200, hide_index=True)

with col_right:
    st.subheader("Gantt Chart Visualization")
    
    if st.session_state.tasks:
        try:
            df_sched = solve_scheduler(st.session_state.tasks, algo_choice, quantum)
            
            if not df_sched.empty:
                finish_time = df_sched['Finish'].max()
                
                fig = px.timeline(
                    df_sched, x_start="Start_Date", x_end="Finish_Date", y="Task", color="Priority",
                    color_continuous_scale=['#111111', '#aaaaaa'],
                    hover_data={"Start":True, "Finish":True, "Start_Date":False, "Finish_Date":False}
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(title="Time Units", tickformat="%H:%M", showgrid=True, gridcolor='#eeeeee', linecolor='black'),
                    yaxis=dict(showgrid=False, linecolor='black', autorange="reversed"),
                    margin=dict(l=10, r=10, t=20, b=20),
                    height=350,
                    showlegend=False,
                    bargap=0.2
                )
                fig.update_traces(marker_line_color='black', marker_line_width=1)
                st.plotly_chart(fig, use_container_width=True)
                
                s1, s2 = st.columns(2)
                s1.info(f"Total Time: {finish_time} units")
                utilization = (sum(t['Burst'] for t in st.session_state.tasks) / finish_time) * 100
                s2.info(f"CPU Utilization: {utilization:.1f}%")
                
            else:
                st.warning("No tasks could be scheduled.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Add tasks to view the timeline.")