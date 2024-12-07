import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List
from datetime import datetime

def create_agent_path_visualization(agent_paths: Dict[str, List[str]]) -> go.Figure:
    """Create a visualization of agent movements in the facility"""
    # Create a graph of the facility layout
    G = nx.Graph()
    
    # Add basic facility locations
    locations = [
        "entrance", "waiting_room", "triage", "er", "icu", "ward",
        "pharmacy", "lab", "imaging", "surgery", "staff_room"
    ]
    
    # Add nodes and edges to create facility layout
    G.add_nodes_from(locations)
    G.add_edges_from([
        ("entrance", "waiting_room"),
        ("waiting_room", "triage"),
        ("triage", "er"),
        ("er", "icu"),
        ("er", "ward"),
        ("ward", "pharmacy"),
        ("ward", "lab"),
        ("ward", "imaging"),
        ("er", "surgery"),
        ("staff_room", "ward")
    ])
    
    # Calculate layout
    pos = nx.spring_layout(G)
    
    # Create figure
    fig = go.Figure()
    
    # Add edges (corridors)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='gray'),
        hoverinfo='none',
        mode='lines',
        name='Corridors'
    ))
    
    # Add nodes (locations)
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node.replace('_', ' ').title())
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        name='Locations',
        marker=dict(
            size=20,
            color='lightblue',
            line_width=2
        ),
        text=node_text,
        textposition="top center"
    ))
    
    # Add agent paths
    for agent_id, path in agent_paths.items():
        path_x = []
        path_y = []
        for location in path:
            if location in pos:
                x, y = pos[location]
                path_x.append(x)
                path_y.append(y)
        
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines+markers',
            name=f'Agent {agent_id}',
            line=dict(width=2, dash='dot'),
            marker=dict(size=8)
        ))
    
    # Update layout
    fig.update_layout(
        title='Facility Layout and Agent Movements',
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    return fig

def create_agent_status_cards(simulation_manager) -> None:
    """Create status cards for each healthcare agent"""
    # Get all staff members
    staff = simulation_manager.get_all_staff()
    
    # Create columns for staff cards
    cols = st.columns(3)
    col_idx = 0
    
    for staff_id, staff_member in staff.items():
        with cols[col_idx]:
            st.markdown(f"### {staff_member['name']}")
            st.markdown(f"**Role:** {staff_member['role']}")
            st.markdown(f"**Location:** {staff_member['location']}")
            st.markdown(f"**Status:** {staff_member['status']}")
            
            # Create progress bar for fatigue
            fatigue = staff_member.get('fatigue', 0)
            st.progress(fatigue/100.0, f"Fatigue: {fatigue}%")
            
            # Show current task if any
            if staff_member.get('current_action'):
                st.info(f"Current Task: {staff_member['current_action']}")
            
            st.markdown("---")
        
        # Move to next column
        col_idx = (col_idx + 1) % 3

def create_event_frequency_charts(events: List[Dict]) -> None:
    """Create charts showing event frequency analysis"""
    # Count events by type
    event_types = {}
    for event in events:
        event_type = event.get('type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(event_types.keys()),
            y=list(event_types.values()),
            text=list(event_types.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Event Distribution by Type',
        xaxis_title='Event Type',
        yaxis_title='Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create timeline of events
    times = [event.get('timestamp', datetime.now()) for event in events]
    event_counts = list(range(1, len(events) + 1))
    
    fig = go.Figure(data=[
        go.Scatter(
            x=times,
            y=event_counts,
            mode='lines+markers',
            name='Cumulative Events'
        )
    ])
    
    fig.update_layout(
        title='Event Timeline',
        xaxis_title='Time',
        yaxis_title='Cumulative Event Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_patient_statistics(simulation_manager) -> None:
    """Create visualizations of patient statistics"""
    # Get all patients
    patients = simulation_manager.get_all_patients()
    
    # Count patients by condition
    conditions = {}
    locations = {}
    for patient in patients.values():
        condition = patient.get('condition', 'unknown')
        location = patient.get('location', 'unknown')
        conditions[condition] = conditions.get(condition, 0) + 1
        locations[location] = locations.get(location, 0) + 1
    
    # Create condition distribution chart
    fig = go.Figure(data=[
        go.Pie(
            labels=list(conditions.keys()),
            values=list(conditions.values()),
            hole=.3
        )
    ])
    
    fig.update_layout(
        title='Patient Distribution by Condition',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create location distribution chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(locations.keys()),
            y=list(locations.values()),
            text=list(locations.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Patient Distribution by Location',
        xaxis_title='Location',
        yaxis_title='Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True) 