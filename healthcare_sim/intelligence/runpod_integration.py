import os
import runpod
import asyncio
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    VLLM = "vllm"
    TGI = "tgi"

@dataclass
class SecurityConfig:
    """Security and compliance configuration"""
    encrypt_data: bool = True
    audit_logging: bool = True
    data_retention_days: int = 30
    compliance_mode: str = "HIPAA"  # HIPAA, GDPR, etc.

class RunPodLLM:
    def __init__(self, 
        api_key: str, 
        endpoint_id: str,
        template_id: str,
        model_name: str,
        security_config: Optional[SecurityConfig] = None
    ):
        """Initialize RunPod LLM integration with enhanced security
        
        Args:
            api_key: RunPod API key
            endpoint_id: RunPod endpoint ID
            template_id: Docker template ID (TGI or vLLM)
            model_name: Model name/version
            security_config: Security and compliance settings
        """
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.template_id = template_id
        self.model_name = model_name
        self.model_type = ModelType.VLLM if "vllm" in template_id.lower() else ModelType.TGI
        self.security_config = security_config or SecurityConfig()
        
        # Initialize RunPod
        runpod.api_key = api_key
        
        # Setup monitoring
        self.request_count = 0
        self.error_count = 0
        self.last_error = None
        
        logger.info(f"Initialized RunPodLLM with model {model_name} using {self.model_type.value}")

    async def generate_scenario(self, 
        current_state: Dict[str, Any],
        patient_history: List[Dict],
        department_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate new healthcare scenarios with enhanced monitoring"""
        self.request_count += 1
        
        try:
            # Sanitize and encrypt sensitive data if configured
            if self.security_config.encrypt_data:
                current_state = self._sanitize_data(current_state)
                patient_history = self._sanitize_data(patient_history)
            
            prompt = self._build_scenario_prompt(
                current_state,
                patient_history,
                department_stats
            )
            
            start_time = datetime.now()
            if self.model_type == ModelType.VLLM:
                response = await self._vllm_generate(prompt, max_tokens=4000)
            else:
                response = await self._tgi_generate(prompt, max_tokens=4000)
            
            # Log performance metrics
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Scenario generation completed in {duration}s")
            
            result = self._parse_scenario_response(response)
            
            # Audit logging
            if self.security_config.audit_logging:
                self._log_audit_event("scenario_generation", {
                    "duration": duration,
                    "tokens_generated": len(str(result)) // 4,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Scenario generation failed: {e}")
            
            if self.security_config.audit_logging:
                self._log_audit_event("scenario_generation_error", {
                    "error": str(e),
                    "error_count": self.error_count
                })
            
            return {
                "events": [],
                "required_actions": [],
                "risk_factors": [],
                "error": str(e)
            }

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data before processing"""
        # Implementation of data sanitization logic
        # Remove PII, encrypt sensitive fields, etc.
        return data

    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit events for compliance"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "model": self.model_name,
            "details": details,
            "compliance_mode": self.security_config.compliance_mode
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health and performance metrics"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "last_error": self.last_error,
            "model_type": self.model_type.value,
            "model_name": self.model_name
        }

    async def analyze_trends(self,
        historical_data: List[Dict],
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """Analyze historical data for trends and patterns"""
        prompt = self._build_analysis_prompt(historical_data, timeframe)
        
        try:
            if self.model_type == ModelType.VLLM:
                response = await self._vllm_generate(prompt, max_tokens=8000)
            else:
                response = await self._tgi_generate(prompt, max_tokens=8000)
            
            return self._parse_analysis_response(response)
        except Exception as e:
            print(f"RunPod analysis error: {e}")
            return {
                "trends": [],
                "patterns": [],
                "risks": [],
                "recommendations": [],
                "error": str(e)
            }
    
    async def _vllm_generate(self, prompt: str, max_tokens: int = 4000) -> Dict:
        """Generate text using vLLM template"""
        return await runpod.async_run(
            endpoint_id=self.endpoint_id,
            input={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": True,
                "model": self.model_name
            }
        )
    
    async def _tgi_generate(self, prompt: str, max_tokens: int = 4000) -> Dict:
        """Generate text using TGI template"""
        return await runpod.async_run(
            endpoint_id=self.endpoint_id,
            input={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
        )
        
    def _build_scenario_prompt(self,
        current_state: Dict[str, Any],
        patient_history: List[Dict],
        department_stats: Dict[str, Any]
    ) -> str:
        """Build prompt for scenario generation"""
        system_prompt = """You are an advanced medical AI assistant generating realistic healthcare scenarios. 
        Focus on creating medically accurate and detailed patient events, considering current hospital state and history."""
        
        return f"""{system_prompt}

        Given the current healthcare simulation state:
        
        Current Time: {datetime.now().isoformat()}
        
        Department Statistics:
        {json.dumps(department_stats, indent=2)}
        
        Current State:
        {json.dumps(current_state, indent=2)}
        
        Recent Patient History:
        {json.dumps(patient_history[-5:], indent=2)}
        
        Generate a realistic healthcare scenario including:
        1. Patient events and status changes
        2. Department resource updates
        3. Staff interactions
        4. Emergency situations if appropriate
        5. Required vital sign changes
        
        Format the response as JSON with the following structure:
        {
            "events": [
                {
                    "type": "patient_update|department_update|emergency",
                    "details": {...},
                    "priority": 1-5
                }
            ],
            "required_actions": [...],
            "risk_factors": [...]
        }
        """
        
    def _build_analysis_prompt(self,
        historical_data: List[Dict],
        timeframe: str
    ) -> str:
        """Build prompt for trend analysis"""
        system_prompt = """You are an advanced medical AI assistant analyzing healthcare data patterns.
        Focus on identifying clinically significant trends and providing actionable insights."""
        
        return f"""{system_prompt}

        Analyze the following healthcare simulation data for the past {timeframe}:
        
        Historical Data:
        {json.dumps(historical_data, indent=2)}
        
        Identify:
        1. Patient flow patterns
        2. Resource utilization trends
        3. Risk factors and correlations
        4. Efficiency opportunities
        5. Potential bottlenecks
        
        Format the response as JSON with the following structure:
        {
            "trends": [...],
            "patterns": [...],
            "risks": [...],
            "recommendations": [...]
        }
        """
            
    def _parse_scenario_response(self, response: Dict) -> Dict[str, Any]:
        """Parse and validate scenario generation response"""
        try:
            if self.model_type == ModelType.VLLM:
                output = response.get('output', '')
                if isinstance(output, str):
                    return json.loads(output)
                return output
            else:
                generated_text = response.get('generated_text', '')
                if isinstance(generated_text, str):
                    return json.loads(generated_text)
                return generated_text
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"Error parsing response: {e}")
            return {
                "events": [],
                "required_actions": [],
                "risk_factors": [],
                "error": f"Failed to parse response: {str(e)}"
            }
            
    def _parse_analysis_response(self, response: Dict) -> Dict[str, Any]:
        """Parse and validate trend analysis response"""
        try:
            if self.model_type == ModelType.VLLM:
                output = response.get('output', '')
                if isinstance(output, str):
                    return json.loads(output)
                return output
            else:
                generated_text = response.get('generated_text', '')
                if isinstance(generated_text, str):
                    return json.loads(generated_text)
                return generated_text
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"Error parsing response: {e}")
            return {
                "trends": [],
                "patterns": [],
                "risks": [],
                "recommendations": [],
                "error": f"Failed to parse response: {str(e)}"
            }