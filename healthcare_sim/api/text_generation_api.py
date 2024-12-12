import requests
import json
from typing import Dict, Any, Optional

class TextGenerationAPI:
    def __init__(self, base_url: str = "http://localhost:7860"):
        """Initialize the API client for text-generation-webui.
        
        Args:
            base_url: The base URL of the text-generation-webui instance
        """
        self.base_url = base_url.rstrip('/')
        
    def generate(self, 
                prompt: str,
                max_new_tokens: int = 250,
                temperature: float = 0.7,
                top_p: float = 0.9,
                stop: Optional[list] = None) -> Dict[str, Any]:
        """Generate text using the loaded model.
        
        Args:
            prompt: The input prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: List of strings that will stop generation if encountered
            
        Returns:
            Dict containing the generated text and other metadata
        """
        endpoint = f"{self.base_url}/run/predict"
        
        payload = {
            "data": [
                prompt  # Simple prompt-only format
            ]
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            return {"results": [{"text": result.get("data", [""])[0]}]}
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to text-generation-webui: {str(e)}")
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model.
        
        Returns:
            Dict containing model information
        """
        endpoint = f"{self.base_url}/run/predict"
        
        payload = {
            "data": ["Model information:"]
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get model info: {str(e)}") 