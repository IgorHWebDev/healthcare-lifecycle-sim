from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from agents.base_agent import AgentRole
import json

def main():
    # Initialize simulation with MIMIC database path
    mimic_path = "/Users/igor/Downloads/mimic-iv-clinical-database-demo-2.2"
    sim = SimulationManager(mimic_path=mimic_path)
    
    # Create doctors with different specializations
    doctors = [
        ("Dr. Sarah Chen", "Cardiology", 10),
        ("Dr. James Wilson", "Emergency Medicine", 15),
        ("Dr. Maria Rodriguez", "Internal Medicine", 8),
        ("Dr. David Kim", "Surgery", 12)
    ]
    
    doctor_ids = {}
    for name, specialization, experience in doctors:
        doctor_id = sim.create_doctor(
            name=name,
            specialization=specialization,
            years_experience=experience
        )
        doctor_ids[name] = doctor_id
        print(f"\nCreated {name}, specialized in {specialization}")
    
    # Set initial locations
    sim.agents[doctor_ids["Dr. Sarah Chen"]].update_location("ward_1")
    sim.agents[doctor_ids["Dr. James Wilson"]].update_location("er")
    sim.agents[doctor_ids["Dr. Maria Rodriguez"]].update_location("ward_2")
    sim.agents[doctor_ids["Dr. David Kim"]].update_location("or_1")
    
    # Schedule some procedures
    cardio_doc = sim.agents[doctor_ids["Dr. Sarah Chen"]]
    current_time = datetime.now()
    
    print("\nScheduling procedures...")
    cardio_doc.schedule_procedure(
        patient_id="patient_001",
        procedure_type="Cardiac Catheterization",
        scheduled_time=current_time + timedelta(hours=2),
        location="or_1",
        required_equipment=["catheterization_lab"]
    )
    
    # Run simulation for 4 hours
    print("\nStarting simulation...")
    simulation_start = current_time
    simulation_end = current_time + timedelta(hours=4)
    
    while sim.current_time < simulation_end:
        events = sim.step()
        
        # Print significant events
        for event in events:
            if event.get("type") == "emergency":
                print(f"\nEmergency at {event['timestamp']}:")
                print(f"Type: {event['emergency_type']}")
                print(f"Location: {event['location']}")
                print(f"Assigned Doctor: {event['assigned_doctor']}")
                
                # Get doctor's thought process
                doctor = sim.agents[event['assigned_doctor']]
                if hasattr(doctor, 'brain'):
                    reflection = doctor.brain.memory.reflect()
                    print(f"Doctor's Reflection: {reflection}")
            else:
                print(f"\nEvent at {event['timestamp']}:")
                print(f"Agent {event['agent_id']}: {event['action']}")
                print(f"Location: {event['location']}")
                
                # Get agent's thought process if available
                agent = sim.agents[event['agent_id']]
                if hasattr(agent, 'brain'):
                    recent_memories = agent.brain.memory.short_term[-1:]
                    if recent_memories:
                        print(f"Agent's Thoughts: {recent_memories[0]['processed_content']}")
    
    # Generate and print simulation report
    print("\nGenerating simulation report...")
    report = sim.generate_report(simulation_start, simulation_end)
    
    print("\nSimulation Report:")
    print("=================")
    print(f"Time Period: {report['time_period']['start']} to {report['time_period']['end']}")
    print(f"Total Events: {report['total_events']}")
    
    print("\nEvent Counts:")
    for event_type, count in report['event_counts'].items():
        print(f"- {event_type}: {count}")
    
    print("\nAgent Statistics:")
    for agent_id, stats in report['agent_statistics'].items():
        print(f"\n{stats['name']} ({stats['role']}):")
        print(f"- Memories recorded: {stats['memory_count']}")
        print(f"- Average importance: {stats['average_importance']:.2f}")
        print(f"- Locations visited: {stats['locations_visited']}")
        if 'patient_count' in stats:
            print(f"- Patients handled: {stats['patient_count']}")
    
    # Print final agent statuses
    print("\nFinal Agent Statuses:")
    for agent_id in sim.agents:
        status = sim.get_agent_status(agent_id)
        print(f"\n{status['name']}:")
        print(f"- Location: {status['location']}")
        print(f"- Status: {status['status']}")
        print(f"- Fatigue: {status['fatigue']:.2f}")
        
        # Print agent's final reflections if available
        agent = sim.agents[agent_id]
        if hasattr(agent, 'brain') and agent.brain.memory.reflections:
            print(f"- Final Reflection: {agent.brain.memory.reflections[-1]['content']}")

if __name__ == "__main__":
    main() 