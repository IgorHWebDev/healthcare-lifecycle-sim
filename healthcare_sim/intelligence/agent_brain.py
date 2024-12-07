import openai
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import random
from ..config import OPENAI_API_KEY, MIMIC_DATABASE_PATH
from .ai_integration import AIModelManager
from dataclasses import dataclass

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@dataclass
class AgentState:
    location: str
    status: str
    current_action: Optional[str]
    fatigue: float
    patient_count: int

class FallbackResponses:
    """Predefined responses for when OpenAI API is unavailable."""
    
    @staticmethod
    def get_observation_analysis(observation: str) -> str:
        templates = [
            "Patient observation noted. Continuing standard monitoring protocol.",
            "Vital signs within expected range. Will maintain current treatment plan.",
            "Minor changes observed. Adjusting care plan accordingly.",
            "Stable condition maintained. No immediate intervention required."
        ]
        return random.choice(templates)
    
    @staticmethod
    def get_reflection() -> str:
        templates = [
            "Patient care proceeding as planned. All protocols being followed.",
            "Team coordination effective. Resources being utilized efficiently.",
            "Standard procedures maintained. Patient responses within expectations.",
            "Department operations normal. Staff performance satisfactory."
        ]
        return random.choice(templates)
    
    @staticmethod
    def get_decision() -> str:
        templates = [
            "Continue current treatment plan with regular monitoring.",
            "Maintain standard protocols and observe patient response.",
            "Follow established procedures and document outcomes.",
            "Proceed with routine care while monitoring vital signs."
        ]
        return random.choice(templates)
    
    @staticmethod
    def get_schedule_plan() -> List[Dict]:
        return [
            {'time': '09:00', 'action': 'Morning rounds and patient assessment', 'priority': 'normal'},
            {'time': '10:30', 'action': 'Review test results and update charts', 'priority': 'normal'},
            {'time': '12:00', 'action': 'Team coordination and handoff', 'priority': 'normal'},
            {'time': '14:00', 'action': 'Patient consultations and follow-ups', 'priority': 'normal'}
        ]
    
    @staticmethod
    def get_emergency_plan(emergency_type: str) -> Dict:
        templates = {
            'cardiac_arrest': {
                'immediate_actions': 'Initiate CPR protocol and call emergency response team',
                'full_plan': '''1. Start chest compressions
2. Prepare defibrillator
3. Establish IV access
4. Administer emergency medications
5. Document all interventions'''
            },
            'severe_trauma': {
                'immediate_actions': 'Stabilize patient and assess injuries',
                'full_plan': '''1. Primary trauma survey
2. Control bleeding
3. Establish airway
4. Monitor vital signs
5. Prepare for imaging'''
            },
            'respiratory_failure': {
                'immediate_actions': 'Secure airway and begin oxygen therapy',
                'full_plan': '''1. Position patient
2. Start oxygen supplementation
3. Prepare for intubation if needed
4. Monitor SpO2
5. Assess breathing effort'''
            }
        }
        default_plan = {
            'immediate_actions': 'Assess patient and stabilize vital signs',
            'full_plan': '''1. Check vital signs
2. Establish IV access
3. Monitor patient
4. Call for specialist consult
5. Document interventions'''
        }
        return templates.get(emergency_type, default_plan)

class AgentMemory:
    def __init__(self):
        self.short_term: List[Dict] = []
        self.long_term: List[Dict] = []
        self.reflections: List[Dict] = []
    
    def add_observation(self, observation: str, importance: float, context: Dict):
        try:
            prompt = f"""
            As a healthcare professional, process this observation:
            Observation: {observation}
            Context: {context}
            
            Analyze the medical significance and potential implications for patient care.
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical professional analyzing healthcare observations."},
                    {"role": "user", "content": prompt}
                ]
            )
            processed_content = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}. Using fallback response.")
            processed_content = FallbackResponses.get_observation_analysis(observation)
        
        processed_memory = {
            'timestamp': datetime.now(),
            'raw_observation': observation,
            'processed_content': processed_content,
            'importance': importance,
            'context': context
        }
        
        self.short_term.append(processed_memory)
        if importance > 0.7:
            self.long_term.append(processed_memory)
    
    def reflect(self) -> str:
        try:
            recent_memories = self.short_term[-5:]
            memory_texts = [m['processed_content'] for m in recent_memories]
            
            prompt = f"""
            As a healthcare professional, reflect on these recent observations and generate insights:
            
            Recent Events:
            {memory_texts}
            
            What patterns or important conclusions can be drawn? What actions might be needed?
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical professional reflecting on recent events."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}. Using fallback response.")
            content = FallbackResponses.get_reflection()
        
        reflection = {
            'timestamp': datetime.now(),
            'content': content,
            'based_on': recent_memories if 'recent_memories' in locals() else []
        }
        
        self.reflections.append(reflection)
        return reflection['content']

