# Healthcare Simulation System 🏥

An interactive hospital simulation system that models real-time hospital operations, patient management, and healthcare events.

## Features

### 🏥 Hospital Management
- Real-time department occupancy tracking
- Multiple departments (ER, ICU, General Ward, Operating Room)
- Capacity monitoring and alerts
- Visual statistics and metrics

### 👥 Patient Management
- Patient admission and discharge
- Inter-department transfers
- Status tracking and updates
- Vital signs monitoring
- Medical event history

### 📊 Real-time Analytics
- Department occupancy rates
- Patient status distribution
- Event timeline
- Activity monitoring
- Filterable event feed

### ⚙️ Simulation Controls
- Adjustable simulation speed
- Start/Pause functionality
- Reset capability
- Real-time updates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healthcare-sim.git
cd healthcare-sim
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the simulation:
```bash
cd healthcare_sim
streamlit run gui.py
```

2. Use the web interface to:
   - Monitor hospital status
   - Manage patients
   - View real-time events
   - Control simulation parameters

## Project Structure

```
healthcare_sim/
├── README.md
├── requirements.txt
├── gui.py                 # Main Streamlit interface
├── simulation_manager.py  # Core simulation logic
├── data/
│   └── db_engine.py      # Data management
├── lifecycle/
│   └── lifecycle_manager.py  # Event and lifecycle management
└── visualization/
    └── __init__.py       # Visualization components
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Inspired by real hospital operations
- Designed for educational purposes 