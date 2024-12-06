import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def create_timeline_visualization(events, start_time, end_time):
    """Create a Gantt chart showing agent activities over time."""
    df = []
    
    for event in events:
        # Estimate duration based on action type
        if "emergency" in event.get("type", ""):
            duration = timedelta(minutes=30)
        else:
            duration = timedelta(minutes=15)
            
        df.append({
            'Task': f"{event['agent_id']} - {event['action']}",
            'Start': event['timestamp'],
            'Finish': event['timestamp'] + duration,
            'Location': event['location'],
            'Type': event.get('type', 'routine')
        })
    
    df = pd.DataFrame(df)
    
    if len(df) == 0:
        return None
        
    colors = {
        'emergency': 'rgb(255, 0, 0)',
        'routine': 'rgb(0, 255, 0)'
    }
    
    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col='Type',
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True
    )
    
    fig.update_layout(
        title='Agent Activities Timeline',
        xaxis_title='Time',
        height=400,
        font=dict(size=10)
    )
    
    return fig

def create_agent_path_visualization(agent_locations, environment):
    """Create a visualization of agent movements in the hospital."""
    fig = go.Figure()
    
    # Create nodes for all locations
    for loc_id, location in environment.locations.items():
        pos = get_location_position(loc_id)  # You'll need to implement this
        fig.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            name=loc_id,
            text=[loc_id],
            marker=dict(size=20),
            textposition="bottom center"
        ))
    
    # Add paths for each agent
    for agent_id, locations in agent_locations.items():
        path_x = []
        path_y = []
        for loc in locations:
            pos = get_location_position(loc)
            path_x.append(pos[0])
            path_y.append(pos[1])
        
        fig.add_trace(go.Scatter(
            x=path_x,
            y=path_y,
            mode='lines',
            name=f'Agent {agent_id} path',
            line=dict(width=2, dash='dot')
        ))
    
    fig.update_layout(
        title='Agent Movement Paths',
        showlegend=True,
        height=500
    )
    
    return fig

def get_location_position(location_id):
    """Get the x,y coordinates for a location in the visualization."""
    # This is a simplified positioning system - you might want to make this more sophisticated
    positions = {
        'ward_1': (0, 0),
        'ward_2': (1, 0),
        'icu_1': (0, 1),
        'er': (1, 1),
        'or_1': (2, 0),
        'or_2': (2, 1),
        'pharmacy': (3, 0),
        'nurse_station_1': (1.5, 0.5)
    }
    return positions.get(location_id, (0, 0))

def create_agent_status_cards(simulation):
    """Create status cards for each healthcare professional."""
    for agent_id, agent in simulation.agents.items():
        with st.expander(f"{agent.name} - {agent.specialization}", expanded=True):
            status = simulation.get_agent_status(agent_id)
            
            # Create metrics for key information
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Patient Count",
                    value=status.get('patient_count', 0)
                )
            with col2:
                st.metric(
                    label="Fatigue Level",
                    value=f"{status['fatigue']*100:.0f}%"
                )
            
            st.write(f"📍 Location: {status['location']}")
            st.write(f"🏥 Status: {status['status']}")
            st.write(f"⚕️ Current Action: {status['current_action']}")
            
            # Show fatigue level with color coding
            fatigue = status['fatigue']
            fatigue_color = (
                "🟢" if fatigue < 0.3 else
                "🟡" if fatigue < 0.7 else
                "🔴"
            )
            st.write(f"{fatigue_color} Energy Level:")
            st.progress(1 - fatigue)
            
            # Show assigned patients if doctor
            if hasattr(agent, 'patients'):
                st.write("🏥 Assigned Patients:")
                for patient_id, patient in agent.patients.items():
                    diagnosis = patient['latest_admission']['diagnosis']
                    location = patient['latest_admission']['admission_location']
                    st.info(
                        f"Patient {patient_id}\n"
                        f"Diagnosis: {diagnosis}\n"
                        f"Location: {location}"
                    )

def create_event_frequency_charts(events):
    """Create charts showing event frequency and distribution."""
    if not events:
        st.info("No events recorded yet.")
        return
        
    # Event type distribution
    event_types = [e.get('type', 'routine') for e in events]
    type_counts = pd.Series(event_types).value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=type_counts.index,
        values=type_counts.values,
        hole=.3
    )])
    fig.update_layout(title="Event Type Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Event timeline
    df = pd.DataFrame(events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    # Resample by minute and count events
    event_counts = df.resample('1T').size()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=event_counts.index,
        y=event_counts.values,
        mode='lines+markers',
        name='Events per Minute'
    ))
    fig.update_layout(
        title="Event Frequency Over Time",
        xaxis_title="Time",
        yaxis_title="Number of Events"
    )
    st.plotly_chart(fig, use_container_width=True)

def create_patient_statistics(simulation):
    """Create patient statistics visualizations."""
    if not simulation.patient_data:
        st.info("No patient data available.")
        return
    
    # Department distribution
    dept_dist = simulation.patient_data.get_department_distribution()
    
    # Create two columns for statistics
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.subheader("Patient Distribution")
        fig = go.Figure(data=[go.Bar(
            x=list(dept_dist.keys()),
            y=list(dept_dist.values())
        )])
        fig.update_layout(
            title="Patients by Department",
            xaxis_title="Department",
            yaxis_title="Number of Patients"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with stat_col2:
        # Emergency cases
        emergency_cases = simulation.patient_data.get_emergency_cases()
        st.subheader("Emergency Cases")
        st.metric(
            label="Active Emergency Cases",
            value=len(emergency_cases),
            delta=None
        )
        
        if emergency_cases:
            with st.expander("View Emergency Cases"):
                for case in emergency_cases[:5]:  # Show only the first 5 cases
                    st.markdown(f"""
                    **Patient {case['patient_id']}**
                    - Diagnosis: {case['primary_diagnosis']}
                    - Age: {case['age']}
                    - Location: {case['current_location']}
                    - Admitted: {case['admission_time'].strftime('%Y-%m-%d %H:%M')}
                    """)