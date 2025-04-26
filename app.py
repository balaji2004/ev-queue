from flask import Flask, render_template, jsonify, request
import threading
import time
import config
import argparse
from utils.data_generator import generate_synthetic_data
from models.simulation import Simulation

# Parse command line arguments
parser = argparse.ArgumentParser(description='EV Queue Simulation Server')
parser.add_argument('--no-cache', action='store_true', help='Disable data caching')
parser.add_argument('--clear-cache', action='store_true', help='Clear existing cache before starting')
args = parser.parse_args()

app = Flask(__name__)

# Clear cache if requested
if args.clear_cache:
    import os
    import glob
    print("Clearing cache files...")
    for cache_file in glob.glob("*.pkl"):
        try:
            os.remove(cache_file)
            print(f"Removed {cache_file}")
        except Exception as e:
            print(f"Failed to remove {cache_file}: {e}")

# Initialize simulation with predefined routes
print("Initializing simulation data...")
evs, stations, routes = generate_synthetic_data(100, 20, 80, 240, use_cache=not args.no_cache)
print("Creating simulation engine...")
simulation = Simulation(evs, stations, routes)
print("Server initialization complete!")

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', api_key=config.GOOGLE_MAPS_API_KEY)

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    success = simulation.start()
    return jsonify({'success': success})

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    success = simulation.stop()
    return jsonify({'success': success})

@app.route('/api/simulation/reset', methods=['POST'])
def reset_simulation():
    """Reset the simulation"""
    success = simulation.reset()
    return jsonify({'success': success})

@app.route('/api/simulation/state')
def get_state():
    """Get current simulation state"""
    state = simulation.get_current_state()
    if not state:
        return jsonify({'error': 'No simulation state available'})
    return jsonify(state)

@app.route('/api/simulation/history')
def get_history():
    """Get simulation history"""
    start = int(request.args.get('start', 0))
    count = int(request.args.get('count', 100))
    history = simulation.get_history(start, count)
    return jsonify(history)

@app.route('/api/optimization/logs')
def get_optimization_logs():
    """Get optimization logs"""
    logs = simulation.get_optimization_logs()
    return jsonify({'logs': logs})

@app.route('/api/ev/journey-log/<ev_id>')
def get_ev_journey_log(ev_id):
    """Get detailed journey log for a specific EV"""
    journey_log = simulation.get_ev_journey_log(ev_id)
    return jsonify({'ev_id': ev_id, 'journey_log': journey_log})

@app.route('/api/stations')
def get_stations():
    """Get all charging stations"""
    return jsonify([station.to_dict() for station in stations])

@app.route('/api/evs')
def get_evs():
    """Get all EVs"""
    return jsonify([ev.to_dict() for ev in evs])

@app.route('/api/routes')
def get_routes():
    """Get all predefined routes"""
    return jsonify(routes)

@app.route('/api/generate', methods=['POST'])
def regenerate_data():
    """Regenerate synthetic data"""
    global evs, stations, routes, simulation
    
    # Stop current simulation
    simulation.stop()
    
    # Get parameters
    num_evs = int(request.json.get('num_evs', 100))
    num_stations = int(request.json.get('num_stations', 20))
    num_nodes = int(request.json.get('num_nodes', 80))
    num_routes = int(request.json.get('num_routes', 240))
    use_cache = request.json.get('use_cache', True)
    
    print(f"Regenerating data with {num_evs} EVs, {num_stations} stations, {num_nodes} nodes, {num_routes} routes...")
    print(f"Cache usage: {'enabled' if use_cache else 'disabled'}")
    
    # Generate new data
    evs, stations, routes = generate_synthetic_data(num_evs, num_stations, num_nodes, num_routes, use_cache=use_cache)
    
    # Create new simulation
    print("Creating new simulation engine...")
    simulation = Simulation(evs, stations, routes)
    print("Regeneration complete!")
    
    return jsonify({
        'success': True, 
        'num_evs': num_evs, 
        'num_stations': num_stations,
        'num_nodes': num_nodes,
        'num_routes': num_routes,
        'cache_used': use_cache
    })

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)