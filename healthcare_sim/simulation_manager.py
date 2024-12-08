from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from .intelligence.ai_integration import AIModelManager
from .lifecycle.lifecycle_manager import LifecycleManager, LifecycleStage, LifecycleEvent
from .config import config

class SimulationManager:
    def __init__(self):
        """Initialize simulation manager"""
        self.ai_manager = AIModelManager()
        self.lifecycle_manager = LifecycleManager(self.ai_manager)
        self.current_time = datetime.now()
        self.facility_layout = {
            "departments": {
                "er": {
                    "name": "Emergency Room",
                    "capacity": config.DEPARTMENTS['ER']['capacity'],
                    "staff": config.DEPARTMENTS['ER']['min_staff'],
                    "current_patients": 0,
                    "equipment": config.DEPARTMENTS['ER']['equipment'],
                    "locations": ["triage", "trauma", "general"]
                },
                "icu": {
                    "name": "Intensive Care Unit",
                    "capacity": config.DEPARTMENTS['ICU']['capacity'],
                    "staff": config.DEPARTMENTS['ICU']['min_staff'],
                    "current_patients": 0,
                    "equipment": config.DEPARTMENTS['ICU']['equipment'],
                    "locations": ["bed1", "bed2", "monitoring"]
                },
                "ward": {
                    "name": "General Ward",
                    "capacity": config.DEPARTMENTS['WARD']['capacity'],
                    "staff": config.DEPARTMENTS['WARD']['min_staff'],
                    "current_patients": 0,
                    "equipment": config.DEPARTMENTS['WARD']['equipment'],
                    "locations": ["room1", "room2", "nurses_station"]
                }
            },
            "connections": [
                ("er", "icu"),
                ("icu", "ward"),
                ("er", "ward")
            ]
        }
        
        # Initialize with some test data
        self._initialize_test_data()
    
    def get_facility_layout(self) -> Dict:
        """Get the current facility layout"""
        return self.facility_layout
    
    def _initialize_test_data(self):
        """Initialize simulation with test data"""
        # Add some test events
        self.events = []
        
        # Add some test patients
        self.patients = {
            "P001": {
                "id": "P001",
                "location": "er",
                "condition": "stable",
                "admission_time": datetime.now() - timedelta(hours=2)
            },
            "P002": {
                "id": "P002",
                "location": "icu",
                "condition": "critical",
                "admission_time": datetime.now() - timedelta(hours=5)
            }
        }
        
        # Update department counts
        for patient in self.patients.values():
            dept = patient["location"]
            if dept in self.facility_layout["departments"]:
                self.facility_layout["departments"][dept]["current_patients"] += 1
    
    def update(self, time_delta: timedelta) -> None:
        """Update simulation state"""
        self.current_time += time_delta
        
        # Update patient states
        for patient_id, patient in self.patients.items():
            if random.random() < 0.1:  # 10% chance of state change
                if patient["condition"] == "critical" and random.random() < 0.3:
                    patient["condition"] = "stable"
                    self._move_patient(patient_id, "icu", "ward")
                elif patient["condition"] == "stable" and random.random() < 0.1:
                    patient["condition"] = "critical"
                    self._move_patient(patient_id, "ward", "icu")
    
    def _move_patient(self, patient_id: str, from_dept: str, to_dept: str) -> None:
        """Move a patient between departments"""
        if (from_dept in self.facility_layout["departments"] and 
            to_dept in self.facility_layout["departments"]):
            self.facility_layout["departments"][from_dept]["current_patients"] -= 1
            self.facility_layout["departments"][to_dept]["current_patients"] += 1
            self.patients[patient_id]["location"] = to_dept
    
    def get_department_stats(self) -> Dict[str, Dict]:
        """Get statistics for each department"""
        stats = {}
        for dept_id, dept in self.facility_layout["departments"].items():
            stats[dept_id] = {
                "name": dept["name"],
                "occupancy_rate": dept["current_patients"] / dept["capacity"],
                "staff_ratio": dept["staff"] / dept["capacity"],
                "equipment": len(dept["equipment"])
            }
        return stats
    
    def get_patient_stats(self) -> Dict[str, int]:
        """Get patient statistics"""
        conditions = {}
        for patient in self.patients.values():
            condition = patient["condition"]
            conditions[condition] = conditions.get(condition, 0) + 1
        return conditions
    