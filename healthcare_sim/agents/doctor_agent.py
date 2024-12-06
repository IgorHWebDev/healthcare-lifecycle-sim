from typing import List, Dict, Optional
from datetime import datetime, timedelta
from healthcare_sim.agents.base_agent import BaseAgent, AgentRole, Memory, Plan
from healthcare_sim.intelligence.agent_brain import AgentBrain

class DoctorAgent(BaseAgent):
    def __init__(self,
                 agent_id: str,
                 name: str,
                 specialization: str,
                 years_experience: int):
        super().__init__(agent_id, AgentRole.DOCTOR, name, specialization)
        
        self.years_experience = years_experience
        self.patients: Dict[str, Dict] = {}  # patient_id: patient_info
        self.scheduled_procedures: List[Dict] = []
        
        # Initialize the intelligent agent brain
        self.brain = AgentBrain("Doctor", specialization)
        
        # Initialize doctor-specific skills
        self.skills = {
            "diagnosis": min(0.5 + years_experience * 0.05, 1.0),
            "surgery": min(0.3 + years_experience * 0.07, 1.0),
            "patient_care": min(0.6 + years_experience * 0.04, 1.0),
            "emergency_response": min(0.4 + years_experience * 0.06, 1.0)
        }
    
    def diagnose_patient(self, patient_id: str, symptoms: List[str]) -> str:
        """Diagnose a patient using AI-enhanced decision making."""
        situation = {
            'patient_id': patient_id,
            'symptoms': symptoms,
            'patient_history': self.patients.get(patient_id, {}),
            'doctor_skills': self.skills
        }
        
        # Use AI brain to make diagnosis decision
        diagnosis_decision = self.brain.make_decision(situation)
        
        # Add to memory
        self.brain.memory.add_observation(
            f"Diagnosed patient {patient_id} with symptoms: {symptoms}",
            importance=0.8,
            context={'diagnosis': diagnosis_decision['action']}
        )
        
        return diagnosis_decision['action']
    
    def schedule_procedure(self, 
                         patient_id: str,
                         procedure_type: str,
                         scheduled_time: datetime,
                         location: str,
                         required_equipment: List[str]) -> bool:
        """Schedule a medical procedure with intelligent planning."""
        procedure = {
            "patient_id": patient_id,
            "type": procedure_type,
            "time": scheduled_time,
            "location": location,
            "equipment": required_equipment,
            "status": "scheduled"
        }
        
        # Use AI to validate and optimize the procedure schedule
        schedule_situation = {
            'procedure': procedure,
            'current_schedule': self.scheduled_procedures,
            'patient_info': self.patients.get(patient_id, {})
        }
        
        schedule_decision = self.brain.make_decision(schedule_situation)
        
        if 'proceed' in schedule_decision['action'].lower():
            self.scheduled_procedures.append(procedure)
            
            # Add to daily plan
            self.add_plan(
                start_time=scheduled_time,
                end_time=scheduled_time + timedelta(hours=1),
                action=f"Perform {procedure_type} on patient {patient_id}",
                location=location,
                priority=8,
                related_agents=[patient_id]
            )
            
            # Add to memory
            self.brain.memory.add_observation(
                f"Scheduled {procedure_type} for patient {patient_id}",
                importance=0.7,
                context=procedure
            )
            
            return True
        return False
    
    def perform_rounds(self, ward: str) -> List[str]:
        """Perform rounds with intelligent patient assessment."""
        observations = []
        
        # Get all patients in the ward
        ward_patients = {
            pid: pinfo for pid, pinfo in self.patients.items()
            if pinfo.get("ward") == ward
        }
        
        # Use AI to plan the rounds
        rounds_plan = self.brain.plan_schedule(
            list(ward_patients.values()),
            {'location': ward, 'time_available': 120}  # 2 hours for rounds
        )
        
        for plan_item in rounds_plan:
            patient_id = plan_item['action'].split()[1]  # Extract patient ID from action
            observation = f"Checked patient {patient_id} during rounds"
            observations.append(observation)
            
            self.brain.memory.add_observation(
                observation,
                importance=0.6,
                context={'location': ward, 'priority': plan_item['priority']}
            )
            
            # Increase fatigue slightly for each patient checked
            self.increase_fatigue(0.05)
        
        # Generate insights from rounds
        reflection = self.brain.memory.reflect()
        observations.append(f"Rounds reflection: {reflection}")
        
        return observations
    
    def handle_emergency(self, 
                        emergency_type: str,
                        patient_id: str,
                        location: str) -> None:
        """Handle medical emergency with AI-enhanced decision making."""
        # Get emergency response plan from AI
        emergency_info = {
            'type': emergency_type,
            'patient_id': patient_id,
            'location': location,
            'doctor_skills': self.skills,
            'current_status': self.status
        }
        
        response_plan = self.brain.handle_emergency(emergency_info)
        
        # Cancel or reschedule lower priority tasks
        current_time = datetime.now()
        self.daily_plan = [
            plan for plan in self.daily_plan
            if plan.start_time > current_time and plan.priority >= 9
        ]
        
        # Add emergency response to plan with highest priority
        self.add_plan(
            start_time=current_time,
            end_time=current_time + timedelta(minutes=30),
            action=response_plan['immediate_actions'],
            location=location,
            priority=10,
            related_agents=[patient_id]
        )
        
        # Add to memory with high importance
        self.brain.memory.add_observation(
            f"Emergency response: {emergency_type} for patient {patient_id}",
            importance=1.0,
            context={'plan': response_plan['full_plan']}
        )
        
        # Increase fatigue due to emergency stress
        self.increase_fatigue(0.2)
    
    def write_prescription(self, 
                         patient_id: str,
                         medication: str,
                         dosage: str,
                         duration: int) -> Dict:
        """Write a prescription with AI validation."""
        prescription_info = {
            'patient_id': patient_id,
            'medication': medication,
            'dosage': dosage,
            'duration_days': duration,
            'patient_history': self.patients.get(patient_id, {}),
            'doctor_specialization': self.specialization
        }
        
        # Get AI validation
        prescription_decision = self.brain.make_decision(prescription_info)
        
        prescription = {
            "patient_id": patient_id,
            "medication": medication,
            "dosage": dosage,
            "duration_days": duration,
            "prescribed_by": self.name,
            "timestamp": datetime.now(),
            "validation_notes": prescription_decision['reasoning']
        }
        
        # Add to memory
        self.brain.memory.add_observation(
            f"Prescribed {medication} for patient {patient_id}",
            importance=0.7,
            context=prescription
        )
        
        return prescription
    
    def update_patient_record(self,
                            patient_id: str,
                            notes: str,
                            vital_signs: Optional[Dict] = None) -> None:
        """Update patient records with AI-enhanced note processing."""
        if patient_id not in self.patients:
            self.patients[patient_id] = {}
            
        # Use AI to process and enhance the medical notes
        notes_context = {
            'patient_id': patient_id,
            'vital_signs': vital_signs,
            'previous_notes': self.patients[patient_id].get('notes', []),
            'doctor_specialization': self.specialization
        }
        
        processed_notes = self.brain.make_decision(notes_context)
        
        if vital_signs:
            self.patients[patient_id]["vital_signs"] = vital_signs
            
        if "notes" not in self.patients[patient_id]:
            self.patients[patient_id]["notes"] = []
            
        self.patients[patient_id]["notes"].append({
            "timestamp": datetime.now(),
            "note": processed_notes['reasoning']
        })
        
        # Add to memory
        self.brain.memory.add_observation(
            f"Updated medical record for patient {patient_id}",
            importance=0.6,
            context={'vital_signs': vital_signs, 'notes': notes}
        ) 