import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import streamlit as st
import json
from typing import Dict, List, Optional
import numpy as np
from io import BytesIO

class HealthcareReportGenerator:
    """Generates standardized healthcare simulation reports following best practices."""
    
    def __init__(self, simulation_manager, events: List[Dict], start_time: datetime):
        self.simulation = simulation_manager
        self.events = events
        self.start_time = start_time
        self.end_time = datetime.now()
    
    def generate_markdown_report(self) -> str:
        """Generate a complete report in markdown format."""
        report = []
        
        # Title
        report.append("# Healthcare Simulation Report\n")
        
        # Executive Summary
        report.append("## Executive Summary\n")
        report.append(self._generate_executive_summary())
        report.append("\n")
        
        # Simulation Parameters
        report.append("## Simulation Parameters\n")
        params = self._get_simulation_parameters()
        for key, value in params.items():
            report.append(f"- **{key}:** {value}")
        report.append("\n")
        
        # Staff Performance Metrics
        report.append("## Healthcare Staff Performance Metrics\n")
        report.extend(self._get_staff_metrics())
        report.append("\n")
        
        # Patient Care Statistics
        report.append("## Patient Care Statistics\n")
        report.extend(self._get_patient_statistics())
        report.append("\n")
        
        # Emergency Response Analysis
        report.append("## Emergency Response Analysis\n")
        report.extend(self._get_emergency_analysis())
        report.append("\n")
        
        # Resource Utilization
        report.append("## Resource Utilization\n")
        report.extend(self._get_resource_utilization())
        report.append("\n")
        
        # Quality Metrics
        report.append("## Quality Metrics\n")
        report.extend(self._get_quality_metrics())
        report.append("\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report.append(f"- {rec}")
        
        return "\n".join(report)
    
    def _generate_executive_summary(self) -> str:
        """Generate an executive summary of the simulation results."""
        total_events = len(self.events)
        total_patients = sum(len(agent.patients) for agent in self.simulation.agents.values() 
                           if hasattr(agent, 'patients'))
        emergency_count = len([e for e in self.events if e.get('type') == 'emergency'])
        
        return f"""This report summarizes the healthcare simulation conducted from {self.start_time.strftime('%Y-%m-%d %H:%M')} 
to {self.end_time.strftime('%Y-%m-%d %H:%M')}. The simulation involved {len(self.simulation.agents)} healthcare 
professionals managing {total_patients} patients, with {total_events} total events recorded including 
{emergency_count} emergency cases. Key findings and recommendations are detailed in the following sections."""
    
    def _get_simulation_parameters(self) -> Dict:
        """Get simulation parameters in a structured format."""
        return {
            "Duration": f"{(self.end_time - self.start_time).total_seconds() / 60:.1f} minutes",
            "Emergency Frequency": self.simulation.emergency_frequency,
            "Data Source": "MIMIC-IV Database" if self.simulation.patient_data else "Synthetic Data",
            "Number of Healthcare Professionals": len(self.simulation.agents),
            "Facility Locations": len(self.simulation.environment.locations)
        }
    
    def _get_staff_metrics(self) -> List[str]:
        """Get staff performance metrics in markdown format."""
        metrics = []
        for agent in self.simulation.agents.values():
            if not hasattr(agent, 'patients'):
                continue
            
            metrics.append(f"### {agent.name} - {agent.specialization}\n")
            metrics.append(f"- **Patient Load:** {len(agent.patients)}")
            metrics.append(f"- **Average Response Time:** {self._calculate_response_time(agent)}")
            metrics.append(f"- **Fatigue Level:** {agent.fatigue}%")
            metrics.append(f"- **Patient Outcomes:** {self._calculate_patient_outcomes(agent)}\n")
            
            if agent.patients:
                metrics.append("#### Assigned Patients:")
                for patient_id, patient in agent.patients.items():
                    metrics.append(f"- Patient {patient_id}: {patient['latest_admission']['diagnosis']} "
                                f"(Location: {patient['current_location']})")
                metrics.append("\n")
        return metrics
    
    def _get_patient_statistics(self) -> List[str]:
        """Get patient statistics in markdown format."""
        total_patients = sum(len(agent.patients) for agent in self.simulation.agents.values() 
                           if hasattr(agent, 'patients'))
        
        stats = [
            f"- **Total Patients:** {total_patients}",
            f"- **Average Length of Stay:** {self._calculate_avg_los()}",
            f"- **Patient Distribution by Department:** {self._get_patient_distribution()}",
            f"- **Critical Cases:** {len([e for e in self.events if e.get('type') == 'emergency'])}"
        ]
        return stats
    
    def _get_emergency_analysis(self) -> List[str]:
        """Get emergency analysis in markdown format."""
        emergency_events = [e for e in self.events if e.get('type') == 'emergency']
        analysis = []
        
        if emergency_events:
            response_times = [5] * len(emergency_events)  # placeholder
            analysis.extend([
                f"- **Total Emergencies:** {len(emergency_events)}",
                f"- **Average Response Time:** {np.mean(response_times):.1f} minutes",
                f"- **Response Time Range:** {min(response_times):.1f} - {max(response_times):.1f} minutes"
            ])
        return analysis
    
    def _get_resource_utilization(self) -> List[str]:
        """Get resource utilization in markdown format."""
        utilization = []
        for location_id, location in self.simulation.environment.locations.items():
            utilization.append(f"### {location.type.value}\n")
            utilization.extend([
                f"- **Current Occupancy:** {location.current_occupancy}/{location.capacity}",
                f"- **Utilization Rate:** {(location.current_occupancy/location.capacity)*100:.1f}%",
                f"- **Available Equipment:** {len(self.simulation.environment.get_available_equipment(location_id))}\n"
            ])
        return utilization
    
    def _get_quality_metrics(self) -> List[str]:
        """Get quality metrics in markdown format."""
        return [
            f"- **Staff-to-Patient Ratio:** {self._calculate_staff_patient_ratio()}",
            f"- **Average Wait Time:** {self._calculate_avg_wait_time()}",
            f"- **Patient Satisfaction Score:** {self._calculate_satisfaction_score()}"
        ]
    
    def _calculate_response_time(self, agent) -> str:
        """Calculate average response time for an agent."""
        return "5.0 minutes"  # placeholder
    
    def _calculate_patient_outcomes(self, agent) -> str:
        """Calculate patient outcomes for an agent."""
        return "85% Positive"  # placeholder
    
    def _calculate_avg_los(self) -> str:
        """Calculate average length of stay."""
        return "3.2 days"  # placeholder
    
    def _get_patient_distribution(self) -> str:
        """Get patient distribution across departments."""
        distribution = {}
        for agent in self.simulation.agents.values():
            if hasattr(agent, 'patients'):
                distribution[agent.specialization] = len(agent.patients)
        
        return ", ".join(f"{k}: {v}" for k, v in distribution.items())
    
    def _calculate_staff_patient_ratio(self) -> str:
        """Calculate staff-to-patient ratio."""
        total_staff = len([a for a in self.simulation.agents.values() if hasattr(a, 'patients')])
        total_patients = sum(len(agent.patients) for agent in self.simulation.agents.values() 
                           if hasattr(agent, 'patients'))
        
        if total_staff == 0:
            return "N/A"
        return f"1:{total_patients/total_staff:.1f}"
    
    def _calculate_avg_wait_time(self) -> str:
        """Calculate average wait time."""
        return "12.5 minutes"  # placeholder
    
    def _calculate_satisfaction_score(self) -> str:
        """Calculate patient satisfaction score."""
        return "4.2/5.0"  # placeholder
    
    def _generate_recommendations(self) -> List[str]:
        """Generate data-driven recommendations."""
        recommendations = []
        
        # Check staff fatigue
        high_fatigue_staff = [a for a in self.simulation.agents.values() 
                            if hasattr(a, 'fatigue') and a.fatigue > 70]
        if high_fatigue_staff:
            recommendations.append(
                "Consider implementing additional rest periods for staff members showing high fatigue levels."
            )
        
        # Check workload distribution
        workloads = [len(a.patients) for a in self.simulation.agents.values() if hasattr(a, 'patients')]
        if workloads:
            if max(workloads) > 2 * min(workloads):
                recommendations.append(
                    "Significant workload imbalance detected. Consider redistributing patients among available staff."
                )
        
        # Check resource utilization
        for location in self.simulation.environment.locations.values():
            if location.current_occupancy / location.capacity > 0.9:
                recommendations.append(
                    f"High occupancy in {location.type.value}. Consider expanding capacity or optimizing patient flow."
                )
        
        return recommendations

def add_report_section(st_container):
    """Add report generation section to Streamlit interface."""
    st_container.subheader("📊 Simulation Reports")
    
    if st.button("Generate Report"):
        report_gen = HealthcareReportGenerator(
            st.session_state.simulation,
            st.session_state.events,
            st.session_state.start_time
        )
        
        # Generate markdown report
        report_md = report_gen.generate_markdown_report()
        
        # Display report in Streamlit
        st.markdown(report_md)
        
        # Offer download as markdown
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report_md,
            file_name=f"healthcare_simulation_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
        
        # Show key metrics preview
        st.subheader("Key Metrics Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Events", len(st.session_state.events))
            st.metric("Active Staff", len(st.session_state.simulation.agents))
        
        with col2:
            emergency_count = len([e for e in st.session_state.events if e.get('type') == 'emergency'])
            st.metric("Emergency Cases", emergency_count)
            total_patients = sum(len(agent.patients) for agent in st.session_state.simulation.agents.values() 
                               if hasattr(agent, 'patients'))
            st.metric("Total Patients", total_patients)