from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
from lifecycle.lifecycle_manager import LifecycleManager, LifecycleStage
from data.db_engine import HealthcareDBEngine

class SimulationManager:
    def __init__(self):
        """Initialize simulation manager with database engine"""
        self.current_time = datetime.now()
        self.db = HealthcareDBEngine()  # Use in-memory SQLite database
        self.lifecycle_manager = LifecycleManager()
        
        # Initialize simulation state
        self.last_update = self.current_time
        self.update_interval = timedelta(seconds=1)
    
    def update(self, time_delta: timedelta) -> None:
        """Update simulation state"""
        try:
            # Update current time
            self.current_time += time_delta
            
            # Check if we should generate new events
            if self.current_time - self.last_update >= self.update_interval:
                self._generate_events()
                self.last_update = self.current_time
            
            # Update lifecycle events
            self.lifecycle_manager.update(self.current_time)
            
        except Exception as e:
            raise RuntimeError(f"Error updating simulation: {str(e)}")
    
    def _generate_events(self):
        """Generate random events in the simulation"""
        # Chance for new admission
        if random.random() < 0.1:  # 10% chance
            self._generate_new_admission()
        
        # Update existing patients
        active_patients = self.db.get_active_patients()
        for patient in active_patients:
            # 20% chance for each patient to have an event
            if random.random() < 0.2:
                self._generate_patient_event(patient)
    
    def _generate_patient_event(self, patient: Dict):
        """Generate an event for a specific patient"""
        # Generate new vital signs
        vitals = {
            'heart_rate': random.randint(60, 100),
            'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            'temperature': round(random.uniform(36.5, 38.5), 1),
            'oxygen_saturation': random.randint(92, 100),
            'respiratory_rate': random.randint(12, 20)
        }
        
        # Possible events based on department
        dept_events = {
            "Emergency Room": [
                ("Initial assessment completed", "Under Observation"),
                ("Emergency treatment started", "Critical"),
                ("Stabilization in progress", "Improving"),
                ("Ready for transfer", "Stable")
            ],
            "Intensive Care Unit": [
                ("Critical care administered", "Critical"),
                ("Condition stabilizing", "Improving"),
                ("Recovery progressing", "Stable"),
                ("Ready for ward transfer", "Stable")
            ],
            "General Ward": [
                ("Routine checkup completed", "Stable"),
                ("Medication administered", "Improving"),
                ("Physical therapy session", "Improving"),
                ("Preparing for discharge", "Ready for Discharge")
            ],
            "Operating Room": [
                ("Surgery in progress", "Critical"),
                ("Surgery completed", "Recovery"),
                ("Post-op care started", "Under Observation")
            ]
        }
        
        # Get events for current department
        possible_events = dept_events.get(patient["department_name"], [("Check-up completed", "Stable")])
        event, new_status = random.choice(possible_events)
        
        # Update patient status
        self.db.update_patient_status(patient["patient_id"], new_status)
        
        # Create lifecycle event
        self.lifecycle_manager.create_lifecycle_event(
            patient_id=patient["patient_id"],
            stage=LifecycleStage.BIRTH,  # Using BIRTH as default stage
            description=f"{event} - {patient['department_name']}",
            location=patient["department_name"],
            providers=self._get_random_providers(),
            biometric_data=vitals
        )
        
        # Consider patient transfer based on status
        self._handle_patient_transfer(patient, new_status)
    
    def _handle_patient_transfer(self, patient: Dict, new_status: str):
        """Handle patient transfers between departments based on status"""
        current_dept = patient["department_name"]
        
        transfer_rules = {
            ("Emergency Room", "Stable"): "General Ward",
            ("Emergency Room", "Critical"): "Intensive Care Unit",
            ("Emergency Room", "Recovery"): "Operating Room",
            ("Intensive Care Unit", "Stable"): "General Ward",
            ("Operating Room", "Recovery"): "Intensive Care Unit"
        }
        
        target_dept = transfer_rules.get((current_dept, new_status))
        if target_dept:
            departments = self.db.get_department_stats()
            dept = next((d for d in departments if d["name"] == target_dept), None)
            
            if dept and dept["current_occupancy"] < dept["capacity"]:
                self.db.transfer_patient(patient["patient_id"], dept["department_id"])
                self.lifecycle_manager.create_lifecycle_event(
                    patient_id=patient["patient_id"],
                    stage=LifecycleStage.BIRTH,
                    description=f"Transferred from {current_dept} to {target_dept}",
                    location=target_dept,
                    providers=self._get_random_providers(),
                    biometric_data=None
                )
    
    def _get_random_providers(self) -> List[str]:
        """Get a random selection of healthcare providers"""
        doctors = [
            "Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown",
            "Dr. Jones", "Dr. Garcia", "Dr. Miller", "Dr. Davis"
        ]
        nurses = [
            "Nurse Anderson", "Nurse Taylor", "Nurse Thomas",
            "Nurse Jackson", "Nurse White", "Nurse Harris"
        ]
        return [random.choice(doctors), random.choice(nurses)]
    
    def _generate_new_admission(self):
        """Generate a new patient admission"""
        departments = self.db.get_department_stats()
        er = next((d for d in departments if d['name'] == "Emergency Room"), None)
        
        if er and er['current_occupancy'] < er['capacity']:
            # Create lifecycle event for new admission
            patient_id = f"NEW_{random.randint(1000, 9999)}"
            self.lifecycle_manager.create_lifecycle_event(
                patient_id=patient_id,
                stage=LifecycleStage.BIRTH,
                description="New emergency admission",
                location="Emergency Room",
                providers=["Dr. Smith", "Nurse Johnson"],
                biometric_data={
                    'heart_rate': random.randint(60, 100),
                    'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
                    'temperature': round(random.uniform(36.5, 38.5), 1),
                    'oxygen_saturation': random.randint(92, 100),
                    'respiratory_rate': random.randint(12, 20)
                }
            )
    
    def get_department_stats(self) -> List[Dict]:
        """Get current department statistics"""
        return self.db.get_department_stats()
    
    def get_active_patients(self) -> List[Dict]:
        """Get all currently active patients"""
        return self.db.get_active_patients()
    
    def get_patient_details(self, patient_id: int) -> Optional[Dict]:
        """Get detailed information for a specific patient"""
        return self.db.get_patient_details(patient_id)
    
    def get_current_time(self) -> datetime:
        """Get the current simulation time"""
        return self.current_time
    
    def get_facility_layout(self) -> Dict:
        """Get the facility layout information"""
        return {
            "departments": {
                "er": {
                    "name": "Emergency Room",
                    "locations": ["Triage", "Trauma Bay", "Treatment Rooms"]
                },
                "icu": {
                    "name": "Intensive Care Unit",
                    "locations": ["ICU Beds", "Monitoring Station", "Isolation Rooms"]
                },
                "ward": {
                    "name": "General Ward",
                    "locations": ["Patient Rooms", "Nursing Station", "Common Area"]
                },
                "or": {
                    "name": "Operating Room",
                    "locations": ["OR 1", "OR 2", "Recovery Room"]
                }
            },
            "connections": [
                ["Emergency Room", "Operating Room"],
                ["Emergency Room", "Intensive Care Unit"],
                ["Operating Room", "Intensive Care Unit"],
                ["Intensive Care Unit", "General Ward"]
            ]
        }
    