import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import OpenAI, but don't fail if it's not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI package not available. Using mock responses.")
    OPENAI_AVAILABLE = False

class AgentBrain:
    def __init__(self):
        """Initialize the agent brain with OpenAI integration if available"""
        self.openai_available = OPENAI_AVAILABLE
        if self.openai_available:
            try:
                # Try to get API key from Streamlit secrets first
                import streamlit as st
                self.api_key = st.secrets["openai"]["api_key"]
            except Exception:
                # Fall back to environment variable
                self.api_key = os.getenv("OPENAI_API_KEY")
            
            if self.api_key:
                openai.api_key = self.api_key
            else:
                print("OpenAI API key not found. Using mock responses.")
                self.openai_available = False
    
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using OpenAI or fallback to mock"""
        if not self.openai_available:
            return self._generate_mock_response(prompt)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a healthcare professional."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response when OpenAI is not available"""
        return f"Mock response for: {prompt}\nThis is a simulated healthcare response."