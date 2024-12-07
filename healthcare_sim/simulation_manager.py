from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from healthcare_sim.intelligence.ai_integration import AIModelManager
from healthcare_sim.lifecycle.lifecycle_manager import LifecycleManager, LifecycleStage, LifecycleEvent
from healthcare_sim.config import (
    DEPARTMENTS,
    SIMULATION_STEP_DURATION,
    DEFAULT_EMERGENCY_FREQUENCY,
    DEFAULT_SIMULATION_DURATION,
    DEFAULT_SIMULATION_SPEED
)

class SimulationManager:
    def __init__(self):
        """Initialize simulation manager"""
        self.current_time = datetime.now()
        self.events = []
        self.patients = {}
        self.staff = {}
        self.facility_layout = self._create_facility_layout()
        self.ai_manager = AIModelManager()
        self.lifecycle_manager = LifecycleManager(self.ai_manager)
        
        # Initialize with some test data
        self._initialize_test_data()
    
    def _create_facility_layout(self) -> Dict:
        """Create the initial facility layout"""
        return {
            "departments": {
                "fertility_clinic": {
                    "name": "Fertility Clinic",
                    "locations": ["consultation", "lab", "storage", "procedure_room"],
                    "capacity": 10,
                    "current_patients": 0,
                    "staff": 5,
                    "equipment": ["microscopes", "incubators", "cryostorage"]
                },
                "prenatal": {
                    "name": "Prenatal Care",
                    "locations": ["waiting_room", "exam_rooms", "ultrasound", "lab"],
                    "capacity": 15,
                    "current_patients": 0,
                    "staff": 8,
                    "equipment": ["ultrasound_machines", "fetal_monitors"]
                },
                "labor_delivery": {
                    "name": "Labor & Delivery",
                    "locations": ["triage", "delivery_rooms", "operating_room", "recovery"],
                    "capacity": 12,
                    "current_patients": 0,
                    "staff": 10,
                    "equipment": ["delivery_beds", "monitors", "emergency_equipment"]
                }
            },
            "connections": [
                ("fertility_clinic", "prenatal"),
                ("prenatal", "labor_delivery")
            ]
        }
    
    def get_facility_layout(self) -> Dict:
        """Get the facility layout"""
        return self.facility_layout
    
    def _initialize_test_data(self):
        """Initialize simulation with test data"""
        # Create some genetic materials
        egg_id = self.lifecycle_manager.register_genetic_material(
            material_type="egg",
            donor_id="donor_123",
            genetic_markers={"marker1": "test"}
        )
        
        sperm_id = self.lifecycle_manager.register_genetic_material(
            material_type="sperm",
            donor_id="donor_456",
            genetic_markers={"marker1": "test"}
        )
        
        # Create conception event
        self.lifecycle_manager.create_lifecycle_event(
            patient_id="patient_789",
            stage=LifecycleStage.CONCEPTION,
            description=f"IVF conception using egg {egg_id} and sperm {sperm_id}",
            location="Fertility Clinic A",
            providers=["Dr. Smith"],
            genetic_data={
                "egg_id": egg_id,
                "sperm_id": sperm_id
            }
        )
    
    def update(self, time_delta: timedelta = timedelta(minutes=1), auto_events: bool = True, risk_level: str = "normal"):
        """Update simulation state"""
        self.current_time += time_delta
        
        if auto_events:
            self._generate_random_events(risk_level)
        
        self._update_lifecycle_events(risk_level)
        self._update_department_stats()
    
    def _generate_random_events(self, risk_level: str):
        """Generate random events based on risk level"""
        # Adjust probabilities based on risk level
        event_probability = {
            "low": 0.1,
            "normal": 0.3,
            "high": 0.5
        }.get(risk_level, 0.3)
        
        if random.random() < event_probability:
            # Generate a random event
            stage = random.choice(list(LifecycleStage))
            department = random.choice(list(self.facility_layout["departments"].keys()))
            dept_info = self.facility_layout["departments"][department]
            
            event_descriptions = {
                LifecycleStage.PRE_CONCEPTION: [
                    "Initial fertility consultation",
                    "Genetic screening",
                    "Donor material evaluation"
                ],
                LifecycleStage.CONCEPTION: [
                    "IVF procedure",
                    "Embryo transfer",
                    "Fertilization confirmation"
                ],
                LifecycleStage.PRENATAL: [
                    "Routine checkup",
                    "Ultrasound scan",
                    "Blood work analysis"
                ],
                LifecycleStage.BIRTH: [
                    "Labor onset",
                    "Delivery preparation",
                    "Emergency C-section"
                ],
                LifecycleStage.NEONATAL: [
                    "Newborn examination",
                    "Feeding session",
                    "Vital signs check"
                ]
            }
            
            description = random.choice(event_descriptions.get(stage, ["Routine check"]))
            location = random.choice(dept_info["locations"])
            
            self.lifecycle_manager.create_lifecycle_event(
                patient_id=f"patient_{random.randint(1, 999)}",
                stage=stage,
                description=description,
                location=f"{dept_info['name']} - {location}",
                providers=[f"Dr. Staff_{random.randint(1, dept_info['staff'])}"],
                biometric_data={
                    "heart_rate": random.randint(60, 100),
                    "blood_pressure": f"{random.randint(110, 140)}/{random.randint(60, 90)}"
                }
            )
    
    def _update_lifecycle_events(self, risk_level: str):
        """Update lifecycle events based on current time and risk level"""
        # Update existing events based on risk level
        complication_probability = {
            "low": 0.05,
            "normal": 0.15,
            "high": 0.30
        }.get(risk_level, 0.15)
        
        for patient_id, events in self.lifecycle_manager.lifecycle_events.items():
            if events and random.random() < complication_probability:
                # Add a complication event
                latest_event = max(events, key=lambda e: e.timestamp)
                
                complication_descriptions = {
                    LifecycleStage.PRE_CONCEPTION: "Quality control issue detected",
                    LifecycleStage.CONCEPTION: "Fertilization complications",
                    LifecycleStage.PRENATAL: "Abnormal test results",
                    LifecycleStage.BIRTH: "Delivery complications",
                    LifecycleStage.NEONATAL: "Neonatal distress"
                }
                
                self.lifecycle_manager.create_lifecycle_event(
                    patient_id=patient_id,
                    stage=latest_event.stage,
                    description=f"ALERT: {complication_descriptions.get(latest_event.stage, 'Complication detected')}",
                    location=latest_event.location,
                    providers=latest_event.providers,
                    biometric_data={
                        "alert_level": "high",
                        "requires_attention": True
                    }
                )
    
    def _update_department_stats(self):
        """Update department statistics"""
        for dept_id, dept in self.facility_layout["departments"].items():
            # Randomly update current patients
            dept["current_patients"] = min(
                dept["capacity"],
                max(0, dept["current_patients"] + random.randint(-1, 1))
            )
    