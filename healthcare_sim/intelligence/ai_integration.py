from typing import Dict, List, Optional
import random

class AIModelManager:
    def __init__(self):
        """Initialize AI model manager"""
        self.response_history = []
        
    def generate_response(self,
                         prompt: str,
                         model_type: str = "general",
                         temperature: float = 0.7,
                         generate_alternatives: bool = False) -> Dict:
        """Generate AI response (simplified mock version)"""
        response = {
            "primary_response": "This is a mock AI response",
            "confidence_score": random.random(),
            "reasoning": ["Reason 1", "Reason 2"],
            "alternatives": ["Alternative 1", "Alternative 2"] if generate_alternatives else [],
            "risks": ["Risk 1", "Risk 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
        
        self.response_history.append({
            "timestamp": "2023-12-07",
            "model": model_type,
            "prompt": prompt,
            "response": response,
            "decision_process": {
                "context_analysis": {"context": "test"},
                "confidence_factors": {"factor1": 0.8}
            },
            "structured_output": response
        })
        
        return response
    
    def get_response_history(self) -> List[Dict]:
        """Get history of AI responses"""
        return self.response_history
    
    def get_staff_avatar(self, role: str) -> str:
        """Get avatar for staff role"""
        return "👨‍⚕️"
    
    def get_patient_avatar(self, condition: str) -> str:
        """Get avatar for patient condition"""
        return "🏥"