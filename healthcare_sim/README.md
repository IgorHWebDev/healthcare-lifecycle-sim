# Healthcare Simulation System

A generative agent-based simulation system for modeling healthcare environments and interactions between medical professionals. This system is inspired by the architecture of the generative agents paper and adapted for healthcare scenarios.

## Features

- **Realistic Hospital Environment**
  - Multiple wards, ICU, ER, operating rooms, and other facilities
  - Pathfinding between locations
  - Equipment and resource management
  - Occupancy tracking

- **Intelligent Healthcare Agents**
  - Doctors with specializations and experience levels
  - Memory-based decision making
  - Realistic scheduling and task prioritization
  - Fatigue modeling
  - Emergency response capabilities

- **Complex Interactions**
  - Patient diagnosis and treatment
  - Medical procedures scheduling
  - Emergency event handling
  - Staff coordination
  - Medical record management

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage example:

```python
from healthcare_sim import SimulationManager
from datetime import datetime, timedelta

# Initialize simulation
sim = SimulationManager()

# Create a doctor
doctor_id = sim.create_doctor(
    name="Dr. Smith",
    specialization="Cardiology",
    years_experience=10
)

# Run simulation for 4 hours
current_time = datetime.now()
end_time = current_time + timedelta(hours=4)

while sim.current_time < end_time:
    events = sim.step()
    for event in events:
        print(f"Event: {event}")

# Generate report
report = sim.generate_report(current_time, end_time)
print(report)
```

## Architecture

### Environment Layer
- `HospitalEnvironment`: Manages the physical layout and state of the hospital
- Location types: Wards, ICU, ER, OR, etc.
- Equipment and resource tracking

### Agent Layer
- `BaseAgent`: Core agent functionality
  - Memory management
  - Planning and scheduling
  - Status tracking
  - Fatigue modeling

- `DoctorAgent`: Specialized medical agent
  - Patient diagnosis
  - Procedure scheduling
  - Emergency handling
  - Prescription writing
  - Medical record management

### Simulation Layer
- `SimulationManager`: Coordinates all simulation components
  - Time management
  - Event generation
  - Agent coordination
  - Reporting and statistics

## Extending the System

### Adding New Agent Types
Create new agent classes inheriting from `BaseAgent`:

```python
from healthcare_sim import BaseAgent, AgentRole

class NurseAgent(BaseAgent):
    def __init__(self, agent_id, name):
        super().__init__(agent_id, AgentRole.NURSE, name)
        # Add nurse-specific attributes and methods
```

### Adding New Location Types
Extend the `LocationType` enum in `hospital_environment.py`:

```python
class LocationType(Enum):
    WARD = "ward"
    ICU = "icu"
    # Add new location types
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 