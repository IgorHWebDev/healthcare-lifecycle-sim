import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.llm_integration import LLMIntegration

def test_connection():
    # Initialize LLM integration with the configured URL
    llm = LLMIntegration()
    
    print("Testing LLM Integration...")
    print(f"Using API URL: {llm.api_url}")
    
    # Test simple agent response
    test_context = "Patient presents with chest pain, shortness of breath, and sweating."
    test_role = "emergency physician"
    test_task = "Assess the situation and provide initial recommendations."
    
    print("\nTesting agent response generation...")
    try:
        response = llm.generate_agent_response(
            context=test_context,
            role=test_role,
            task=test_task
        )
        print("\nResponse received:")
        print(response)
    except Exception as e:
        print(f"\nError testing agent response: {str(e)}")
    
    # Test medical situation analysis
    test_patient_data = {
        "age": 65,
        "gender": "male",
        "symptoms": ["chest pain", "shortness of breath", "sweating"],
        "vital_signs": {
            "blood_pressure": "160/95",
            "heart_rate": 110,
            "oxygen_saturation": 94
        }
    }
    test_current_state = "Patient arrived in ER 10 minutes ago with acute symptoms."
    test_query = "Evaluate likelihood of acute cardiac event and recommend immediate actions."
    
    print("\nTesting medical situation analysis...")
    try:
        analysis = llm.analyze_medical_situation(
            patient_data=test_patient_data,
            current_state=test_current_state,
            query=test_query
        )
        print("\nAnalysis received:")
        print(analysis)
    except Exception as e:
        print(f"\nError testing medical analysis: {str(e)}")

if __name__ == "__main__":
    test_connection() 