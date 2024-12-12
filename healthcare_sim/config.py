import os
from typing import Any, Dict, Optional

# Try to load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available. Using environment variables and Streamlit secrets only.")

class Config:
    """Lazy-loaded configuration"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._load_config()
    
    def _get_secret(self, section: str, key: str, default: Any = None) -> Any:
        """Get a secret from Streamlit secrets or environment variables"""
        try:
            import streamlit as st
            return st.secrets[section][key]
        except:
            env_key = f"{section.upper()}_{key.upper()}"
            return os.getenv(env_key, default)
    
    def _load_config(self):
        """Load all configuration values"""
        # OpenAI Configuration
        self.OPENAI_API_KEY = self._get_secret("openai", "api_key")
        
        # RunPod Configuration
        self.RUNPOD_API_KEY = self._get_secret("runpod", "api_key")
        self.RUNPOD_ENDPOINT_ID = self._get_secret("runpod", "endpoint_id", "rae27bwesqoyty")
        self.RUNPOD_ENDPOINT_URL = self._get_secret(
            "runpod", "endpoint_url", 
            f"https://{self.RUNPOD_ENDPOINT_ID}-8000.proxy.runpod.net"
        )
        self.RUNPOD_MODEL_NAME = self._get_secret(
            "runpod", "model_name", 
            "meta-llama-3.1-70b-instruct-awq-int4"
        )
        
        # vLLM Settings
        self.VLLM_MAX_TOKENS = int(self._get_secret("runpod", "max_total_tokens", 4096))
        self.VLLM_TEMPERATURE = float(self._get_secret("runpod", "temperature", 0.7))
        self.VLLM_TOP_P = float(self._get_secret("runpod", "top_p", 0.9))
        self.VLLM_MAX_CONCURRENT = int(self._get_secret("runpod", "max_concurrent_requests", 2))
        
        # Database Configuration
        self.MIMIC_DATABASE_PATH = self._get_secret(
            "database", "mimic_path", 
            "/mount/src/healthcare-lifecycle-sim/data/mimic"
        )
        
        # Simulation settings
        self.SIMULATION_STEP_DURATION = int(self._get_secret("simulation", "step_duration", 10))
        self.DEBUG_MODE = str(self._get_secret("simulation", "debug_mode", "false")).lower() == "true"
        
        # Default settings
        self.DEFAULT_EMERGENCY_FREQUENCY = self._get_secret(
            "default_settings", "emergency_frequency", "normal"
        )
        self.DEFAULT_SIMULATION_DURATION = int(self._get_secret(
            "default_settings", "simulation_duration", 240
        ))
        self.DEFAULT_SIMULATION_SPEED = float(self._get_secret(
            "default_settings", "simulation_speed", 0.5
        ))
        self.SHOW_AGENT_THOUGHTS = str(self._get_secret(
            "default_settings", "show_agent_thoughts", "true"
        )).lower() == "true"
        
        # Hospital settings
        self.DEPARTMENTS = {
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
        self.FATIGUE_INCREASE_RATE = 0.1
        self.REST_RECOVERY_RATE = 0.2
        self.EMERGENCY_PROBABILITY = 0.05
        
        # RunPod Hardware Monitoring
        self.GPU_MEMORY_THRESHOLD = float(self._get_secret("runpod.monitoring", "gpu_memory_threshold", 0.9))
        self.CPU_THRESHOLD = float(self._get_secret("runpod.monitoring", "cpu_threshold", 0.8))
        self.MEMORY_THRESHOLD = float(self._get_secret("runpod.monitoring", "memory_threshold", 0.8))

# Create a global config instance
config = Config()