# 🖥️ OS Scheduler Visualization Tool

An interactive **Operating System CPU Scheduling Simulator** built using **Streamlit**, **Pandas**, and **Plotly**.  
This application allows users to visualize and compare different CPU scheduling algorithms using a **Gantt chart** representation.

---

## ✨ Features

- 📊 **Visual Gantt Chart** for CPU scheduling
- 🧮 Supports multiple scheduling algorithms:
  - First-Come, First-Serve (FCFS)
  - Shortest Job First (SJF)
  - Priority Scheduling (Non-preemptive)
  - Round Robin (RR)
  - Multilevel Queue Scheduling
- ⏱️ Adjustable **Time Quantum** for RR and Multilevel Queue
- ➕ Add custom processes dynamically
- 🗑️ Reset process queue instantly
- 📈 Displays:
  - Total Execution Time
  - CPU Utilization
- 🎨 Minimal **Black & White UI theme**
- 🚀 Fully interactive and real-time updates

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** – UI framework
- **Pandas** – Data handling
- **Plotly Express** – Gantt chart visualization
- **Datetime** – Time simulation

---

## 📥 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/os-scheduler-streamlit.git
cd os-scheduler-streamlit
