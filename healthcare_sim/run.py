import os
import sys
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from datetime import datetime, timedelta

# Import from the package
from healthcare_sim.simulation_manager import SimulationManager
from healthcare_sim.lifecycle.lifecycle_manager import LifecycleStage
from healthcare_sim.visualization import (
    create_lifecycle_timeline,
    create_stage_distribution,
    create_genetic_timeline,
    display_lifecycle_dashboard,
    create_agent_path_visualization
)

def main():
    st.set_page_config(
        page_title="Healthcare Simulation",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("Healthcare Lifecycle Simulation")
    
    # Initialize simulation if needed
    if 'simulation' not in st.session_state:
        st.session_state.simulation = SimulationManager()
        st.session_state.events = []
        st.session_state.start_time = datetime.now()
        st.session_state.is_running = False
        st.session_state.is_paused = False
        st.session_state.agent_paths = {}
        st.session_state.simulation_speed = 1.0
        st.session_state.time_scale = "minutes"
        st.session_state.auto_events = True
        st.session_state.risk_level = "normal"
        st.session_state.selected_patient = None
    
    # Sidebar for simulation parameters
    with st.sidebar:
        st.header("Simulation Parameters")
        
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
        departments = st.session_state.simulation.get_facility_layout()["departments"]
        for dept_id, dept in departments.items():
            st.markdown(f"**{dept['name']}**")
            capacity = st.number_input(
                f"👥 {dept['name']} Capacity",
                min_value=1,
                max_value=50,
                value=dept['capacity'],
                key=f"capacity_{dept_id}"
            )
            staff = st.number_input(
                f"👨‍⚕️ {dept['name']} Staff",
                min_value=1,
                max_value=20,
                value=dept['staff'],
                key=f"staff_{dept_id}"
            )
    
    # Main simulation controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Simulation" if not st.session_state.is_running else "⏹️ Stop Simulation"):
            st.session_state.is_running = not st.session_state.is_running
            if st.session_state.is_running:
                st.success("🚀 Simulation started!")
            else:
                st.warning("🛑 Simulation stopped!")
    
    with col2:
        if st.session_state.is_running:
            if st.button("⏸️ Pause" if not st.session_state.is_paused else "▶️ Resume"):
                st.session_state.is_paused = not st.session_state.is_paused
                if st.session_state.is_paused:
                    st.info("⏸️ Simulation paused")
                else:
                    st.success("▶️ Simulation resumed")
    
    with col3:
        if st.button("🔄 Reset Simulation"):
            st.session_state.simulation = SimulationManager()
            st.session_state.events = []
            st.session_state.start_time = datetime.now()
            st.session_state.is_running = False
            st.session_state.is_paused = False
            st.session_state.agent_paths = {}
            st.success("🔄 Simulation reset!")
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "👥 Patients & Staff",
        "🏥 Facility Status",
        "📝 Event Log"
    ])
    
    with tab1:
        st.header("📊 Simulation Dashboard")
        
        # Status indicators
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            status = "🟢 Running" if st.session_state.is_running and not st.session_state.is_paused else \
                    "⏸️ Paused" if st.session_state.is_paused else \
                    "🔴 Stopped"
            st.metric("Status", status)
            st.metric("Current Time", st.session_state.simulation.current_time.strftime("%H:%M:%S"))
        
        with status_col2:
            st.metric("Simulation Speed", f"{st.session_state.simulation_speed}x")
            st.metric("Time Scale", st.session_state.time_scale)
        
        with status_col3:
            st.metric("Risk Level", st.session_state.risk_level.title())
            st.metric("Auto Events", "Enabled" if st.session_state.auto_events else "Disabled")
        
        # Timeline visualization
        if st.session_state.events:
            timeline = create_lifecycle_timeline(st.session_state.events)
            if timeline:
                st.plotly_chart(timeline, use_container_width=True)
            
            # Stage distribution
            distribution = create_stage_distribution(st.session_state.events)
            if distribution:
                st.plotly_chart(distribution, use_container_width=True)
    
    with tab2:
        st.header("👥 Patients & Staff")
        
        # Patient list
        st.subheader("🏥 Current Patients")
        patient_events = {}
        for patient_id, events in st.session_state.simulation.lifecycle_manager.lifecycle_events.items():
            if events:
                latest_event = max(events, key=lambda e: e.timestamp)
                patient_events[patient_id] = latest_event
        
        for patient_id, event in patient_events.items():
            with st.expander(f"👤 Patient {patient_id} - {event.stage.name}"):
                st.write(f"**Current Location:** {event.location}")
                st.write(f"**Healthcare Providers:** {', '.join(event.providers)}")
                if event.biometric_data:
                    st.write("**Biometric Data:**")
                    for key, value in event.biometric_data.items():
                        st.write(f"- {key}: {value}")
        
        # Staff status
        st.subheader("👨‍⚕️ Staff Status")
        departments = st.session_state.simulation.get_facility_layout()["departments"]
        for dept_id, dept in departments.items():
            with st.expander(f"🏥 {dept['name']} Staff"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Staff", dept['staff'])
                    st.write("**Equipment:**")
                    for item in dept['equipment']:
                        st.write(f"- 🔧 {item}")
                with col2:
                    st.metric("Current Patients", dept['current_patients'])
                    st.progress(dept['current_patients'] / dept['capacity'])
    
    with tab3:
        st.header("🏥 Facility Status")
        
        # Department layout
        facility = st.session_state.simulation.get_facility_layout()
        cols = st.columns(len(facility["departments"]))
        
        for i, (dept_id, dept) in enumerate(facility["departments"].items()):
            with cols[i]:
                st.subheader(f"🏥 {dept['name']}")
                st.metric("Capacity", f"{dept['current_patients']}/{dept['capacity']}")
                st.progress(dept['current_patients'] / dept['capacity'])
                
                st.write("**Locations:**")
                for loc in dept['locations']:
                    st.write(f"📍 {loc}")
                
                st.write("**Equipment:**")
                for equip in dept['equipment']:
                    st.write(f"🔧 {equip}")
        
        # Department connections
        st.subheader("🔄 Department Connections")
        for conn in facility["connections"]:
            st.write(f"🔄 {conn[0]} ↔️ {conn[1]}")
    
    with tab4:
        st.header("📝 Event Log")
        
        if st.session_state.events:
            for event in sorted(st.session_state.events, key=lambda e: e.timestamp, reverse=True):
                severity = "🔴" if "ALERT" in event.description else "🟢"
                with st.expander(f"{severity} {event.timestamp.strftime('%H:%M:%S')} - {event.stage.name}"):
                    st.write(f"**Description:** {event.description}")
                    st.write(f"**Location:** {event.location}")
                    st.write(f"**Providers:** {', '.join(event.providers)}")
                    
                    if event.biometric_data:
                        st.write("**Biometric Data:**")
                        for key, value in event.biometric_data.items():
                            st.write(f"- {key}: {value}")
                    
                    if event.genetic_data:
                        st.write("**Genetic Data:**")
                        for key, value in event.genetic_data.items():
                            st.write(f"- {key}: {value}")
    
    # Update simulation if running
    if st.session_state.is_running and not st.session_state.is_paused:
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
        st.session_state.simulation.update(
            time_delta=delta,
            auto_events=st.session_state.auto_events,
            risk_level=st.session_state.risk_level
        )
        
        # Update events list
        all_events = []
        for events in st.session_state.simulation.lifecycle_manager.lifecycle_events.values():
            all_events.extend(events)
        st.session_state.events = sorted(all_events, key=lambda e: e.timestamp)

if __name__ == "__main__":
    main()
