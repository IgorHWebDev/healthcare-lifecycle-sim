from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass

class LifecycleStage(Enum):
    PRE_CONCEPTION = 1
    CONCEPTION = 2
    PRENATAL = 3
    BIRTH = 4
    NEONATAL = 5

@dataclass
class GeneticMaterial:
    material_id: str
    material_type: str  # egg, sperm, embryo
    donor_id: Optional[str]
    collection_date: datetime
    genetic_markers: Dict

@dataclass
class LifecycleEvent:
    event_id: str
    timestamp: datetime
    stage: LifecycleStage
    description: str
    location: str
    providers: List[str]
    biometric_data: Optional[Dict]
    genetic_data: Optional[Dict]

class LifecycleManager:
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.genetic_materials: Dict[str, GeneticMaterial] = {}
        self.lifecycle_events: Dict[str, List[LifecycleEvent]] = {}
        
    def register_genetic_material(self, 
                                material_type: str,
                                donor_id: Optional[str],
                                genetic_markers: Dict) -> str:
        """Register new genetic material in the system"""
        material_id = f"genetic_{len(self.genetic_materials)}"
        
        material = GeneticMaterial(
            material_id=material_id,
            material_type=material_type,
            donor_id=donor_id,
            collection_date=datetime.now(),
            genetic_markers=genetic_markers
        )
        
        self.genetic_materials[material_id] = material
        return material_id
    
    def create_lifecycle_event(self,
                             patient_id: str,
                             stage: LifecycleStage,
                             description: str,
                             location: str,
                             providers: List[str],
                             biometric_data: Optional[Dict] = None,
                             genetic_data: Optional[Dict] = None) -> str:
        """Create a new lifecycle event"""
        event_id = f"event_{len(self.lifecycle_events)}"
        
        event = LifecycleEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            stage=stage,
            description=description,
            location=location,
            providers=providers,
            biometric_data=biometric_data,
            genetic_data=genetic_data
        )
        
        if patient_id not in self.lifecycle_events:
            self.lifecycle_events[patient_id] = []
        
        self.lifecycle_events[patient_id].append(event)
        return event_id
    
    def get_patient_timeline(self, patient_id: str) -> List[LifecycleEvent]:
        """Get complete timeline of patient's lifecycle events"""
        return sorted(
            self.lifecycle_events.get(patient_id, []),
            key=lambda e: e.timestamp
        )
    
    def get_stage_events(self, 
                        patient_id: str, 
                        stage: LifecycleStage) -> List[LifecycleEvent]:
        """Get all events for a specific lifecycle stage"""
        return [
            event for event in self.lifecycle_events.get(patient_id, [])
            if event.stage == stage
        ]