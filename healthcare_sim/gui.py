import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Dict, List
from simulation_manager import SimulationManager
from lifecycle.lifecycle_manager import LifecycleStage

def reset_simulation():
    """Reset the simulation state."""
    if 'simulation' not in st.session_state:
        st.session_state.simulation = SimulationManager()
        
        # Add some initial patients
        sim = st.session_state.simulation
        
        # Admit some initial patients
        initial_patients = [
            ("ER001", "er", "Under Observation"),
            ("ICU001", "icu", "Critical"),
            ("WARD001", "ward", "Stable"),
            ("WARD002", "ward", "Improving")
        ]
        
        for patient_id, dept, status in initial_patients:
            sim.db.admit_patient(patient_id, dept, status)
            
            # Generate initial event for each patient
            sim._generate_patient_event({
                "patient_id": patient_id,
                "department_name": sim.db.departments[dept]["name"],
                "status": status
            })
        
        st.session_state.events = []
        st.session_state.start_time = datetime.now()
        st.session_state.is_running = False
        st.session_state.simulation_speed = 1.0
        st.session_state.last_update = datetime.now()

def update_simulation():
    """Update simulation state if running."""
    if st.session_state.is_running:
        current_time = datetime.now()
        elapsed = current_time - st.session_state.last_update
        scaled_elapsed = elapsed * st.session_state.simulation_speed
        st.session_state.simulation.update(scaled_elapsed)
        st.session_state.last_update = current_time

def display_hospital_overview():
    """Display hospital departments and their current status with detailed metrics."""
    st.subheader("🏥 Hospital Overview")
    
    # Get department statistics
    departments = st.session_state.simulation.db.get_department_stats()
    
    # Summary metrics
    total_patients = sum(dept["current_occupancy"] for dept in departments)
    total_capacity = sum(dept["capacity"] for dept in departments)
    overall_occupancy = (total_patients / total_capacity * 100) if total_capacity > 0 else 0
    
    # Overall hospital metrics
    st.markdown("### Hospital Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Patients",
            f"{total_patients}/{total_capacity}",
            f"{overall_occupancy:.1f}% Occupied"
        )
    with col2:
        critical_count = len([p for p in st.session_state.simulation.db.get_active_patients() 
                            if p["status"] == "Critical"])
        st.metric("Critical Patients", critical_count)
    with col3:
        available_beds = total_capacity - total_patients
        st.metric("Available Beds", available_beds)
    
    # Department details
    st.markdown("### Department Status")
    
    # Create columns for departments
    cols = st.columns(len(departments))
    for col, dept in zip(cols, departments):
        with col:
            occupancy_pct = (dept["current_occupancy"] / dept["capacity"]) * 100
            
            # Department metrics
            st.markdown(f"#### {dept['name']}")
            st.metric(
                "Occupancy",
                f"{dept['current_occupancy']}/{dept['capacity']}",
                f"{occupancy_pct:.1f}% Occupied",
                delta_color="inverse"
            )
            
            # Visual capacity indicator
            st.progress(occupancy_pct/100, text=f"{occupancy_pct:.1f}%")
            
            # Department patients
            patients = [p for p in st.session_state.simulation.db.get_active_patients() 
                       if p["department_name"] == dept["name"]]
            
            if patients:
                with st.expander("View Patients"):
                    for p in patients:
                        st.markdown(f"• {p['patient_id']} ({p['status']})")

