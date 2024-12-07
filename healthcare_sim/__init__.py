"""
Healthcare Simulation Package

A comprehensive healthcare simulation system that models the entire patient lifecycle
from pre-conception to post-mortem, including genetic material tracking, biometric data,
and AI-assisted healthcare management.
"""

import os
import sys
from pathlib import Path

# Add the package root to Python path
package_root = str(Path(__file__).parent)
if package_root not in sys.path:
    sys.path.insert(0, package_root)

# Import main components
from .simulation_manager import SimulationManager
from .lifecycle.lifecycle_manager import LifecycleStage, LifecycleManager
from .intelligence.ai_integration import AIModelManager

__version__ = "0.1.0"
__author__ = "Healthcare Sim Team"

__all__ = [
    'SimulationManager',
    'LifecycleStage',
    'LifecycleManager',
    'AIModelManager'
] 