import os
import streamlit as st

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available. Using environment variables and Streamlit secrets only.")

# Configuration with fallback to environment variables
def get_secret(section: str, key: str, default=None):
    """Get a secret from Streamlit secrets or environment variables"""
    try:
        return st.secrets[section][key]
    except:
        env_key = f"{section.upper()}_{key.upper()}"
        return os.getenv(env_key, default)

# OpenAI Configuration
OPENAI_API_KEY = get_secret("openai", "api_key")

# Database Configuration
MIMIC_DATABASE_PATH = get_secret("database", "mimic_path", "/mount/src/healthcare-lifecycle-sim/data/mimic")

# Simulation settings
SIMULATION_STEP_DURATION = int(get_secret("simulation", "step_duration", 10))
DEBUG_MODE = get_secret("simulation", "debug_mode", "false").lower() == "true"

# Default settings
DEFAULT_EMERGENCY_FREQUENCY = get_secret("default_settings", "emergency_frequency", "normal")
DEFAULT_SIMULATION_DURATION = int(get_secret("default_settings", "simulation_duration", 240))
DEFAULT_SIMULATION_SPEED = float(get_secret("default_settings", "simulation_speed", 0.5))
SHOW_AGENT_THOUGHTS = get_secret("default_settings", "show_agent_thoughts", "true").lower() == "true"

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