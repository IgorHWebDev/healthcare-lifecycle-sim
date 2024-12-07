import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MIMIC_DATABASE_PATH = os.getenv('MIMIC_DATABASE_PATH', "/Users/igor/Downloads/mimic-iv-clinical-database-demo-2.2")

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Store your API key in .env file

# Simulation settings
SIMULATION_STEP_DURATION = 10  # seconds
MAX_MEMORY_COUNT = 100
REFLECTION_THRESHOLD = 5

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