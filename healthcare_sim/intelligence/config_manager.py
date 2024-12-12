import os
from typing import Dict, Any
import streamlit as st
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

class LLMConfig(BaseModel):
    """LLM configuration settings"""
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field("gpt-4", description="OpenAI model name")
    openai_temperature: float = Field(0.7, description="OpenAI temperature")
    openai_max_tokens: int = Field(1000, description="OpenAI max tokens")
    
    runpod_api_key: str = Field(..., description="RunPod API key")
    runpod_endpoint_id: str = Field(..., description="RunPod endpoint ID")
    runpod_model_name: str = Field("llama2-70b", description="RunPod model name")
    runpod_batch_size: int = Field(4, description="RunPod batch size")
    runpod_max_length: int = Field(2000, description="RunPod max length")
    runpod_temperature: float = Field(0.7, description="RunPod temperature")
    runpod_top_p: float = Field(0.9, description="RunPod top p")
    
    scenario_interval: int = Field(300, description="Scenario generation interval in seconds")
    analysis_interval: int = Field(3600, description="Trend analysis interval in seconds")
    max_context_length: int = Field(4000, description="Maximum context length")
    memory_window: int = Field(24, description="Memory window in hours")
    confidence_threshold: float = Field(0.85, description="Confidence threshold")
    fallback_to_rules: bool = Field(True, description="Fallback to rules-based system")

class ConfigManager:
    """Manages LLM configuration settings"""
    
    def __init__(self):
        """Initialize configuration manager"""
        self.config = self._load_config()
        
    def _load_config(self) -> LLMConfig:
        """Load configuration from Streamlit secrets"""
        try:
            return LLMConfig(
                openai_api_key=st.secrets["openai"]["api_key"],
                openai_model=st.secrets["openai"]["model"],
                openai_temperature=st.secrets["openai"]["temperature"],
                openai_max_tokens=st.secrets["openai"]["max_tokens"],
                
                runpod_api_key=st.secrets["runpod"]["api_key"],
                runpod_endpoint_id=st.secrets["runpod"]["endpoint_id"],
                runpod_model_name=st.secrets["runpod"]["model_name"],
                runpod_batch_size=st.secrets["runpod"]["batch_size"],
                runpod_max_length=st.secrets["runpod"]["max_length"],
                runpod_temperature=st.secrets["runpod"]["temperature"],
                runpod_top_p=st.secrets["runpod"]["top_p"],
                
                scenario_interval=st.secrets["llm"]["scenario_generation_interval"],
                analysis_interval=st.secrets["llm"]["trend_analysis_interval"],
                max_context_length=st.secrets["llm"]["max_context_length"],
                memory_window=st.secrets["llm"]["memory_window"],
                confidence_threshold=st.secrets["llm"]["confidence_threshold"],
                fallback_to_rules=st.secrets["llm"]["fallback_to_rules"]
            )
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Return default configuration
            return LLMConfig(
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
                runpod_api_key=os.getenv("RUNPOD_API_KEY", ""),
                runpod_endpoint_id=os.getenv("RUNPOD_ENDPOINT_ID", "")
            )
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return {
            "api_key": self.config.openai_api_key,
            "model": self.config.openai_model,
            "temperature": self.config.openai_temperature,
            "max_tokens": self.config.openai_max_tokens
        }
    
    def get_runpod_config(self) -> Dict[str, Any]:
        """Get RunPod configuration"""
        return {
            "api_key": self.config.runpod_api_key,
            "endpoint_id": self.config.runpod_endpoint_id,
            "model_name": self.config.runpod_model_name,
            "batch_size": self.config.runpod_batch_size,
            "max_length": self.config.runpod_max_length,
            "temperature": self.config.runpod_temperature,
            "top_p": self.config.runpod_top_p
        }
    
    def get_llm_settings(self) -> Dict[str, Any]:
        """Get LLM settings"""
        return {
            "scenario_interval": self.config.scenario_interval,
            "analysis_interval": self.config.analysis_interval,
            "max_context_length": self.config.max_context_length,
            "memory_window": self.config.memory_window,
            "confidence_threshold": self.config.confidence_threshold,
            "fallback_to_rules": self.config.fallback_to_rules
        }
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        return (
            bool(self.config.openai_api_key) and
            bool(self.config.runpod_api_key) and
            bool(self.config.runpod_endpoint_id)
        ) 

