import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Configuration with fallback to environment variables
OPENAI_API_KEY = st.secrets["openai"]["api_key"] if "openai" in st.secrets else os.getenv('OPENAI_API_KEY')
MIMIC_DATABASE_PATH = st.secrets["database"]["mimic_path"] if "database" in st.secrets else os.getenv('MIMIC_DATABASE_PATH')

# Simulation settings
SIMULATION_STEP_DURATION = int(st.secrets["simulation"]["step_duration"] if "simulation" in st.secrets else os.getenv('SIMULATION_STEP_DURATION', 10))
DEBUG_MODE = st.secrets["simulation"]["debug_mode"] if "simulation" in st.secrets else os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Default settings
DEFAULT_EMERGENCY_FREQUENCY = st.secrets["default_settings"]["emergency_frequency"] if "default_settings" in st.secrets else "normal"
DEFAULT_SIMULATION_DURATION = int(st.secrets["default_settings"]["simulation_duration"] if "default_settings" in st.secrets else 240)
DEFAULT_SIMULATION_SPEED = float(st.secrets["default_settings"]["simulation_speed"] if "default_settings" in st.secrets else 0.5)
SHOW_AGENT_THOUGHTS = st.secrets["default_settings"]["show_agent_thoughts"] if "default_settings" in st.secrets else True

# Hospital settings
DEPARTMENTS = {
    'ER': {
        'capacity': 15,
        'min_staff': 2,
        'equipment': ['ventilator', 'defibrillator', 'monitoring_system']
    },
    'ICU': {
        'capacity': 10,
        'min_staff': 3,
        'equipment': ['ventilator', 'ecmo', 'dialysis_machine']
    },
    'WARD': {
        'capacity': 20,
        'min_staff': 1,
        'equipment': ['basic_monitoring']
    }
}

# Agent behavior settings
FATIGUE_INCREASE_RATE = 0.1
REST_RECOVERY_RATE = 0.2
EMERGENCY_PROBABILITY = 0.05 