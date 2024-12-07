import streamlit as st
import os
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import Dict
from healthcare_sim.simulation_manager import SimulationManager
from healthcare_sim.visualization import (
    create_lifecycle_timeline,
    create_stage_distribution,
    create_genetic_timeline,
    display_lifecycle_dashboard,
    create_agent_path_visualization
)
from healthcare_sim.lifecycle.lifecycle_manager import LifecycleStage

def format_duration(td: timedelta) -> str:
    """Format timedelta into a readable string."""
    minutes = td.total_seconds() / 60
    return f"{minutes}m"

def reset_simulation():
    """Reset the simulation state."""
    if 'simulation' not in st.session_state:
        st.session_state.simulation = SimulationManager()
        st.session_state.events = st.session_state.simulation.lifecycle_manager.get_patient_timeline("patient_789")
        st.session_state.start_time = datetime.now()
        st.session_state.is_running = False
        st.session_state.is_paused = False
        st.session_state.agent_paths = {}

def display_facility_layout():
    """Display facility layout in a more visual way."""
    layout = st.session_state.simulation.get_facility_layout()
    
    # Display departments as columns
    cols = st.columns(len(layout["departments"]))
    for col, (dept_id, dept) in zip(cols, layout["departments"].items()):
        with col:
            st.markdown(f"### {dept['name']}")
            for loc in dept['locations']:
                st.markdown(f"- 📍 {loc}")
    
    # Display connections
    st.markdown("### Department Connections")
    for conn in layout["connections"]:
        st.markdown(f"🔄 {conn[0]} ↔️ {conn[1]}")

def display_stage_specific_interface(stage: LifecycleStage, lifecycle_manager):
    """Display interface specific to the selected lifecycle stage."""
    if stage == LifecycleStage.PRE_CONCEPTION:
        st.subheader("Pre-conception Stage")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("genetic_material"):
                material_type = st.selectbox("Material Type", ["egg", "sperm"])
                donor_id = st.text_input("Donor ID")
                if st.form_submit_button("Register Material"):
                    try:
                        material_id = lifecycle_manager.register_genetic_material(
                            material_type=material_type,
                            donor_id=donor_id,
                            genetic_markers={"marker1": "test"}
                        )
                        st.success(f"Registered {material_type} with ID: {material_id}")
                    except Exception as e:
                        st.error(f"Error registering material: {str(e)}")
        
        with col2:
            st.markdown("### Registered Materials")
            for material_id, material in lifecycle_manager.genetic_materials.items():
                st.markdown(f"""
                - **{material.material_type.title()}** (ID: {material_id})
                  - Donor: {material.donor_id or 'Anonymous'}
                  - Collected: {material.collection_date.strftime('%Y-%m-%d %H:%M')}
                """)
    
    elif stage == LifecycleStage.CONCEPTION:
        st.subheader("Conception Stage")
        with st.form("conception_event"):
            col1, col2 = st.columns(2)
            with col1:
                egg_materials = {k: v for k, v in lifecycle_manager.genetic_materials.items() 
                               if v.material_type == "egg"}
                sperm_materials = {k: v for k, v in lifecycle_manager.genetic_materials.items() 
                                 if v.material_type == "sperm"}
                
                egg_id = st.selectbox("Select Egg", options=list(egg_materials.keys()))
                sperm_id = st.selectbox("Select Sperm", options=list(sperm_materials.keys()))
            
            with col2:
                location = st.text_input("Location")
                providers = st.text_input("Healthcare Providers (comma-separated)")
            
            if st.form_submit_button("Create Conception Event"):
                try:
                    event_id = lifecycle_manager.create_lifecycle_event(
                        patient_id="patient_789",
                        stage=stage,
                        description=f"IVF conception using egg {egg_id} and sperm {sperm_id}",
                        location=location,
                        providers=providers.split(",") if providers else ["Unknown"],
                        genetic_data={
                            "egg_id": egg_id,
                            "sperm_id": sperm_id
                        }
                    )
                    st.session_state.events = lifecycle_manager.get_patient_timeline("patient_789")
                    st.success(f"Created conception event with ID: {event_id}")
                except Exception as e:
                    st.error(f"Error creating event: {str(e)}")
    
    else:
        st.subheader(f"{stage.name} Stage")
        with st.form("create_event"):
            col1, col2 = st.columns(2)
            
            with col1:
                description = st.text_area("Event Description")
                location = st.text_input("Location")
            
            with col2:
                providers = st.text_input("Healthcare Providers (comma-separated)")
                include_biometrics = st.checkbox("Include Biometric Data")
            
            if include_biometrics:
                st.markdown("### Biometric Data")
                bio_col1, bio_col2 = st.columns(2)
                with bio_col1:
                    height = st.number_input("Height (cm)", min_value=0.0)
                    weight = st.number_input("Weight (kg)", min_value=0.0)
                with bio_col2:
                    blood_pressure = st.text_input("Blood Pressure (e.g., 120/80)")
                    heart_rate = st.number_input("Heart Rate (bpm)", min_value=0)
            
            if st.form_submit_button("Create Event"):
                try:
                    biometric_data = None
                    if include_biometrics:
                        biometric_data = {
                            "height_cm": height,
                            "weight_kg": weight,
                            "blood_pressure": blood_pressure,
                            "heart_rate_bpm": heart_rate
                        }
                    
                    event_id = lifecycle_manager.create_lifecycle_event(
                        patient_id="patient_789",
                        stage=stage,
                        description=description,
                        location=location,
                        providers=providers.split(",") if providers else ["Unknown"],
                        biometric_data=biometric_data
                    )
                    st.session_state.events = lifecycle_manager.get_patient_timeline("patient_789")
                    st.success(f"Created event with ID: {event_id}")
                except Exception as e:
                    st.error(f"Error creating event: {str(e)}")

