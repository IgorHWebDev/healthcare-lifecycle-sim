from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from enum import Enum

class AgentRole(Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    TECHNICIAN = "technician"
    PATIENT = "patient"
    ADMIN = "admin"

@dataclass
class Memory:
    timestamp: datetime
    description: str
    importance: float
    related_agents: List[str] = field(default_factory=list)
    location: str = ""
    
@dataclass
class Plan:
    start_time: datetime
    end_time: datetime
    action: str
    location: str
    priority: int
    related_agents: List[str] = field(default_factory=list)

class BaseAgent:
    def __init__(self, 
                 agent_id: str,
                 role: AgentRole,
                 name: str,
                 specialization: Optional[str] = None):
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.specialization = specialization
        
        # Agent state
        self.current_location = ""
        self.current_action = ""
        self.status = "available"
        
        # Memory and planning
        self.memories: List[Memory] = []
        self.daily_plan: List[Plan] = []
        self.reflections: List[str] = []
        
        # Skills and attributes (can be extended based on role)
        self.skills: Dict[str, float] = {}
        self.fatigue = 0.0
        
    def add_memory(self, description: str, importance: float,
                  related_agents: List[str] = None, location: str = "") -> None:
        """Add a new memory to the agent's memory stream."""
        if related_agents is None:
            related_agents = []
            
        memory = Memory(
            timestamp=datetime.now(),
            description=description,
            importance=importance,
            related_agents=related_agents,
            location=location
        )
        self.memories.append(memory)
        
        # Trigger reflection if enough important memories have accumulated
        if len(self.memories) % 5 == 0:
            self.reflect()
    
    def retrieve_relevant_memories(self, context: str, k: int = 5) -> List[Memory]:
        """Retrieve k most relevant memories for the given context."""
        # In a real implementation, this would use embedding similarity
        # For now, we'll use simple importance-based retrieval
        sorted_memories = sorted(self.memories, 
                               key=lambda x: x.importance, 
                               reverse=True)
        return sorted_memories[:k]
    
    def add_plan(self, start_time: datetime, end_time: datetime,
                 action: str, location: str, priority: int,
                 related_agents: List[str] = None) -> None:
        """Add a new plan to the agent's schedule."""
        if related_agents is None:
            related_agents = []
            
        plan = Plan(
            start_time=start_time,
            end_time=end_time,
            action=action,
            location=location,
            priority=priority,
            related_agents=related_agents
        )
        
        # Insert plan in chronological order
        insert_idx = 0
        for i, existing_plan in enumerate(self.daily_plan):
            if existing_plan.start_time > start_time:
                insert_idx = i
                break
        self.daily_plan.insert(insert_idx, plan)
    
    def reflect(self) -> None:
        """Generate reflections based on recent memories."""
        recent_memories = sorted(self.memories[-5:], 
                               key=lambda x: x.importance, 
                               reverse=True)
        
        # In a real implementation, this would use LLM to generate meaningful reflections
        # For now, we'll create a simple summary
        reflection = f"Reflection based on recent activities: "
        reflection += ", ".join([m.description for m in recent_memories])
        self.reflections.append(reflection)
    
    def update_location(self, new_location: str) -> None:
        """Update the agent's current location."""
        self.current_location = new_location
        self.add_memory(f"Moved to {new_location}", importance=0.5, location=new_location)
    
    def update_status(self, new_status: str) -> None:
        """Update the agent's status (e.g., available, busy, off-duty)."""
        self.status = new_status
        self.add_memory(f"Status changed to {new_status}", importance=0.3)
    
    def increase_fatigue(self, amount: float = 0.1) -> None:
        """Increase agent's fatigue level."""
        self.fatigue = min(1.0, self.fatigue + amount)
        if self.fatigue > 0.8:
            self.add_memory("Feeling very tired", importance=0.7)
    
    def rest(self, amount: float = 0.2) -> None:
        """Reduce agent's fatigue through rest."""
        self.fatigue = max(0.0, self.fatigue - amount)
        self.add_memory("Took some rest", importance=0.4)
    
    def get_next_action(self) -> Optional[Plan]:
        """Get the next planned action based on current time and priority."""
        current_time = datetime.now()
        valid_plans = [p for p in self.daily_plan 
                      if p.start_time > current_time]
        
        if not valid_plans:
            return None
            
        # Return the next plan, prioritizing high-priority tasks
        return max(valid_plans, key=lambda x: x.priority) 