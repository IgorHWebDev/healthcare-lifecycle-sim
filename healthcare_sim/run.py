import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st

# Import from the package
from healthcare_sim.simulation_manager import SimulationManager
from healthcare_sim.lifecycle.lifecycle_manager import LifecycleStage

def initialize_session_state():
    """Initialize session state variables"""
    if 'simulation' not in st.session_state:
        st.session_state.simulation = SimulationManager()
    if 'events' not in st.session_state:
        st.session_state.events = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'is_paused' not in st.session_state:
        st.session_state.is_paused = False
    if 'simulation_speed' not in st.session_state:
        st.session_state.simulation_speed = 1.0
    if 'time_scale' not in st.session_state:
        st.session_state.time_scale = "seconds"
    if 'auto_events' not in st.session_state:
        st.session_state.auto_events = True
    if 'risk_level' not in st.session_state:
        st.session_state.risk_level = "normal"
    if 'terminal_messages' not in st.session_state:
        st.session_state.terminal_messages = []

def add_terminal_message(message: str, category: str = "INFO"):
    """Add a message to the terminal log"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    color_map = {
        "INFO": "white",
        "EVENT": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "PATIENT": "cyan",
        "STAFF": "magenta",
        "DEPT": "blue"
    }
    color = color_map.get(category, "white")
    formatted_msg = f"[{timestamp}] [{category}] {message}"
    st.session_state.terminal_messages.append((formatted_msg, color))
    if len(st.session_state.terminal_messages) > 100:
        st.session_state.terminal_messages = st.session_state.terminal_messages[-100:]

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))

def main():
    st.set_page_config(
        page_title="Healthcare Simulation",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("Healthcare Lifecycle Simulation")
    
    # Initialize session state
    initialize_session_state()
    
    # Create two columns: controls and live view
    control_col, view_col = st.columns([1, 2])
    
    with control_col:
        st.header("Simulation Controls")
        
        # Time controls
        st.subheader("⏱️ Time Settings")
        st.session_state.simulation_speed = st.slider(
            "Simulation Speed",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.simulation_speed,
            step=0.1,
            help="Speed multiplier for simulation time"
        )
        
        st.session_state.time_scale = st.selectbox(
            "Time Scale",
            options=["seconds", "minutes", "hours", "days"],
            index=["seconds", "minutes", "hours", "days"].index(st.session_state.time_scale),
            help="Unit of time for simulation updates"
        )
        
        # Event generation
        st.subheader("🎲 Event Generation")
        st.session_state.auto_events = st.checkbox(
            "Auto-generate Events",
            value=st.session_state.auto_events,
            help="Automatically generate lifecycle events"
        )
        
        st.session_state.risk_level = st.select_slider(
            "Risk Level",
            options=["low", "normal", "high"],
            value=st.session_state.risk_level,
            help="Probability of complications and emergencies"
        )
        
        # Department settings
        st.subheader("🏥 Department Settings")
        departments = st.session_state.simulation.get_department_stats()
        for dept in departments:
            with st.expander(f"📍 {dept['name']} Settings"):
                capacity = st.number_input(
                    f"👥 Capacity",
                    min_value=1,
                    max_value=50,
                    value=dept['capacity'],
                    key=f"capacity_{dept['department_id']}"
                )
                staff = st.number_input(
                    f"👨‍⚕️ Staff",
                    min_value=1,
                    max_value=20,
                    value=10,  # Default staff value
                    key=f"staff_{dept['department_id']}"
                )
    
    with view_col:
        st.header("Live Simulation View")
        
        # Terminal window
        st.markdown("### 🖥️ System Log Terminal")
        terminal_container = st.empty()
        
        def update_terminal():
            # Format terminal messages with colors
            terminal_text = ""
            for msg, color in st.session_state.terminal_messages[-50:]:  # Show last 50 messages
                terminal_text += f"<pre style='color: {color};'>{msg}</pre>"
            
            terminal_container.markdown(
                f"""
                <div style="
                    background-color: black;
                    padding: 10px;
                    border-radius: 5px;
                    height: 400px;
                    overflow-y: scroll;
                    font-family: 'Courier New', monospace;
                    margin-bottom: 20px;
                ">
                    {terminal_text}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Update terminal initially
        update_terminal()
        
        # Main simulation controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Start" if not st.session_state.is_running else "⏹️ Stop"):
                st.session_state.is_running = not st.session_state.is_running
                if st.session_state.is_running:
                    add_terminal_message("Simulation started - Initializing systems...", "EVENT")
                else:
                    add_terminal_message("Simulation stopped", "WARNING")
                update_terminal()
        
        with col2:
            if st.session_state.is_running:
                if st.button("⏸️ Pause" if not st.session_state.is_paused else "▶️ Resume"):
                    st.session_state.is_paused = not st.session_state.is_paused
                    if st.session_state.is_paused:
                        add_terminal_message("Simulation paused", "WARNING")
                    else:
                        add_terminal_message("Simulation resumed", "EVENT")
                    update_terminal()
        
        with col3:
            if st.button("🔄 Reset"):
                st.session_state.simulation = SimulationManager()
                st.session_state.events = []
                st.session_state.start_time = datetime.now()
                st.session_state.is_running = False
                st.session_state.is_paused = False
                st.session_state.terminal_messages = []
                add_terminal_message("System reset - All data cleared", "WARNING")
                update_terminal()
        
        # Department status
        st.subheader("Department Status")
        dept_cols = st.columns(len(departments))
        for i, dept in enumerate(departments):
            with dept_cols[i]:
                st.markdown(f"**{dept['name']}**")
                occupancy_rate = dept['current_occupancy'] / dept['capacity']
                occupancy_percentage = occupancy_rate * 100
                st.metric("Occupancy", f"{occupancy_percentage:.1f}%")
                st.metric("Patients", f"{dept['current_occupancy']}/{dept['capacity']}")
                st.progress(clamp(occupancy_rate))
        
        # Patient list
        st.subheader("Active Patients")
        show_all = st.button("👥 Toggle All Patient Data")
        if 'show_all_patients' not in st.session_state:
            st.session_state.show_all_patients = False
        if show_all:
            st.session_state.show_all_patients = not st.session_state.show_all_patients
            
        active_patients = st.session_state.simulation.get_active_patients()
        for patient in active_patients:
            if st.session_state.show_all_patients:
                details = st.session_state.simulation.get_patient_details(patient['patient_id'])
                if details:
                    st.markdown(f"""
                    ### 👤 Patient {patient['patient_id']} - {patient['status']}
                    - **Gender:** {details['gender']}
                    - **Age:** {details['age']}
                    - **Blood Type:** {details['blood_type']}
                    - **Department:** {details['current_department']}
                    """)
                    
                    if details['current_vitals']:
                        cols = st.columns(5)
                        with cols[0]:
                            st.metric("Heart Rate", f"{details['current_vitals']['heart_rate']} bpm")
                        with cols[1]:
                            st.metric("Blood Pressure", details['current_vitals']['blood_pressure'])
                        with cols[2]:
                            st.metric("Temperature", f"{details['current_vitals']['temperature']}°C")
                        with cols[3]:
                            st.metric("O2 Sat", f"{details['current_vitals']['oxygen_saturation']}%")
                        with cols[4]:
                            st.metric("Resp Rate", f"{details['current_vitals']['respiratory_rate']}/min")
                    st.markdown("---")
            else:
                with st.expander(f"👤 Patient {patient['patient_id']} - {patient['status']}"):
                    details = st.session_state.simulation.get_patient_details(patient['patient_id'])
                    if details:
                        st.write(f"**Gender:** {details['gender']}")
                        st.write(f"**Age:** {details['age']}")
                        st.write(f"**Blood Type:** {details['blood_type']}")
                        st.write(f"**Department:** {details['current_department']}")
                        
                        if details['current_vitals']:
                            st.write("**Current Vitals:**")
                            cols = st.columns(5)
                            with cols[0]:
                                st.metric("Heart Rate", f"{details['current_vitals']['heart_rate']} bpm")
                            with cols[1]:
                                st.metric("Blood Pressure", details['current_vitals']['blood_pressure'])
                            with cols[2]:
                                st.metric("Temperature", f"{details['current_vitals']['temperature']}°C")
                            with cols[3]:
                                st.metric("O2 Sat", f"{details['current_vitals']['oxygen_saturation']}%")
                            with cols[4]:
                                st.metric("Resp Rate", f"{details['current_vitals']['respiratory_rate']}/min")
        
        # Update simulation if running
        if st.session_state.is_running and not st.session_state.is_paused:
            try:
                # Calculate time delta based on settings
                if st.session_state.time_scale == "seconds":
                    delta = timedelta(seconds=1 * st.session_state.simulation_speed)
                elif st.session_state.time_scale == "minutes":
                    delta = timedelta(minutes=1 * st.session_state.simulation_speed)
                elif st.session_state.time_scale == "hours":
                    delta = timedelta(hours=1 * st.session_state.simulation_speed)
                else:  # days
                    delta = timedelta(days=1 * st.session_state.simulation_speed)
                
                # Update simulation with current parameters
                st.session_state.simulation.update(delta)  # Simplified update call
                
                # Log department changes
                departments = st.session_state.simulation.get_department_stats()
                for dept in departments:
                    message = (
                        f"Department: {dept['name']} | "
                        f"Patients: {dept['current_occupancy']}/{dept['capacity']} | "
                        f"Occupancy: {(dept['current_occupancy']/dept['capacity']*100):.1f}%"
                    )
                    add_terminal_message(message, "DEPT")
                
                # Log patient updates
                active_patients = st.session_state.simulation.get_active_patients()
                for patient in active_patients:
                    details = st.session_state.simulation.get_patient_details(patient['patient_id'])
                    if details:
                        message = (
                            f"Patient {patient['patient_id']} | "
                            f"Status: {patient['status']} | "
                            f"Department: {details['current_department']}"
                        )
                        add_terminal_message(message, "PATIENT")
                
                # Update terminal display
                update_terminal()
                
            except Exception as e:
                add_terminal_message(f"Error: {str(e)}", "ERROR")
                update_terminal()
                st.session_state.is_running = False

if __name__ == "__main__":
    main()