@dataclass
class VLLMConfig:
    """vLLM deployment configuration"""
    model_name: str = "hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4"
    tensor_parallel_size: int = 4
    gpu_memory_utilization: float = 0.85
    max_num_batched_tokens: int = 512
    quantization: str = "awq"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Advanced settings
    max_num_seqs: int = 128
    trust_remote_code: bool = True
    disable_custom_all_reduce: bool = True
    worker_use_ray: bool = False
    
    # Healthcare specific settings
    max_response_time_seconds: int = 30
    enable_medical_validation: bool = True
    compliance_mode: str = "HIPAA"

class DeploymentManager:
    def __init__(self, config: Optional[VLLMConfig] = None):
        """Initialize deployment manager"""
        self.config = config or VLLMConfig()
        self.health_check_enabled = True
        
    def generate_deployment_config(self) -> Dict[str, Any]:
        """Generate deployment configuration for RunPod"""
        return {
            "container_config": {
                "image": "vllm/vllm-openai:latest",
                "ports": [self.config.port],
                "env": self._get_environment_variables(),
                "command": self._get_start_command()
            },
            "resource_config": {
                "gpu_count": self.config.tensor_parallel_size,
                "gpu_memory_utilization": self.config.gpu_memory_utilization,
                "cpu_count": 8,
                "memory": "32GB"
            },
            "network_config": {
                "ports": [
                    {"port": self.config.port, "protocol": "http"}
                ]
            },
            "health_check": {
                "enabled": self.health_check_enabled,
                "endpoint": f"http://localhost:{self.config.port}/health",
                "interval": 30,
                "timeout": 10,
                "retries": 3
            }
        }
    
    def _get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for deployment"""
        return {
            "MODEL_NAME": self.config.model_name,
            "TENSOR_PARALLEL_SIZE": str(self.config.tensor_parallel_size),
            "GPU_MEMORY_UTILIZATION": str(self.config.gpu_memory_utilization),
            "MAX_NUM_BATCHED_TOKENS": str(self.config.max_num_batched_tokens),
            "QUANTIZATION": self.config.quantization,
            "MAX_NUM_SEQS": str(self.config.max_num_seqs),
            "COMPLIANCE_MODE": self.config.compliance_mode,
            "CUDA_VISIBLE_DEVICES": ",".join(map(str, range(self.config.tensor_parallel_size)))
        }
    
    def _get_start_command(self) -> str:
        """Get container start command"""
        return (
            "python -m vllm.entrypoints.openai.api_server "
            f"--model {self.config.model_name} "
            f"--tensor-parallel-size {self.config.tensor_parallel_size} "
            f"--gpu-memory-utilization {self.config.gpu_memory_utilization} "
            f"--max-num-batched-tokens {self.config.max_num_batched_tokens} "
            f"--quantization {self.config.quantization} "
            f"--host {self.config.host} "
            f"--port {self.config.port}"
        )
    
    def validate_deployment(self) -> bool:
        """Validate deployment configuration"""
        try:
            # Check GPU requirements
            if self.config.tensor_parallel_size < 1:
                logger.error("Invalid tensor parallel size")
                return False
                
            # Validate memory settings
            if not (0.0 < self.config.gpu_memory_utilization <= 1.0):
                logger.error("Invalid GPU memory utilization")
                return False
                
            # Check healthcare compliance
            if self.config.compliance_mode not in ["HIPAA", "GDPR", "None"]:
                logger.error("Invalid compliance mode")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def save_config(self, filepath: str):
        """Save configuration to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.generate_deployment_config(), f, indent=2)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def load_config(self, filepath: str):
        """Load configuration from file"""
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            # Update configuration
            env_vars = config_data["container_config"]["env"]
            self.config = VLLMConfig(
                model_name=env_vars.get("MODEL_NAME", self.config.model_name),
                tensor_parallel_size=int(env_vars.get("TENSOR_PARALLEL_SIZE", self.config.tensor_parallel_size)),
                gpu_memory_utilization=float(env_vars.get("GPU_MEMORY_UTILIZATION", self.config.gpu_memory_utilization)),
                max_num_batched_tokens=int(env_vars.get("MAX_NUM_BATCHED_TOKENS", self.config.max_num_batched_tokens)),
                quantization=env_vars.get("QUANTIZATION", self.config.quantization),
                compliance_mode=env_vars.get("COMPLIANCE_MODE", self.config.compliance_mode)
            )
            logger.info(f"Configuration loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")