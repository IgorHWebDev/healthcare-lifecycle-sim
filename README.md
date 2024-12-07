# Healthcare Lifecycle Simulation

A comprehensive healthcare simulation system that models patient lifecycle from pre-conception through neonatal care, with emphasis on patient safety and identity verification.

## Features

- Real-time simulation of healthcare facility operations
- Patient lifecycle tracking from pre-conception to neonatal care
- Genetic material management and tracking
- Staff and resource allocation
- Risk assessment and monitoring
- Interactive visualization of patient journeys
- Department capacity management
- Event logging and analysis

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

4. Create a `.env` file with your configuration:
```bash
cp healthcare_sim/.env.example healthcare_sim/.env
```

## Running the Application

1. Start the Streamlit server:
```bash
streamlit run healthcare_sim/run.py
```

2. Open your browser and navigate to:
```
http://localhost:8501
```

## Usage

### Simulation Controls

- **Start/Stop**: Control simulation execution
- **Pause/Resume**: Temporarily halt simulation
- **Reset**: Start fresh simulation

### Parameters

1. Time Settings
   - Simulation Speed (0.1x - 5.0x)
   - Time Scale (seconds/minutes/hours/days)

2. Event Generation
   - Auto-generate Events toggle
   - Risk Level adjustment (low/normal/high)

3. Department Settings
   - Capacity configuration
   - Staff allocation
   - Equipment management

### Monitoring

1. Dashboard
   - Real-time status
   - Timeline visualization
   - Event distribution

2. Patients & Staff
   - Current patient status
   - Staff assignments
   - Department occupancy

3. Facility Status
   - Department layout
   - Equipment status
   - Capacity metrics

4. Event Log
   - Chronological event tracking
   - Severity indicators
   - Detailed event information

## Deployment

1. Ensure all dependencies are in `requirements.txt`
2. Configure environment variables in `.env`
3. Test locally with `streamlit run healthcare_sim/run.py`
4. Deploy to your preferred platform (Streamlit Cloud, Heroku, etc.)

## Security Notes

- Keep `.env` file secure and never commit to version control
- Configure proper access controls in production
- Regularly update dependencies for security patches

## License

This project is licensed under the MIT License - see the LICENSE file for details.