class MedicalKnowledgeBase:
    def __init__(self):
        """Initialize with MIMIC database knowledge."""
        self.mimic_path = MIMIC_DATABASE_PATH
        self.load_mimic_data()
    
    def load_mimic_data(self):
        """Load relevant MIMIC data for medical knowledge."""
        try:
            self.diagnoses = pd.read_csv(f"{self.mimic_path}/diagnoses_icd.csv")
            self.procedures = pd.read_csv(f"{self.mimic_path}/procedures_icd.csv")
            self.admissions = pd.read_csv(f"{self.mimic_path}/admissions.csv")
        except Exception as e:
            print(f"Error loading MIMIC data: {str(e)}")
            self.use_synthetic_data()
    
    def use_synthetic_data(self):
        """Use synthetic data if MIMIC data is unavailable."""
        # Create synthetic medical knowledge
        self.common_conditions = [
            "Acute Myocardial Infarction",
            "Pneumonia",
            "Sepsis",
            "Stroke",
            "Trauma"
        ]
        self.common_procedures = [
            "ECG",
            "X-Ray",
            "CT Scan",
            "Blood Tests",
            "Surgery"
        ]

class AgentBrain:
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
        self.ai_manager = AIModelManager()
        self.state = AgentState(
            location="entrance",
            status="available",
            current_action=None,
            fatigue=0.0,
            patient_count=0
        )
    
    def update(self):
        """Update agent state"""
        # Simplified state update
        self.state.fatigue = min(1.0, self.state.fatigue + random.random() * 0.1)
        if random.random() < 0.3:
            self.state.location = random.choice(["ward", "office", "lab"])
            self.state.current_action = random.choice(["consulting", "examining", "resting"])
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state
    
    def make_decision(self, situation: Dict) -> Dict:
        """Make a decision using advanced AI analysis"""
        try:
            # Analyze patient risk
            risk_analysis = self.medical_analyzer.analyze_patient_risk(
                patient_data=situation.get('patient_data', {}),
                history=self.memory.short_term[-3:]
            )
            
            # Generate potential progression
            progression = self.scenario_generator.generate_patient_progression(
                current_state=situation,
                time_window="1h"
            )
            
            # Combine analyses for decision making
            prompt = f"""
            As a {self.agent_type} {'specialized in ' + self.specialization if self.specialization else ''},
            make a decision based on:
            
            Risk Analysis: {risk_analysis}
            Projected Progression: {progression}
            Current Situation: {situation}
            
            Provide specific actions and reasoning.
            """
            
            decision = self.ai_manager.generate_response(prompt, "medical", 0.7)
            
        except Exception as e:
            print(f"AI decision making error: {str(e)}. Using fallback.")
            decision = self.ai_manager._get_fallback_response("medical")
        
        return {
            'action': decision.split('\n')[0] if '\n' in decision else decision,
            'reasoning': decision,
            'risk_analysis': risk_analysis if 'risk_analysis' in locals() else None,
            'projected_progression': progression if 'progression' in locals() else None,
            'timestamp': datetime.now(),
            'context': situation
        }
    
    def handle_emergency(self, emergency_type: str, patient_id: str) -> Dict:
        """Handle emergency situations using scenario generation"""
        try:
            # Generate detailed emergency scenario
            scenario = self.scenario_generator.generate_emergency_scenario()
            
            # Analyze immediate risks
            risk_analysis = self.medical_analyzer.analyze_patient_risk(
                patient_data={"id": patient_id, "emergency_type": emergency_type},
                history=self.memory.short_term
            )
            
            # Get AI-generated response
            prompt = f"""
            Emergency situation:
            Type: {emergency_type}
            Scenario: {scenario}
            Risk Analysis: {risk_analysis}
            
            As a {self.agent_type} {'specialized in ' + self.specialization if self.specialization else ''},
            provide immediate action plan.
            """
            
            response = self.ai_manager.generate_response(prompt, "emergency", 0.9)
            
        except Exception as e:
            print(f"Emergency handling error: {str(e)}. Using fallback.")
            response = self.ai_manager._get_fallback_response("emergency")
        
        return {
            'action_plan': response,
            'scenario': scenario if 'scenario' in locals() else None,
            'risk_analysis': risk_analysis if 'risk_analysis' in locals() else None,
            'timestamp': datetime.now()
        }
    
    def generate_complex_case(self) -> Dict:
        """Generate a complex medical case for simulation"""
        try:
            # Generate base case
            case = self.scenario_generator.generate_complex_case()
            
            # Analyze case risks
            risk_analysis = self.medical_analyzer.analyze_patient_risk(
                patient_data=case,
                history=None
            )
            
            # Generate progression timeline
            progression = self.scenario_generator.generate_patient_progression(
                current_state=case,
                time_window="24h"
            )
            
            return {
                'case_details': case,
                'risk_analysis': risk_analysis,
                'progression_timeline': progression,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Case generation error: {str(e)}. Using fallback.")
            return {
                'case_details': "Standard medical case",
                'risk_level': "Moderate",
                'required_actions': ["Standard protocols"]
            }
    
    def analyze_treatment_plan(self, 
                             treatment_data: Dict,
                             patient_history: List[Dict]) -> Dict:
        """Analyze and optimize treatment plans"""
        try:
            # Analyze treatment effectiveness
            effectiveness = self.medical_analyzer.analyze_treatment_effectiveness(
                treatment_data=treatment_data,
                outcomes=patient_history
            )
            
            # Generate potential progression
            progression = self.scenario_generator.generate_patient_progression(
                current_state={"treatment": treatment_data, "history": patient_history},
                time_window="12h"
            )
            
            # Get AI recommendations
            prompt = f"""
            Analyze treatment plan:
            Current Treatment: {treatment_data}
            Effectiveness Analysis: {effectiveness}
            Projected Progression: {progression}
            
            Provide optimization recommendations.
            """
            
            recommendations = self.ai_manager.generate_response(prompt, "analysis", 0.7)
            
            return {
                'effectiveness_analysis': effectiveness,
                'progression_projection': progression,
                'recommendations': recommendations,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Treatment analysis error: {str(e)}. Using fallback.")
            return {
                'effectiveness': "Needs assessment",
                'recommendations': ["Follow standard protocols"]
            }
    
    def plan_schedule(self, current_patients: List[Dict], available_resources: Dict) -> List[Dict]:
        try:
            patient_summaries = []
            for patient in current_patients:
                summary = f"Patient {patient['id']}: {patient['diagnosis']} in {patient['location']}"
                patient_summaries.append(summary)
            
            prompt = f"""
            As a {self.agent_type} {'specialized in ' + self.specialization if self.specialization else ''},
            create a prioritized schedule for these patients:
            
            Patients:
            {patient_summaries}
            
            Available Resources:
            {available_resources}
            
            Create a detailed schedule that optimizes:
            1. Patient care priority
            2. Resource utilization
            3. Time management
            4. Emergency readiness
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a healthcare professional planning patient care."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            schedule_text = response.choices[0].message.content
            schedule_items = []
            
            for line in schedule_text.split('\n'):
                if line.strip():
                    schedule_items.append({
                        'time': line.split(':')[0] if ':' in line else None,
                        'action': line,
                        'priority': 'high' if 'urgent' in line.lower() or 'emergency' in line.lower() else 'normal'
                    })
            
            return schedule_items
        except Exception as e:
            print(f"OpenAI API error: {str(e)}. Using fallback response.")
            return FallbackResponses.get_schedule_plan()