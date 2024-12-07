import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from ..lifecycle.lifecycle_manager import LifecycleStage, LifecycleEvent

def create_lifecycle_timeline(events: List[LifecycleEvent]) -> go.Figure:
    """Create an interactive timeline visualization of lifecycle events"""
    
    # Prepare data
    df = pd.DataFrame([
        {
            'Stage': event.stage.value,
            'Date': event.timestamp,
            'Description': event.description,
            'Location': event.location,
            'Providers': ', '.join(event.providers),
            'Has_Genetic': bool(event.genetic_data),
            'Has_Biometric': bool(event.biometric_data)
        }
        for event in events
    ])
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add events as scatter plot
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Stage'],
            mode='markers+text',
            name='Events',
            text=df['Description'],
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Date: %{x}<br>' +
                'Stage: %{y}<br>' +
                '<extra></extra>'
            ),
            marker=dict(
                size=12,
                symbol='circle',
                color=['red' if g else 'blue' for g in df['Has_Genetic']]
            )
        )
    )
    
    # Add connecting lines
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Stage'],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Patient Lifecycle Timeline',
        xaxis_title='Date',
        yaxis_title='Lifecycle Stage',
        height=600,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

def create_stage_distribution(events: List[LifecycleEvent]) -> go.Figure:
    """Create a visualization of event distribution across lifecycle stages"""
    
    # Count events per stage
    stage_counts = {}
    for event in events:
        stage_counts[event.stage.value] = stage_counts.get(event.stage.value, 0) + 1
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(stage_counts.keys()),
            y=list(stage_counts.values()),
            text=list(stage_counts.values()),
            textposition='auto',
        )
    ])
    
    # Update layout
    fig.update_layout(
        title='Events by Lifecycle Stage',
        xaxis_title='Stage',
        yaxis_title='Number of Events',
        height=400
    )
    
    return fig

def create_genetic_timeline(events: List[LifecycleEvent]) -> go.Figure:
    """Create a timeline visualization focusing on genetic data"""
    
    # Filter events with genetic data
    genetic_events = [e for e in events if e.genetic_data]
    
    # Prepare data
    df = pd.DataFrame([
        {
            'Stage': event.stage.value,
            'Date': event.timestamp,
            'Description': event.description,
            'Genetic_Markers': len(event.genetic_data.keys()) if event.genetic_data else 0
        }
        for event in genetic_events
    ])
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot for genetic events
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Genetic_Markers'],
            mode='markers+lines',
            name='Genetic Markers',
            text=df['Description'],
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Date: %{x}<br>' +
                'Markers: %{y}<br>' +
                '<extra></extra>'
            ),
            marker=dict(
                size=10,
                color=df['Genetic_Markers'],
                colorscale='Viridis',
                showscale=True
            )
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Genetic Data Timeline',
        xaxis_title='Date',
        yaxis_title='Number of Genetic Markers',
        height=400
    )
    
    return fig

def display_lifecycle_dashboard(lifecycle_manager, patient_id: str):
    """Display comprehensive lifecycle dashboard"""
    
    st.header("🧬 Patient Lifecycle Dashboard")
    
    # Get patient timeline
    events = lifecycle_manager.get_patient_timeline(patient_id)
    
    if not events:
        st.warning("No lifecycle events found for this patient.")
        return
    
    # Timeline visualization
    st.subheader("📊 Lifecycle Timeline")
    timeline_fig = create_lifecycle_timeline(events)
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Stage distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Event Distribution")
        dist_fig = create_stage_distribution(events)
        st.plotly_chart(dist_fig, use_container_width=True)
    
    with col2:
        st.subheader("🧬 Genetic Timeline")
        genetic_fig = create_genetic_timeline(events)
        st.plotly_chart(genetic_fig, use_container_width=True)
    
    # Detailed event list
    st.subheader("📝 Event Details")
    for event in events:
        with st.expander(
            f"{event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.stage.value}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Description:** {event.description}")
                st.markdown(f"**Location:** {event.location}")
                st.markdown(f"**Providers:** {', '.join(event.providers)}")
            
            with col2:
                if event.genetic_data:
                    st.markdown("🧬 **Genetic Data Available**")
                if event.biometric_data:
                    st.markdown("👤 **Biometric Data Available**")
                st.markdown(f"**Event ID:** `{event.event_id}`")
                st.markdown(f"**Data Hash:** `{event.data_hash[:8]}...`") 