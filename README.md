# Healthcare Facility Simulation

A sophisticated healthcare facility simulation system that models the interactions between healthcare professionals, patients, and hospital resources using generative AI and the MIMIC-IV database.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

## Features

- Real-time simulation of healthcare facility operations
- Integration with MIMIC-IV clinical database
- AI-powered agent behavior and decision making
- Interactive visualization and monitoring
- Comprehensive reporting system
- Dynamic event generation and handling
- Resource management and allocation

## Requirements

- Python 3.11+
- MIMIC-IV database access (optional)
- OpenAI API key (for advanced agent behavior)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IgorHWebDev/healthcare-simulation.git
cd healthcare-simulation
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp healthcare_sim/.env.example healthcare_sim/.env
# Edit .env with your OpenAI API key
```

4. (Optional) Configure MIMIC-IV database path in `config.py`

## Usage

Run the simulation:
```bash
streamlit run healthcare_sim/gui.py
```

## Configuration

- Emergency Frequency: low/normal/high
- Simulation Duration: minutes/hours
- Simulation Speed: 0.1-5.0 steps/second
- Auto-restart option
- Debug mode
- Agent thought visibility

## Components

- **Simulation Manager**: Core simulation engine
- **Agents**: Healthcare professionals with AI-driven behavior
- **Environment**: Hospital layout and resource management
- **Visualization**: Real-time monitoring and analytics
- **Reports**: Healthcare standard compliant documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Igor H - [@IgorHWebDev](https://github.com/IgorHWebDev)

Project Link: [https://github.com/IgorHWebDev/healthcare-simulation](https://github.com/IgorHWebDev/healthcare-simulation)