def display_interface():
    """Display the main simulation interface."""
    st.title("Healthcare Lifecycle Simulation")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs([
        "Activity Timeline",
        "Facility Layout",
        "🧬 Lifecycle Management"
    ])
    
    with tab1:
        st.header("Activity Timeline")
        if not st.session_state.events:
            st.info("No events recorded yet. Use the Lifecycle Management tab to create events.")
        else:
            try:
                timeline = create_lifecycle_timeline(st.session_state.events)
                if timeline:
                    st.plotly_chart(timeline, use_container_width=True)
                    
                # Show event distribution
                distribution = create_stage_distribution(st.session_state.events)
                if distribution:
                    st.plotly_chart(distribution, use_container_width=True)
                    
                # Show event details
                st.subheader("Event Details")
                for event in sorted(st.session_state.events, key=lambda e: e.timestamp, reverse=True):
                    with st.expander(f"{event.stage.name} - {event.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                        st.markdown(f"""
                        **Description:** {event.description}
                        **Location:** {event.location}
                        **Providers:** {', '.join(event.providers)}
                        """)
                        
                        if event.biometric_data:
                            st.markdown("**Biometric Data:**")
                            for key, value in event.biometric_data.items():
                                st.markdown(f"- {key}: {value}")
                        
                        if event.genetic_data:
                            st.markdown("**Genetic Data:**")
                            for key, value in event.genetic_data.items():
                                st.markdown(f"- {key}: {value}")
            except Exception as e:
                st.error(f"Error creating timeline: {str(e)}")
    
    with tab2:
        st.header("Facility Layout")
        display_facility_layout()
    
    with tab3:
        st.header("🧬 Lifecycle Management")
        try:
            # Get lifecycle manager
            lifecycle_manager = st.session_state.simulation.lifecycle_manager
            
            # Lifecycle stage selector
            stage = st.selectbox(
                "Select Lifecycle Stage",
                options=list(LifecycleStage)
            )
            
            # Display stage-specific interface
            display_stage_specific_interface(stage, lifecycle_manager)
                
        except Exception as e:
            st.error(f"Error in lifecycle management: {str(e)}")

def main():
    st.set_page_config(
        page_title="Healthcare Simulation",
        page_icon="🏥",
        layout="wide"
    )
    
    # Initialize simulation if needed
    if 'simulation' not in st.session_state:
        reset_simulation()
    
    # Display interface
    display_interface()

if __name__ == "__main__":
    main() 