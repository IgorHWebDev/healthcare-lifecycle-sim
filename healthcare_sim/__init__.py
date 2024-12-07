"""
Healthcare Simulation Package

A comprehensive healthcare simulation system that models the entire patient lifecycle
from pre-conception to post-mortem, including genetic material tracking, biometric data,
and AI-assisted healthcare management.
"""

from .lifecycle.lifecycle_manager import LifecycleStage, LifecycleManager
from .visualization.lifecycle_viz import display_lifecycle_dashboard
from .intelligence.ai_integration import AIModelManager
from .simulation_manager import SimulationManager

__version__ = "0.1.0"
__author__ = "Healthcare Sim Team"

__all__ = [
    'LifecycleStage',
    'LifecycleManager',
    'display_lifecycle_dashboard',
    'AIModelManager',
    'SimulationManager'
] 