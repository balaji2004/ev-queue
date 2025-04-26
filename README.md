# EV Charging Queue Optimizer

A simulation platform for optimizing electric vehicle charging station assignments based on location, wait times, and energy needs.

![EV Charging Queue Optimizer](iimg/image.png)

## Overview

This project provides a web-based simulation environment to analyze and optimize electric vehicle charging station assignments. The system helps reduce wait times and improve overall charging infrastructure utilization through intelligent routing and queue management algorithms.

**Note**: The core optimization algorithm and methodology implemented in this project are covered by a patent application that has been published but not yet granted. Please see the [License](#license) section for usage restrictions.

## Features

- Real-time simulation of EV movements and charging needs
- Smart charging station assignment based on:
  - Current battery level
  - Distance to charging stations
  - Station queue lengths
  - Estimated charging times
  - Route optimization
- Interactive map visualization
- Performance metrics tracking
- Customizable simulation parameters

## Technology Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Maps API**: Google Maps Platform
- **Data Processing**: NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ev-charging-queue-optimizer.git
cd ev-charging-queue-optimizer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `config.py` file in the root directory with your Google Maps API key and other settings:
```python
# API Keys
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"

# Server settings
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# Simulation settings
TIME_STEP_SECONDS = 60  # Each simulation step represents 60 seconds
OPTIMIZATION_INTERVAL = 10  # Run optimization every 10 steps
CHARGE_THRESHOLD = 0.3  # Start seeking charging when battery at 30%
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Open a web browser and navigate to `http://127.0.0.1:5000`

3. Use the controls in the interface to:
   - Start/stop the simulation
   - Adjust simulation speed
   - Reset the simulation
   - Generate new data with custom parameters

## Simulation Controls

- **Start Simulation**: Begin the simulation with the current parameters
- **Stop Simulation**: Pause the current simulation
- **Reset**: Reset the simulation to its initial state
- **Speed**: Adjust the simulation speed (1x-10x)
- **Generate New Data**: Create a new simulation with customized parameters:
  - Number of EVs
  - Number of charging stations
  - Number of geographic nodes
  - Number of routes

## Optimization Algorithm

The core optimization algorithm (implemented in `models/optimization.py`) evaluates multiple factors to assign EVs to optimal charging stations:

1. **Accessibility**: Determines if an EV can reach a station with current battery
2. **Route Proximity**: Prioritizes stations that are close to the EV's planned route
3. **Queue Length**: Considers current waiting times at each station
4. **Charging Time**: Calculates the time needed to charge based on current SoC and energy needs
5. **Total Time Cost**: Combines travel time, wait time, and charge time for overall optimization

## Project Structure

```
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models/
│   ├── ev.py              # Electric vehicle model
│   ├── station.py         # Charging station model
│   ├── simulation.py      # Simulation engine
│   ├── optimization.py    # Charging assignment algorithm
│   └── maps_service.py    # Google Maps integration
├── static/
│   ├── css/               # Stylesheets
│   └── js/                # Client-side scripts
├── templates/
│   └── index.html         # Main UI template
└── utils/
    └── data_generator.py  # Synthetic data generation
```

## License

This project is licensed under a custom license - see the [LICENSE](LICENSE) file for details.

**Important**: The core optimization methodology and algorithms implemented in this project are subject to a pending patent. The code is provided for educational and research purposes only. Commercial use or implementation of the optimization algorithm requires explicit permission.

## Acknowledgments

- Google Maps Platform for geospatial services
- Chart.js for visualization components
- Flask community for the web framework

## Contact

For inquiries regarding licensing or commercial use, please contact [your-email@example.com].
