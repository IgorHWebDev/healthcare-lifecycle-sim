import streamlit as st
from typing import Dict, List, Optional

# Try to import visualization dependencies
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    print("Visualization packages not available. Using simplified visualization.")
    VISUALIZATION_AVAILABLE = False

def create_agent_path_visualization(agent_paths: Dict[str, List[str]]) -> Optional[plt.Figure]:
    """Create a visualization of agent paths through the facility"""
    if not VISUALIZATION_AVAILABLE:
        st.warning("Advanced visualization not available. Please install networkx and matplotlib.")
        return None
    
    try:
        G = nx.Graph()
        
        # Add nodes and edges from paths
        for agent_id, path in agent_paths.items():
            for i in range(len(path) - 1):
                G.add_edge(path[i], path[i + 1])
        
        # Create layout
        pos = nx.spring_layout(G)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Draw network
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
               node_size=1500, font_size=10, font_weight='bold',
               ax=ax)
        
        return fig
    except Exception as e:
        st.error(f"Error creating path visualization: {e}")
        return None

def create_agent_status_cards(agents_data: Dict[str, Dict]) -> None:
    """Create status cards for agents"""
    if not agents_data:
        st.info("No agent data available")
        return
    
    cols = st.columns(3)
    for i, (agent_id, data) in enumerate(agents_data.items()):
        with cols[i % 3]:
            st.markdown(f"### 👤 Agent {agent_id}")
            st.metric("Location", data.get("location", "Unknown"))
            st.metric("Status", data.get("status", "Unknown"))
            st.progress(1 - float(data.get("fatigue", 0)))

def create_event_frequency_charts(events: List[Dict]) -> None:
    """Create charts showing event frequencies"""
    if not events:
        st.info("No event data available")
        return
    
    try:
        import pandas as pd
        
        # Convert events to DataFrame
        df = pd.DataFrame(events)
        
        # Event types distribution
        st.subheader("Event Type Distribution")
        event_counts = df["type"].value_counts()
        st.bar_chart(event_counts)
        
        # Time-based distribution
        st.subheader("Events Over Time")
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        hourly_counts = df["hour"].value_counts().sort_index()
        st.line_chart(hourly_counts)
        
    except Exception as e:
        st.error(f"Error creating event charts: {e}")

def create_patient_statistics(patient_data: List[Dict]) -> None:
    """Create patient statistics visualization"""
    if not patient_data:
        st.info("No patient data available")
        return
    
    try:
        # Basic statistics
        total_patients = len(patient_data)
        avg_stay = sum(p.get("stay_duration", 0) for p in patient_data) / total_patients
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patients", total_patients)
        with col2:
            st.metric("Average Stay (hours)", f"{avg_stay:.1f}")
        with col3:
            st.metric("Occupancy Rate", f"{(total_patients / 50 * 100):.1f}%")
        
        # Department distribution
        dept_counts = {}
        for p in patient_data:
            dept = p.get("department", "Unknown")
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        st.subheader("Patient Distribution by Department")
        st.bar_chart(dept_counts)
        
    except Exception as e:
        st.error(f"Error creating patient statistics: {e}") 