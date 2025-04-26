# EV Charging Queue Simulation

A web-based simulation platform for electric vehicle charging queues and optimization, built with Python, Flask, and interactive visualizations.

## Overview

This application simulates electric vehicles (EVs) traveling through a network of roads, requiring charging at strategically placed charging stations. It uses intelligent optimization algorithms to direct EVs to the most efficient charging stations based on various factors including:

- Current battery level
- Distance to charging stations
- Queue lengths at stations
- Charging speeds
- Route proximity

## Features

- **Interactive Map Visualization**: Real-time display of EVs, routes, and charging stations
- **Dynamic Simulation**: Control the simulation with start/stop/reset features
- **Charging Optimization**: Smart algorithms to minimize waiting times and optimize charging distribution
- **Configurable Parameters**: Adjust EV counts, station counts, and simulation settings
- **Performance Metrics**: Track wait times, queue lengths, and charging station utilization
- **Route Caching**: Efficient route generation with persistent caching to reduce API calls

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Mapping**: Google Maps API
- **Data Processing**: NumPy

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Maps API Key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ev-queue-simulation.git
   cd ev-queue-simulation
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `config.py` file with your Google Maps API key:
   ```python
   GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
   HOST = "0.0.0.0"
   PORT = 5000
   DEBUG = True
   TIME_STEP_SECONDS = 60  # Simulation time step in seconds
   CHARGE_THRESHOLD = 0.2  # Battery level threshold for charging
   OPTIMIZATION_INTERVAL = 10  # Run optimization every N steps
   ```

## Usage

1. Start the server:
   ```bash
   python app.py
   ```

2. Access the web interface at http://localhost:5000

### Command Line Arguments

- `--no-cache`: Disable data caching
- `--clear-cache`: Clear existing cache before starting

## Project Structure

- `app.py`: Main Flask application
- `models/`: Core simulation classes
  - `ev.py`: Electric vehicle model
  - `station.py`: Charging station model
  - `simulation.py`: Main simulation engine
  - `optimization.py`: Charging assignment algorithms
  - `maps_service.py`: Geospatial services and route handling
- `utils/`: Helper utilities
  - `data_generator.py`: Synthetic data generation
- `static/`: Frontend assets
  - `js/`: JavaScript files
  - `css/`: CSS styles
- `templates/`: HTML templates

## Caching System

The simulation implements a multi-level caching system to improve performance:

1. **Route Caching**: Stores routes between locations to reduce API calls
2. **Node Caching**: Preserves generated location nodes between runs
3. **Persistent Storage**: Saves cache to disk to retain data between app restarts

Cache files are stored as `.pkl` files in the project root directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Maps Platform for geospatial services
- Chart.js for visualization components 