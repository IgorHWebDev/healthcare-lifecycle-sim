from datetime import datetime, timedelta
import streamlit as st
import os
import time
import plotly.graph_objects as go
from healthcare_sim.simulation_manager import SimulationManager
from healthcare_sim.reports import add_report_section
from healthcare_sim.visualization import (
    create_timeline_visualization,
    create_agent_path_visualization,
    create_agent_status_cards,
    create_event_frequency_charts,
    create_patient_statistics
)

def format_duration(td: timedelta) -> str:
    """Format timedelta into a readable string."""
    minutes = td.total_seconds() / 60
    return f"{minutes}m"

def create_simulation_stats(events, start_time):
    """Create statistics from simulation events."""
    stats = {
        'total_events': len(events),
        'emergency_count': len([e for e in events if e.get('type') == 'emergency']),
        'elapsed_minutes': (datetime.now() - start_time).total_seconds() / 60,
        'events_per_minute': len(events) / max(1, (datetime.now() - start_time).total_seconds() / 60)
    }
    return stats

def reset_simulation():
    """Reset the simulation state."""
    mimic_path = "/Users/igor/Downloads/mimic-iv-clinical-database-demo-2.2"
    
    # Initialize all session state variables
    if 'simulation_duration' not in st.session_state:
        st.session_state.simulation_duration = timedelta(hours=4)
    if 'duration_unit' not in st.session_state:
        st.session_state.duration_unit = 'hours'
    if 'auto_restart' not in st.session_state:
        st.session_state.auto_restart = False
    if 'emergency_frequency' not in st.session_state:
        st.session_state.emergency_frequency = 'normal'
    if 'show_agent_thoughts' not in st.session_state:
        st.session_state.show_agent_thoughts = True
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    if 'simulation_speed' not in st.session_state:
        st.session_state.simulation_speed = 0.5
    
    # Check if MIMIC data exists
    if os.path.exists(mimic_path):
        st.session_state.data_source = "MIMIC-IV Database"
    else:
        st.session_state.data_source = "Synthetic Data"
        mimic_path = None
    
    # Create new simulation instance
    st.session_state.simulation = SimulationManager(mimic_path=mimic_path)
    st.session_state.simulation.set_emergency_frequency(st.session_state.emergency_frequency)
    st.session_state.events = []
    st.session_state.start_time = datetime.now()
    st.session_state.is_running = False
    st.session_state.is_paused = False
    st.session_state.agent_paths = {}

