import openai
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import random
from ..config import OPENAI_API_KEY, MIMIC_DATABASE_PATH

client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
    def __init__(self, agent_type: str, specialization: Optional[str] = None):
        self.memory = AgentMemory()
        self.knowledge_base = MedicalKnowledgeBase()
        self.agent_type = agent_type
        self.specialization = specialization
    
    def make_decision(self, situation: Dict) -> Dict:
        try:
            recent_memories = self.memory.short_term[-3:]
            relevant_reflections = [r for r in self.memory.reflections[-3:]]
            
            prompt = f"""
            As a {self.agent_type} {'specialized in ' + self.specialization if self.specialization else ''},
            analyze this situation and make a decision:
            
            Current Situation:
            {situation}
            
            Recent Memories:
            {recent_memories}
            
            Relevant Reflections:
            {relevant_reflections}
            
            What action should be taken? Consider:
            1. Medical priorities
            2. Resource availability
            3. Patient needs
            4. Staff coordination
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a healthcare professional making medical decisions."},
                    {"role": "user", "content": prompt}
                ]
            )
            decision = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}. Using fallback response.")
            decision = FallbackResponses.get_decision()
        
        return {
            'action': decision.split('\n')[0],
            'reasoning': decision,
            'timestamp': datetime.now(),
            'context': situation
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
    
    def handle_emergency(self, emergency_info: Dict) -> Dict:
        try:
            prompt = f"""
            As a {self.agent_type} {'specialized in ' + self.specialization if self.specialization else ''},
            create an immediate response plan for this emergency:
            
            Emergency Details:
            {emergency_info}
            
            Generate a detailed response plan including:
            1. Immediate actions needed
            2. Resource requirements
            3. Team coordination
            4. Patient stabilization steps
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a healthcare professional handling an emergency."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            plan = response.choices[0].message.content
            
            return {
                'immediate_actions': plan.split('\n')[0],
                'full_plan': plan,
                'timestamp': datetime.now(),
                'emergency_type': emergency_info.get('type', 'unknown')
            }
        except Exception as e:
            print(f"OpenAI API error: {str(e)}. Using fallback response.")
            fallback_plan = FallbackResponses.get_emergency_plan(emergency_info.get('type', 'unknown'))
            fallback_plan['timestamp'] = datetime.now()
            fallback_plan['emergency_type'] = emergency_info.get('type', 'unknown')
            return fallback_plan 