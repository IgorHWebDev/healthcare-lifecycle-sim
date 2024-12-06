from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from healthcare_sim.environment.hospital_environment import HospitalEnvironment, LocationType
from healthcare_sim.agents.base_agent import BaseAgent, AgentRole, Plan
from healthcare_sim.agents.doctor_agent import DoctorAgent
from healthcare_sim.data.patient_loader import PatientDataLoader

class SimulationManager:
    def __init__(self, mimic_path: Optional[str] = None):
        self.environment = HospitalEnvironment()
        self.agents: Dict[str, BaseAgent] = {}
        self.current_time = datetime.now()
        self.time_step = timedelta(minutes=5)
        self.events: List[Dict] = []
        self.emergency_frequency = 'normal'
        
        # Initialize patient data if MIMIC path is provided
        self.patient_data = None
        if mimic_path:
            self.patient_data = PatientDataLoader(mimic_path)
            self._initialize_patients()
        
        # Create initial doctors
        self._initialize_default_doctors()
    
    def _initialize_patients(self):
        """Initialize the simulation with current patients from MIMIC data."""
        if not self.patient_data:
            return
            
        # Get active patients and distribute them to appropriate locations
        active_patients = self.patient_data.get_active_patients()
        for patient in active_patients:
            location = self._map_mimic_location_to_sim(patient['current_location'])
            if location and self.environment.update_occupancy(location, 1):
                # Add patient to relevant doctor's patient list
                self._assign_patient_to_doctor(patient)
    
    def _map_mimic_location_to_sim(self, mimic_location: str) -> Optional[str]:
        """Map MIMIC location names to simulation location IDs."""
        mapping = {
            'EMERGENCY ROOM': 'er',
            'MEDICAL INTENSIVE CARE UNIT': 'icu_1',
            'SURGICAL INTENSIVE CARE UNIT': 'icu_1',
            'OPERATING ROOM': 'or_1',
            'GENERAL WARD': 'ward_1',
            'SURGICAL WARD': 'ward_2'
        }
        return mapping.get(mimic_location.upper())
    
    def _assign_patient_to_doctor(self, patient: Dict):
        """Assign a patient to an appropriate doctor based on diagnosis."""
        # Find doctor with matching specialization
        diagnosis = patient['latest_admission']['diagnosis']
        suitable_doctors = [
            agent for agent in self.agents.values()
            if isinstance(agent, DoctorAgent) and
            self._diagnosis_matches_specialization(diagnosis, agent.specialization)
        ]
        
        if suitable_doctors:
            doctor = min(suitable_doctors, key=lambda d: len(d.patients))
            doctor.patients[patient['patient_id']] = patient
    
    def _diagnosis_matches_specialization(self, diagnosis: str, specialization: str) -> bool:
        """Check if a diagnosis matches a doctor's specialization."""
        # Simple matching logic - could be made more sophisticated
        specialization_keywords = {
            'Cardiology': ['heart', 'cardiac', 'chest pain', 'arrhythmia'],
            'Emergency Medicine': ['trauma', 'acute', 'emergency'],
            'Surgery': ['fracture', 'appendicitis', 'surgical'],
            'Internal Medicine': ['diabetes', 'hypertension', 'pneumonia'],
            'Pediatrics': ['pediatric', 'child', 'juvenile'],
            'Neurology': ['stroke', 'seizure', 'neurological']
        }
        
        if diagnosis and specialization in specialization_keywords:
            return any(keyword.lower() in diagnosis.lower() 
                      for keyword in specialization_keywords[specialization])
        return False
    
    def add_agent(self, agent: BaseAgent) -> None:
        """Add a new agent to the simulation."""
        self.agents[agent.agent_id] = agent
        
    def create_doctor(self, name: str, specialization: str, years_experience: int) -> str:
        """Create and add a new doctor agent."""
        agent_id = f"doc_{len([a for a in self.agents.values() if isinstance(a, DoctorAgent)])}"
        doctor = DoctorAgent(agent_id, name, specialization, years_experience)
        self.add_agent(doctor)
        
        # Assign existing patients if we have MIMIC data
        if self.patient_data:
            active_patients = self.patient_data.get_active_patients()
            for patient in active_patients:
                if self._diagnosis_matches_specialization(
                    patient['latest_admission']['diagnosis'],
                    specialization
                ):
                    doctor.patients[patient['patient_id']] = patient
        
        return agent_id
    
    def step(self) -> List[str]:
        """Advance the simulation by one time step."""
        self.current_time += self.time_step
        events = []
        
        # Balance workload if needed
        self._balance_workload()
        
        # Process each agent's actions
        for agent in self.agents.values():
            # Reset fatigue if too high
            if agent.fatigue >= 90:
                self._schedule_rest(agent)
            
            # Get next planned action
            next_action = agent.get_next_action()
            
            if next_action and next_action.start_time <= self.current_time:
                # Execute the action
                event = self._execute_action(agent, next_action)
                if event:
                    events.append(event)
                    self.events.append(event)
            
            # Generate routine events
            routine_event = self._generate_routine_event(agent)
            if routine_event:
                events.append(routine_event)
                self.events.append(routine_event)
            
            # Check for new emergency cases based on frequency
            if isinstance(agent, DoctorAgent) and agent.status == "available":
                emergency_chance = {
                    'low': 0.05,
                    'normal': 0.15,
                    'high': 0.3
                }.get(self.emergency_frequency, 0.15)
                
                if random.random() < emergency_chance:
                    if self.patient_data:
                        emergency_cases = self.patient_data.get_emergency_cases()
                        if emergency_cases:
                            case = random.choice(emergency_cases)
                            if self._diagnosis_matches_specialization(
                                case['primary_diagnosis'],
                                agent.specialization
                            ):
                                self._generate_emergency(agent, case)
                    else:
                        self._generate_emergency(agent)
        
        return events
    
    def _execute_action(self, agent: BaseAgent, plan: Plan) -> Optional[Dict]:
        """Execute a planned action for an agent."""
        # Update agent's location if needed
        if plan.location != agent.current_location:
            path = self.environment.get_path(agent.current_location, plan.location)
            if path:
                agent.update_location(plan.location)
        
        # Create event record
        event = {
            "timestamp": self.current_time,
            "agent_id": agent.agent_id,
            "action": plan.action,
            "location": plan.location,
            "related_agents": plan.related_agents
        }
        
        # Increase agent fatigue
        agent.increase_fatigue(0.1)
        
        return event
    
    def _generate_emergency(self, agent: BaseAgent, emergency_case: Optional[Dict] = None) -> None:
        """Generate an emergency event, optionally based on MIMIC data."""
        if isinstance(agent, DoctorAgent) and agent.status == "available":
            if emergency_case:
                emergency_type = emergency_case['primary_diagnosis']
                patient_id = emergency_case['patient_id']
                location = self._map_mimic_location_to_sim(emergency_case['latest_admission']['admission_location']) or "er"
            else:
                emergency_types = ["cardiac_arrest", "severe_trauma", "respiratory_failure"]
                emergency_type = random.choice(emergency_types)
                patient_id = f"emergency_patient_{len(self.events)}"
                location = "er"
            
            agent.handle_emergency(emergency_type, patient_id, location)
            
            # Record emergency event
            event = {
                "timestamp": self.current_time,
                "type": "emergency",
                "emergency_type": emergency_type,
                "patient_id": patient_id,
                "location": location,
                "assigned_doctor": agent.agent_id
            }
            self.events.append(event)
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get the current status of an agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return {}
            
        status = {
            "id": agent.agent_id,
            "name": agent.name,
            "role": agent.role.value,
            "location": agent.current_location,
            "status": agent.status,
            "fatigue": agent.fatigue,
            "current_action": agent.current_action
        }
        
        if isinstance(agent, DoctorAgent):
            status["patient_count"] = len(agent.patients)
            status["specialization"] = agent.specialization
        
        return status
    
    def get_location_status(self, location_id: str) -> Dict:
        """Get the current status of a location."""
        location = self.environment.locations.get(location_id)
        if not location:
            return {}
            
        agents_present = [
            agent.agent_id for agent in self.agents.values()
            if agent.current_location == location_id
        ]
        
        return {
            "id": location.id,
            "type": location.type.value,
            "occupancy": location.current_occupancy,
            "capacity": location.capacity,
            "agents_present": agents_present,
            "available_equipment": self.environment.get_available_equipment(location_id)
        }
    
    def generate_report(self, start_time: datetime, end_time: datetime) -> Dict:
        """Generate a report of simulation events within a time window."""
        relevant_events = [
            event for event in self.events
            if start_time <= event["timestamp"] <= end_time
        ]
        
        # Count event types
        event_counts = {}
        for event in relevant_events:
            event_type = event.get("type", "routine")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Calculate agent statistics
        agent_stats = {}
        for agent in self.agents.values():
            relevant_memories = [
                memory for memory in agent.memories
                if start_time <= memory.timestamp <= end_time
            ]
            
            stats = {
                "name": agent.name,
                "role": agent.role.value,
                "memory_count": len(relevant_memories),
                "average_importance": sum(m.importance for m in relevant_memories) / len(relevant_memories) if relevant_memories else 0,
                "locations_visited": len(set(m.location for m in relevant_memories))
            }
            
            if isinstance(agent, DoctorAgent):
                stats["patient_count"] = len(agent.patients)
                stats["specialization"] = agent.specialization
            
            agent_stats[agent.agent_id] = stats
        
        # Get patient statistics if MIMIC data is available
        patient_stats = {}
        if self.patient_data:
            department_distribution = self.patient_data.get_department_distribution()
            active_patients = self.patient_data.get_active_patients()
            emergency_cases = self.patient_data.get_emergency_cases()
            
            patient_stats = {
                "total_active_patients": len(active_patients),
                "department_distribution": department_distribution,
                "emergency_cases": len(emergency_cases)
            }
        
        return {
            "time_period": {
                "start": start_time,
                "end": end_time
            },
            "event_counts": event_counts,
            "agent_statistics": agent_stats,
            "patient_statistics": patient_stats,
            "total_events": len(relevant_events)
        } 

    def _initialize_default_doctors(self):
        """Initialize the simulation with a default set of doctors."""
        default_doctors = [
            ("Dr. Sarah Chen", "Emergency Medicine", 8),
            ("Dr. James Wilson", "Cardiology", 15),
            ("Dr. Maria Rodriguez", "Surgery", 12),
            ("Dr. David Kim", "Internal Medicine", 10),
            ("Dr. Emily Taylor", "Pediatrics", 7)
        ]
        
        for name, specialization, years in default_doctors:
            self.create_doctor(name, specialization, years)

    def set_emergency_frequency(self, frequency: str):
        """Set the emergency event frequency (low, normal, high)."""
        self.emergency_frequency = frequency.lower()
    
    def _balance_workload(self):
        """Balance patient workload among doctors."""
        doctors = [a for a in self.agents.values() if isinstance(a, DoctorAgent)]
        if not doctors:
            return
        
        # Find overloaded and underloaded doctors
        avg_patients = sum(len(d.patients) for d in doctors) / len(doctors)
        overloaded = [d for d in doctors if len(d.patients) > avg_patients * 1.5]
        underloaded = [d for d in doctors if len(d.patients) < avg_patients * 0.5]
        
        # Transfer patients from overloaded to underloaded doctors
        for over_doc in overloaded:
            while len(over_doc.patients) > avg_patients and underloaded:
                under_doc = min(underloaded, key=lambda d: len(d.patients))
                # Transfer suitable patient
                for patient_id, patient in over_doc.patients.items():
                    if self._diagnosis_matches_specialization(
                        patient['latest_admission']['diagnosis'],
                        under_doc.specialization
                    ):
                        under_doc.patients[patient_id] = patient
                        del over_doc.patients[patient_id]
                        break

    def _schedule_rest(self, agent: BaseAgent):
        """Schedule rest for fatigued agent."""
        agent.fatigue = max(0, agent.fatigue - 50)  # Rest reduces fatigue
        event = {
            "timestamp": self.current_time,
            "type": "rest",
            "agent_id": agent.agent_id,
            "location": "break_room",
            "duration": 30  # minutes
        }
        self.events.append(event)

    def _generate_routine_event(self, agent: BaseAgent) -> Optional[Dict]:
        """Generate routine events for agents."""
        if not isinstance(agent, DoctorAgent) or not agent.patients:
            return None
        
        # Random chance to generate routine event
        if random.random() < 0.3:  # 30% chance per step
            patient_id = random.choice(list(agent.patients.keys()))
            patient = agent.patients[patient_id]
            location = self._map_mimic_location_to_sim(patient['current_location'])
            
            event_types = ["patient_check", "medication_admin", "consultation"]
            event = {
                "timestamp": self.current_time,
                "type": random.choice(event_types),
                "agent_id": agent.agent_id,
                "patient_id": patient_id,
                "location": location or "ward_1",
                "details": f"Routine {event_types} for patient {patient_id}"
            }
            return event
        
        return None
    