def display_interface():
    """Display the main simulation interface."""
    # Top bar with simulation status and controls
    status_col1, status_col2, status_col3, status_col4 = st.columns([1, 2, 1, 1])
    
    with status_col1:
        if st.session_state.is_running and not st.session_state.is_paused:
            st.success("🟢 Running")
        elif st.session_state.is_paused:
            st.warning("⏸️ Paused")
        else:
            st.error("🔴 Stopped")
    
    with status_col2:
        stats = create_simulation_stats(st.session_state.events, st.session_state.start_time)
        progress = min((datetime.now() - st.session_state.start_time) / st.session_state.simulation_duration, 1.0)
        remaining_time = st.session_state.simulation_duration - (datetime.now() - st.session_state.start_time)
        if remaining_time.total_seconds() > 0:
            progress_text = f"Progress: {min(progress*100, 100):.1f}% (Remaining: {format_duration(remaining_time)})"
        else:
            progress_text = "Progress: 100.0% (Completed)"
        st.progress(min(progress, 1.0), text=progress_text)
    
    with status_col3:
        st.metric("Events/Minute", stats['events_per_minute'])
    
    with status_col4:
        st.metric("Active Agents", len(st.session_state.simulation.agents))
    
    # Main title and data source
    st.title("Healthcare Facility Simulation")
    st.caption(f"Using {st.session_state.data_source}")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Simulation Controls")
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start" if not st.session_state.is_running else "⏹️ Stop", type="primary"):
                st.session_state.is_running = not st.session_state.is_running
                st.session_state.is_paused = False
        with col2:
            if st.button("⏸️ Pause" if not st.session_state.is_paused else "⏵️ Resume", disabled=not st.session_state.is_running):
                st.session_state.is_paused = not st.session_state.is_paused
        
        if st.button("🔄 Reset Simulation", type="secondary"):
            reset_simulation()
            st.rerun()
        
        # Advanced settings
        with st.expander("⚙️ Advanced Settings", expanded=False):
            st.checkbox("🔄 Auto-restart on completion", key="auto_restart")
            st.checkbox("💭 Show agent thoughts", key="show_agent_thoughts")
            st.checkbox("🐛 Debug mode", key="debug_mode")
            
            st.selectbox(
                "🚨 Emergency Frequency",
                options=['low', 'normal', 'high'],
                key="emergency_frequency"
            )
        
        # Simulation duration
        st.subheader("⏱️ Duration Settings")
        
        # Duration unit selection
        duration_unit = st.radio(
            "Time Unit",
            options=['minutes', 'hours'],
            horizontal=True,
            key='duration_unit'
        )
        
        # Duration input based on selected unit
        if duration_unit == 'minutes':
            minutes = st.slider("Duration (minutes)", 1, 1440, 240)
            st.session_state.simulation_duration = timedelta(minutes=minutes)
            st.caption(f"Equivalent to {minutes/60:.1f} hours")
        else:  # hours
            hours = st.slider("Duration (hours)", 1, 24, 4)
            st.session_state.simulation_duration = timedelta(hours=hours)
            st.caption(f"Equivalent to {hours*60} minutes")
        
        # Display total duration
        st.info(f"⏰ Total simulation time: {format_duration(st.session_state.simulation_duration)}")
        
        # Simulation speed
        st.subheader("⚡ Speed Settings")
        st.session_state.simulation_speed = st.slider(
            "Steps per second",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.simulation_speed,
            step=0.1,
            help="Higher values = faster simulation"
        )
        
        # Statistics
        st.subheader("📊 Statistics")
        st.metric("Total Events", stats['total_events'])
        st.metric("Emergency Events", stats['emergency_count'])
        st.metric("Elapsed Time", f"{stats['elapsed_minutes']:.1f} min")
        
        if st.session_state.debug_mode:
            st.subheader("🐛 Debug Information")
            st.json({
                "running": st.session_state.is_running,
                "paused": st.session_state.is_paused,
                "progress": f"{progress*100:.1f}%",
                "events": len(st.session_state.events),
                "agents": len(st.session_state.agent_paths)
            })
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Activity Timeline",
        "Facility Layout and Agent Movements",
        "Event Frequency",
        "Patient Statistics",
        "Reports"
    ])
    
    with tab1:
        # Timeline visualization
        st.header("Activity Timeline")
        timeline = create_timeline_visualization(
            st.session_state.events,
            st.session_state.start_time,
            datetime.now()
        )
        if timeline:
            st.plotly_chart(timeline, use_container_width=True)
        
        # Agent movement visualization
        st.header("Facility Layout and Agent Movements")
        movement_viz = create_agent_path_visualization(
            st.session_state.agent_paths,
            st.session_state.simulation.environment
        )
        st.plotly_chart(movement_viz, use_container_width=True)
    
    with tab2:
        # Healthcare Professional Status
        st.header("Healthcare Professionals")
        create_agent_status_cards(st.session_state.simulation)
    
    with tab3:
        # Event Frequency Analysis
        st.header("Event Analysis")
        create_event_frequency_charts(st.session_state.events)
    
    with tab4:
        # Patient Statistics
        st.header("Patient Statistics")
        create_patient_statistics(st.session_state.simulation)
    
    with tab5:
        # Reports
        add_report_section(st)

def main():
    st.set_page_config(page_title="Healthcare Simulation", layout="wide")
    
    # Initialize session state
    if 'simulation' not in st.session_state:
        reset_simulation()
    
    # Update emergency frequency when changed
    if 'emergency_frequency' in st.session_state:
        st.session_state.simulation.set_emergency_frequency(st.session_state.emergency_frequency)
    
    # Calculate elapsed time and check if simulation should stop
    elapsed_time = datetime.now() - st.session_state.start_time
    if elapsed_time >= st.session_state.simulation_duration and st.session_state.is_running:
        st.session_state.is_running = False
        st.warning("⏰ Simulation completed! Duration reached.")
        if st.session_state.auto_restart:
            reset_simulation()
            st.session_state.is_running = True
            st.info("🔄 Auto-restarting simulation...")
    
    # Safety check - stop if no events after certain time
    if st.session_state.is_running and elapsed_time.total_seconds() > 30 and len(st.session_state.events) == 0:
        st.session_state.is_running = False
        st.error("⚠️ Simulation stopped: No events generated. Please check configuration and try again.")
        if st.button("🔄 Restart Simulation"):
            reset_simulation()
            st.session_state.is_running = True
            st.rerun()
    
    # Display interface
    display_interface()
    
    # Run simulation
    if st.session_state.is_running and not st.session_state.is_paused:
        try:
            # Process multiple steps per update for smoother performance
            steps_per_update = max(1, int(st.session_state.simulation_duration.total_seconds() / 100))
            for _ in range(steps_per_update):
                if elapsed_time < st.session_state.simulation_duration:
                    events = st.session_state.simulation.step()
                    if events:
                        st.session_state.events.extend(events)
                        for event in events:
                            agent_id = event.get('agent_id')
                            if agent_id and agent_id not in st.session_state.agent_paths:
                                st.session_state.agent_paths[agent_id] = []
                            if agent_id and 'location' in event:
                                st.session_state.agent_paths[agent_id].append(event['location'])
                else:
                    st.session_state.is_running = False
                    break
            
            # Add small delay based on simulation speed
            time.sleep(1/max(0.1, st.session_state.simulation_speed))
            st.rerun()
            
        except Exception as e:
            st.error(f"Simulation error: {str(e)}")
            st.session_state.is_running = False
            if st.button("🔄 Restart After Error"):
                reset_simulation()
                st.rerun()

if __name__ == "__main__":
    main() 