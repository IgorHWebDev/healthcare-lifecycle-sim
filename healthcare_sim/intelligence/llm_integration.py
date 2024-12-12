from typing import Dict, Any, Optional
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.text_generation_api import TextGenerationAPI

class LLMIntegration:
    def __init__(self, api_url: Optional[str] = None):
        """Initialize LLM integration with text-generation-webui.
        
        Args:
            api_url: URL of the text-generation-webui instance
        """
        self.api_url = api_url or os.getenv('TEXT_GENERATION_API_URL', 'http://localhost:7860')
        self.api_client = TextGenerationAPI(base_url=self.api_url)
        
    def generate_agent_response(self, 
                              context: str,
                              role: str,
                              task: str,
                              max_tokens: int = 250) -> str:
        """Generate a response for an agent based on context and role.
        
        Args:
            context: Current situation and relevant information
            role: The role of the agent (e.g., "doctor", "nurse")
            task: The specific task or decision needed
            max_tokens: Maximum length of the response
            
        Returns:
            Generated response from the LLM
        """
        prompt = f"""As a {role} in a healthcare setting, given the following context:

{context}

Task: {task}

Provide a professional response that demonstrates medical expertise and follows healthcare best practices.

Response:"""
        
        try:
            response = self.api_client.generate(
                prompt=prompt,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                stop=["\n\n", "Human:", "Assistant:"]
            )
            text = response.get('results', [{'text': ''}])[0].get('text', '')
            if isinstance(text, dict):
                text = text.get('response', '')
            return str(text).strip()
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"[Error generating response: {str(e)}]"
            
    def analyze_medical_situation(self,
                                patient_data: Dict[str, Any],
                                current_state: str,
                                query: str) -> str:
        """Analyze a medical situation and provide insights.
        
        Args:
            patient_data: Dictionary containing patient information
            current_state: Current state or condition description
            query: Specific question or analysis needed
            
        Returns:
            Analysis and recommendations from the LLM
        """
        prompt = f"""Given the following patient data and current situation:

Patient Information:
{self._format_patient_data(patient_data)}

Current State:
{current_state}

Query: {query}

Provide a detailed medical analysis and recommendations:"""
        
        try:
            response = self.api_client.generate(
                prompt=prompt,
                max_new_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            text = response.get('results', [{'text': ''}])[0].get('text', '')
            if isinstance(text, dict):
                text = text.get('response', '')
            return str(text).strip()
        except Exception as e:
            print(f"Error analyzing situation: {str(e)}")
            return f"[Error analyzing situation: {str(e)}]"
    
    def _format_patient_data(self, data: Dict[str, Any]) -> str:
        """Format patient data for prompt inclusion.
        
        Args:
            data: Dictionary of patient data
            
        Returns:
            Formatted string of patient information
        """
        formatted = []
        for key, value in data.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted) 