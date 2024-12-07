import os
import streamlit as st
from pathlib import Path

# Add the parent directory to Python path for relative imports
import sys
sys.path.append(str(Path(__file__).parent))

# Initialize Streamlit configuration
def init_streamlit():
    st.set_page_config(
        page_title="Healthcare Simulation",
        page_icon="🏥",
        layout="wide"
    )
    
    # Initialize session state if needed
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.events = []
        st.session_state.start_time = None
        st.session_state.is_running = False
        st.session_state.is_paused = False
        st.session_state.agent_paths = {}
        st.session_state.simulation_speed = 1.0
        st.session_state.time_scale = "minutes"
        st.session_state.auto_events = True
        st.session_state.risk_level = "normal"
        st.session_state.selected_patient = None 