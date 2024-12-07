import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_lifecycle_timeline(events):
    """Create a timeline visualization of lifecycle events."""
    if not events:
        return None
        
    fig = go.Figure()
    
    for event in events:
        fig.add_trace(go.Scatter(
            x=[event.timestamp],
            y=[event.stage.name],
            mode='markers+text',
            name=event.event_id,
            text=[event.description],
            marker=dict(size=10),
            textposition="top center"
        ))
    
    fig.update_layout(
        title='Lifecycle Timeline',
        xaxis_title='Time',
        yaxis_title='Stage',
        height=400
    )
    
    return fig

def create_stage_distribution(events):
    """Create a pie chart showing distribution of lifecycle stages."""
    if not events:
        return None
        
    stages = [event.stage.name for event in events]
    stage_counts = {}
    for stage in stages:
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(stage_counts.keys()),
        values=list(stage_counts.values()),
        hole=.3
    )])
    
    fig.update_layout(
        title="Lifecycle Stage Distribution"
    )
    
    return fig

def create_genetic_timeline(genetic_materials):
    """Create a timeline of genetic material registrations."""
    if not genetic_materials:
        return None
        
    fig = go.Figure()
    
    for material_id, material in genetic_materials.items():
        fig.add_trace(go.Scatter(
            x=[material.collection_date],
            y=[material.material_type],
            mode='markers+text',
            name=material_id,
            text=[f"Donor: {material.donor_id or 'Anonymous'}"],
            marker=dict(size=10),
            textposition="top center"
        ))
    
    fig.update_layout(
        title='Genetic Material Timeline',
        xaxis_title='Collection Date',
        yaxis_title='Material Type',
        height=400
    )
    
    return fig

def display_lifecycle_dashboard(lifecycle_manager, patient_id):
    """Display comprehensive lifecycle dashboard."""
    events = lifecycle_manager.get_patient_timeline(patient_id)
    
    if not events:
        st.info(f"No events found for patient {patient_id}")
        return
    
    # Timeline visualization
    timeline = create_lifecycle_timeline(events)
    if timeline:
        st.plotly_chart(timeline, use_container_width=True)
    
    # Stage distribution
    distribution = create_stage_distribution(events)
    if distribution:
        st.plotly_chart(distribution, use_container_width=True)
    
    # Event details
    st.subheader("Event Details")
    for event in events:
        with st.expander(f"{event.stage.name} - {event.timestamp.strftime('%Y-%m-%d %H:%M')}"):
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

def create_agent_path_visualization(agent_paths):
    """Create a visualization of agent movements."""
    if not agent_paths:
        return None
        
    fig = go.Figure()
    
    # Add paths for each agent
    for agent_id, locations in agent_paths.items():
        x_coords = list(range(len(locations)))
        
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=locations,
            mode='lines+markers',
            name=f'Agent {agent_id}',
            text=locations,
            textposition="top center"
        ))
    
    fig.update_layout(
        title='Agent Movement Paths',
        xaxis_title='Time Step',
        yaxis_title='Location',
        height=400
    )
    
    return fig