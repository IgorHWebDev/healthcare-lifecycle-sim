import asyncio
from typing import Dict, List, Optional
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

class HealthcareModelManager:
    def __init__(self, runpod_endpoint: str):
        """Initialize the healthcare model manager with RunPod-hosted model."""
        # Configure API settings for RunPod TextGen WebUI
        self.config = {
            "api_type": "open_ai",
            "api_base": f"https://{runpod_endpoint}-50001.proxy.runpod.net/v1",
            "api_key": "sk-111111111111111111111111111111111111111111111111",  # Dummy key for TextGen WebUI
            "model": "cognitivecomputations_dolphin-2.7-mixtral-8x7b"
        }
        
        # Initialize the model client
        self.model_client = OpenAIChatCompletionClient(
            model=self.config["model"],
            api_key=self.config["api_key"],
            base_url=self.config["api_base"]
        )
        
        # Create specialized healthcare agents
        self.diagnosis_agent = AssistantAgent(
            name="diagnosis_expert",
            model_client=self.model_client,
            system_message="""You are an expert in medical diagnosis. 
            Analyze patient symptoms and medical history to suggest potential diagnoses.
            Always consider multiple possibilities and list them in order of likelihood.
            Format your responses with clear sections:
            - Diagnosis: [your diagnosis]
            - Confidence: [confidence level]
            - Supporting Evidence: [evidence]"""
        )
        
        self.treatment_agent = AssistantAgent(
            name="treatment_planner",
            model_client=self.model_client,
            system_message="""You are an expert in treatment planning.
            Based on diagnoses, create comprehensive treatment plans considering:
            - Medications and dosages
            - Therapy recommendations
            - Lifestyle modifications
            - Follow-up schedule
            Format your responses with clear sections:
            - Treatment Plan: [detailed plan]
            - Duration: [timeframe]
            - Expected Outcomes: [outcomes]"""
        )
        
        self.research_agent = AssistantAgent(
            name="medical_researcher",
            model_client=self.model_client,
            system_message="""You are a medical research expert.
            Provide evidence-based information from recent medical literature.
            Include references to studies and guidelines when possible.
            Format your responses with clear sections:
            - Research Finding: [finding]
            - Source: [source]
            - Relevance: [relevance to case]"""
        )
        
        # Create a user proxy for interaction
        self.user_proxy = UserProxyAgent(
            name="healthcare_coordinator",
            system_message="""You are a healthcare coordinator.
            Your role is to:
            1. Gather relevant patient information
            2. Coordinate between different medical experts
            3. Summarize findings and recommendations
            4. Ensure all necessary follow-ups are scheduled
            Format your responses with clear sections:
            - Summary: [case summary]
            - Action Items: [actions]
            - Follow-up: [follow-up plan]"""
        )
        
    async def analyze_patient_case(self, patient_data: Dict) -> Dict:
        """Analyze a patient case using the team of medical agents."""
        # Create a team of agents
        medical_team = RoundRobinGroupChat(
            agents=[
                self.diagnosis_agent,
                self.treatment_agent,
                self.research_agent,
                self.user_proxy
            ],
            termination_condition=TextMentionTermination("ANALYSIS_COMPLETE")
        )
        
        # Format patient data for analysis
        task = f"""
        Patient Case Analysis Request:
        
        Demographics:
        - Age: {patient_data.get('age')}
        - Gender: {patient_data.get('gender')}
        - Medical History: {patient_data.get('medical_history')}
        
        Current Symptoms:
        {patient_data.get('symptoms')}
        
        Recent Tests:
        {patient_data.get('recent_tests')}
        
        Please analyze this case and provide:
        1. Potential diagnoses
        2. Recommended treatment plan
        3. Relevant research findings
        4. Follow-up recommendations
        
        Each expert should focus on their specialty and format responses according to their system message.
        Conclude with ANALYSIS_COMPLETE when finished.
        """
        
        # Run the analysis
        stream = medical_team.run_stream(task=task)
        
        # Process and collect results
        results = {
            'diagnoses': [],
            'treatment_plan': [],
            'research_findings': [],
            'followup': []
        }
        
        async for message in stream:
            if message.content:
                if "Diagnosis:" in message.content:
                    results['diagnoses'].append(message.content)
                elif "Treatment Plan:" in message.content:
                    results['treatment_plan'].append(message.content)
                elif "Research Finding:" in message.content:
                    results['research_findings'].append(message.content)
                elif "Follow-up:" in message.content:
                    results['followup'].append(message.content)
        
        return results

# Example usage:
async def main():
    # Initialize the manager with your RunPod endpoint
    manager = HealthcareModelManager(
        runpod_endpoint="cloqf29gtp9t1h-7860"  # Your RunPod endpoint
    )
    
    # Example patient data
    patient_data = {
        'age': 45,
        'gender': 'F',
        'medical_history': 'Hypertension, Type 2 Diabetes',
        'symptoms': 'Persistent headache, blurred vision, fatigue',
        'recent_tests': 'Blood pressure: 150/95, Blood sugar: 180 mg/dL'
    }
    
    try:
        # Analyze the case
        print("Starting patient case analysis...")
        analysis = await manager.analyze_patient_case(patient_data)
        
        # Print results
        print("\nAnalysis Results:")
        for category, items in analysis.items():
            print(f"\n{category.upper()}:")
            for item in items:
                print(f"- {item}")
                
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 