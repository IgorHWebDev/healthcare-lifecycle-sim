from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from agents.base_agent import AgentRole
import json

def main():
    # Initialize simulation
    sim = SimulationManager()
    
    # Create some doctors
    cardio_doc_id = sim.create_doctor(
        name="Dr. Sarah Chen",
        specialization="Cardiology",
        years_experience=10
    )
    
    er_doc_id = sim.create_doctor(
        name="Dr. James Wilson",
        specialization="Emergency Medicine",
        years_experience=15
    )
    
    # Set initial locations
    sim.agents[cardio_doc_id].update_location("ward_1")
    sim.agents[er_doc_id].update_location("er")
    
    # Add some scheduled procedures
    cardio_doc = sim.agents[cardio_doc_id]
    current_time = datetime.now()
    
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
            else:
                print(f"\nEvent at {event['timestamp']}:")
                print(f"Agent {event['agent_id']}: {event['action']}")
                print(f"Location: {event['location']}")
    
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
    
    # Print final agent statuses
    print("\nFinal Agent Statuses:")
    for agent_id in sim.agents:
        status = sim.get_agent_status(agent_id)
        print(f"\n{status['name']}:")
        print(f"- Location: {status['location']}")
        print(f"- Status: {status['status']}")
        print(f"- Fatigue: {status['fatigue']:.2f}")

if __name__ == "__main__":
    main() 