def display_patient_monitor():
    """Display active patients and their status with interactive controls."""
    st.subheader("👥 Patient Monitor")
    
    patients = st.session_state.simulation.db.get_active_patients()
    if not patients:
        st.info("No active patients in the hospital")
        return
    
    # Add new patient button
    with st.expander("➕ Admit New Patient"):
        col1, col2 = st.columns(2)
        with col1:
            new_patient_id = st.text_input("Patient ID", value=f"P{len(patients)+1:03d}")
            department = st.selectbox(
                "Initial Department",
                options=["Emergency Room", "General Ward"],
                index=0
            )
        with col2:
            initial_status = st.selectbox(
                "Initial Status",
                options=["Stable", "Under Observation", "Critical"],
                index=1
            )
            if st.button("Admit Patient"):
                dept_id = next(
                    (k for k, v in st.session_state.simulation.db.departments.items() 
                     if v["name"] == department),
                    "er"
                )
                if st.session_state.simulation.db.admit_patient(new_patient_id, dept_id, initial_status):
                    st.success(f"Patient {new_patient_id} admitted to {department}")
                else:
                    st.error(f"Could not admit patient - {department} is full")
    
    # Display active patients
    st.markdown("### Active Patients")
    
    # Create patient table
    patient_table = []
    for p in patients:
        patient_table.append({
            "ID": p["patient_id"],
            "Location": p["department_name"],
            "Status": p["status"]
        })
    
    if patient_table:
        st.table(pd.DataFrame(patient_table))
    
    # Display detailed patient cards
    for patient in patients:
        with st.expander(f"Patient {patient['patient_id']} - {patient['status']}"):
            col1, col2, col3 = st.columns([2,2,1])
            
            with col1:
                st.markdown(f"**Location:** {patient['department_name']}")
                st.markdown(f"**Status:** {patient['status']}")
                
                # Get vital signs
                vitals = st.session_state.simulation.db.vital_signs.get(patient['patient_id'], [])
                if vitals:
                    latest_vitals = vitals[-1]['data']
                    st.markdown("**Latest Vitals:**")
                    for key, value in latest_vitals.items():
                        st.text(f"  • {key}: {value}")
            
            with col2:
                # Patient actions
                new_status = st.selectbox(
                    "Update Status",
                    options=["Stable", "Critical", "Improving", "Under Observation", "Ready for Discharge"],
                    key=f"status_{patient['patient_id']}"
                )
                
                new_dept = st.selectbox(
                    "Transfer to Department",
                    options=[d["name"] for d in st.session_state.simulation.db.get_department_stats()],
                    key=f"dept_{patient['patient_id']}"
                )
            
            with col3:
                if st.button("Update", key=f"update_{patient['patient_id']}"):
                    # Update status
                    st.session_state.simulation.db.update_patient_status(
                        patient['patient_id'],
                        new_status
                    )
                    
                    # Handle transfer if department changed
                    if new_dept != patient['department_name']:
                        dept_id = next(
                            (k for k, v in st.session_state.simulation.db.departments.items() 
                             if v["name"] == new_dept),
                            None
                        )
                        if dept_id:
                            if st.session_state.simulation.db.transfer_patient(patient['patient_id'], dept_id):
                                st.success(f"Patient transferred to {new_dept}")
                            else:
                                st.error(f"Transfer failed - {new_dept} is full")
                
                if st.button("Discharge", key=f"discharge_{patient['patient_id']}"):
                    # Remove patient from the system
                    if patient['patient_id'] in st.session_state.simulation.db.patients:
                        del st.session_state.simulation.db.patients[patient['patient_id']]
                        st.success(f"Patient {patient['patient_id']} discharged")
                        st.rerun()

def display_activity_feed():
    """Display recent activities in the hospital with filtering options."""
    st.subheader("📋 Recent Activities")
    
    # Get recent events
    events = st.session_state.simulation.lifecycle_manager.get_recent_events()
    
    if not events:
        st.info("No recent activities")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_location = st.multiselect(
            "Filter by Location",
            options=list(set(event.location for event in events)),
            default=[]
        )
    with col2:
        filter_type = st.multiselect(
            "Filter by Event Type",
            options=["Transfer", "Status Update", "Admission", "Treatment"],
            default=[]
        )
    
    # Display filtered events
    for event in events:
        # Apply filters
        if filter_location and event.location not in filter_location:
            continue
        if filter_type:
            event_type = next((t for t in filter_type if t.lower() in event.description.lower()), None)
            if not event_type:
                continue
        
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                st.text(event.timestamp.strftime("%H:%M:%S"))
            with cols[1]:
                st.markdown(f"**{event.description}**")
                if event.biometric_data:
                    with st.expander("Vital Signs"):
                        for key, value in event.biometric_data.items():
                            st.text(f"{key}: {value}")

def display_simulation_controls():
    """Display simulation control buttons."""
    st.sidebar.header("⚙️ Simulation Controls")
    
    # Play/Pause button
    if st.sidebar.button("▶️ Start" if not st.session_state.is_running else "⏸️ Pause"):
        st.session_state.is_running = not st.session_state.is_running
        if st.session_state.is_running:
            st.session_state.last_update = datetime.now()
    
    # Reset button
    if st.sidebar.button("🔄 Reset Simulation"):
        reset_simulation()
    
    # Speed control
    st.sidebar.slider(
        "🚀 Simulation Speed",
        min_value=0.1,
        max_value=5.0,
        value=st.session_state.simulation_speed,
        step=0.1,
        key="simulation_speed",
        help="Adjust how fast the simulation runs"
    )
    
    # Display current simulation time
    if st.session_state.is_running:
        st.sidebar.metric(
            "⏰ Simulation Time",
            st.session_state.simulation.current_time.strftime("%H:%M:%S"),
            delta="Running" if st.session_state.is_running else "Paused"
        )

def main():
    st.set_page_config(
        page_title="Hospital Simulation",
        page_icon="🏥",
        layout="wide"
    )
    
    # Initialize simulation if needed
    if 'simulation' not in st.session_state:
        reset_simulation()
    
    # Title and description
    st.title("🏥 Hospital Simulation Dashboard")
    st.markdown("""
    This dashboard shows real-time hospital operations, patient status, and department activities.
    Use the controls in the sidebar to manage the simulation.
    """)
    
    # Display simulation controls in sidebar
    display_simulation_controls()
    
    # Update simulation state
    update_simulation()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Hospital overview section
        display_hospital_overview()
        st.divider()
        # Patient monitor section
        display_patient_monitor()
    
    with col2:
        # Activity feed section
        display_activity_feed()

if __name__ == "__main__":
    main() 