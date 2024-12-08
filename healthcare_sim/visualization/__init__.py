"""Visualization module for healthcare simulation"""

from typing import Dict, List, Optional, Any, Union
import streamlit as st

# Define a type alias for Figure to avoid direct import
try:
    from matplotlib.figure import Figure
except ImportError:
    Figure = Any  # type: ignore

# Import visualization functions with error handling
try:
    from .facility_viz import (
        create_agent_path_visualization,
        create_agent_status_cards,
        create_event_frequency_charts,
        create_patient_statistics
    )
except ImportError as e:
    print(f"Error importing visualization components: {e}")
    
    def create_agent_path_visualization(*args: Any, **kwargs: Any) -> Optional[Any]:
        st.warning("Visualization components not available")
        return None
    
    def create_agent_status_cards(*args: Any, **kwargs: Any) -> None:
        st.warning("Visualization components not available")
    
    def create_event_frequency_charts(*args: Any, **kwargs: Any) -> None:
        st.warning("Visualization components not available")
    
    def create_patient_statistics(*args: Any, **kwargs: Any) -> None:
        st.warning("Visualization components not available")

try:
    from .lifecycle_viz import (
        create_lifecycle_timeline,
        create_stage_distribution,
        create_genetic_timeline,
        display_lifecycle_dashboard
    )
except ImportError as e:
    print(f"Error importing lifecycle visualization components: {e}")
    
    def create_lifecycle_timeline(*args: Any, **kwargs: Any) -> Optional[Any]:
        st.warning("Lifecycle visualization components not available")
        return None
    
    def create_stage_distribution(*args: Any, **kwargs: Any) -> Optional[Any]:
        st.warning("Lifecycle visualization components not available")
        return None
    
    def create_genetic_timeline(*args: Any, **kwargs: Any) -> Optional[Any]:
        st.warning("Lifecycle visualization components not available")
        return None
    
    def display_lifecycle_dashboard(*args: Any, **kwargs: Any) -> None:
        st.warning("Lifecycle visualization components not available")

__all__ = [
    'create_agent_path_visualization',
    'create_agent_status_cards',
    'create_event_frequency_charts',
    'create_patient_statistics',
    'create_lifecycle_timeline',
    'create_stage_distribution',
    'create_genetic_timeline',
    'display_lifecycle_dashboard'
] 