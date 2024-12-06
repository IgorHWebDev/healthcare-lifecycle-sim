import networkx as nx
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LocationType(Enum):
    WARD = "ward"
    ICU = "icu"
    OR = "operating_room"
    ER = "emergency_room"
    PHARMACY = "pharmacy"
    NURSE_STATION = "nurse_station"
    OFFICE = "office"
    WAITING_ROOM = "waiting_room"

@dataclass
class Location:
    id: str
    type: LocationType
    capacity: int
    current_occupancy: int = 0
    equipment: Dict[str, bool] = None  # equipment_name: is_available
    
class HospitalEnvironment:
    def __init__(self):
        self.layout = nx.Graph()
        self.locations: Dict[str, Location] = {}
        self.initialize_hospital_layout()
    
    def initialize_hospital_layout(self):
        """Initialize the basic hospital layout with different areas."""
        # Create main areas
        self.add_location("ward_1", LocationType.WARD, capacity=20)
        self.add_location("ward_2", LocationType.WARD, capacity=20)
        self.add_location("icu_1", LocationType.ICU, capacity=10)
        self.add_location("er", LocationType.ER, capacity=15)
        self.add_location("or_1", LocationType.OR, capacity=2)
        self.add_location("or_2", LocationType.OR, capacity=2)
        self.add_location("pharmacy", LocationType.PHARMACY, capacity=5)
        self.add_location("nurse_station_1", LocationType.NURSE_STATION, capacity=5)
        
        # Connect locations (define paths between areas)
        connections = [
            ("ward_1", "nurse_station_1"),
            ("ward_2", "nurse_station_1"),
            ("icu_1", "nurse_station_1"),
            ("er", "nurse_station_1"),
            ("or_1", "nurse_station_1"),
            ("or_2", "nurse_station_1"),
            ("pharmacy", "nurse_station_1"),
        ]
        
        for loc1, loc2 in connections:
            self.layout.add_edge(loc1, loc2)
    
    def add_location(self, location_id: str, location_type: LocationType, capacity: int,
                    equipment: Optional[Dict[str, bool]] = None):
        """Add a new location to the hospital layout."""
        if equipment is None:
            equipment = {}
        
        location = Location(
            id=location_id,
            type=location_type,
            capacity=capacity,
            equipment=equipment
        )
        self.locations[location_id] = location
        self.layout.add_node(location_id)
    
    def get_path(self, start: str, end: str) -> List[str]:
        """Find the shortest path between two locations."""
        try:
            path = nx.shortest_path(self.layout, start, end)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def update_occupancy(self, location_id: str, delta: int) -> bool:
        """Update the occupancy of a location."""
        location = self.locations[location_id]
        new_occupancy = location.current_occupancy + delta
        
        if 0 <= new_occupancy <= location.capacity:
            location.current_occupancy = new_occupancy
            return True
        return False
    
    def get_available_equipment(self, location_id: str) -> List[str]:
        """Get list of available equipment at a location."""
        location = self.locations[location_id]
        return [equip for equip, available in location.equipment.items() if available]
    
    def update_equipment_status(self, location_id: str, equipment_id: str, is_available: bool):
        """Update the availability status of equipment at a location."""
        if location_id in self.locations and equipment_id in self.locations[location_id].equipment:
            self.locations[location_id].equipment[equipment_id] = is_available 