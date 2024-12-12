from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass
from collections import deque

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
    def __init__(self, ai_manager=None, max_events: int = 100):
        """Initialize lifecycle manager with optional AI manager"""
        self.ai_manager = ai_manager
        self.genetic_materials: Dict[str, GeneticMaterial] = {}
        self.lifecycle_events: Dict[str, List[LifecycleEvent]] = {}
        # Keep a fixed-size deque for recent events
        self.recent_events = deque(maxlen=max_events)
        self.event_counter = 0
        
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
        self.event_counter += 1
        event_id = f"event_{self.event_counter}"
        
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
        
        # Add to patient's event list
        if patient_id not in self.lifecycle_events:
            self.lifecycle_events[patient_id] = []
        self.lifecycle_events[patient_id].append(event)
        
        # Add to recent events
        self.recent_events.appendleft(event)
        
        return event_id
    
    def get_recent_events(self, limit: int = 10) -> List[LifecycleEvent]:
        """Get the most recent events across all patients"""
        return list(self.recent_events)[:limit]
    
    def get_patient_timeline(self, patient_id: str) -> List[LifecycleEvent]:
        """Get all events for a specific patient"""
        return self.lifecycle_events.get(patient_id, [])
    
    def get_stage_events(self, 
                        patient_id: str, 
                        stage: LifecycleStage) -> List[LifecycleEvent]:
        """Get all events for a specific lifecycle stage"""
        return [
            event for event in self.lifecycle_events.get(patient_id, [])
            if event.stage == stage
        ]
    
    def update(self, current_time: datetime) -> None:
        """Update lifecycle events based on current time"""
        # If AI manager is available, use it for event generation
        if self.ai_manager:
            self._generate_ai_events(current_time)
    
    def _generate_ai_events(self, current_time: datetime) -> None:
        """Generate AI-driven events if AI manager is available"""
        if not self.ai_manager:
            return
            
        # Example of generating events with AI
        for patient_id in self.lifecycle_events:
            if len(self.lifecycle_events[patient_id]) > 0:
                latest_event = max(self.lifecycle_events[patient_id], key=lambda e: e.timestamp)
                
                # Generate response using AI
                prompt = f"Patient {patient_id} current stage: {latest_event.stage.name}"
                response = self.ai_manager.generate_response(prompt)
                
                # Create new event based on AI response
                if response and response.get("primary_response"):
                    self.create_lifecycle_event(
                        patient_id=patient_id,
                        stage=latest_event.stage,
                        description=response["primary_response"],
                        location=latest_event.location,
                        providers=latest_event.providers,
                        biometric_data={"ai_confidence": response.get("confidence_score", 0.0)}
                    )