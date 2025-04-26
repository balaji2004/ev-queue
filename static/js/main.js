// Global variables
let simulationRunning = false;
let simulationSpeed = 5;
let updateInterval;
let stateUpdateCounter = 0;

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const resetBtn = document.getElementById('resetBtn');
const speedSlider = document.getElementById('speedSlider');
const speedValue = document.getElementById('speedValue');
const numEVsInput = document.getElementById('numEVs');
const numStationsInput = document.getElementById('numStations');
const numNodesInput = document.getElementById('numNodes');
const numRoutesInput = document.getElementById('numRoutes');
const generateBtn = document.getElementById('generateBtn');

// Metrics elements
const avgWaitTimeEl = document.getElementById('avgWaitTime');
const maxQueueLengthEl = document.getElementById('maxQueueLength');
const completionRateEl = document.getElementById('completionRate');
const abandonedRateEl = document.getElementById('abandonedRate');
const optimizationTimeEl = document.getElementById('optimizationTime');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log("Main module initializing...");
    
    // Setup event listeners
    startBtn.addEventListener('click', startSimulation);
    stopBtn.addEventListener('click', stopSimulation);
    resetBtn.addEventListener('click', resetSimulation);
    speedSlider.addEventListener('input', updateSpeed);
    generateBtn.addEventListener('click', generateNewData);
    
    // Initial update of simulation state
    updateSimulationState();
    
    console.log("Main module initialized");
});

// Start the simulation
function startSimulation() {
    fetch('/api/simulation/start', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            simulationRunning = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            resetBtn.disabled = true;
            generateBtn.disabled = true;
            
            // Start regular updates
            updateInterval = setInterval(updateSimulationState, 1000 / simulationSpeed);
        }
    })
    .catch(error => console.error('Error starting simulation:', error));
}

// Stop the simulation
function stopSimulation() {
    fetch('/api/simulation/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            simulationRunning = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            resetBtn.disabled = false;
            generateBtn.disabled = false;
            
            // Stop regular updates
            clearInterval(updateInterval);
        }
    })
    .catch(error => console.error('Error stopping simulation:', error));
}

// Reset the simulation
function resetSimulation() {
    fetch('/api/simulation/reset', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update state immediately
            updateSimulationState();
            
            // Reset charts
            if (typeof initCharts === 'function') {
                initCharts();
            }
            
            // Clear logs
            const optimizationLogsEl = document.getElementById('optimizationLogs');
            if (optimizationLogsEl) {
                optimizationLogsEl.textContent = "No optimization logs yet.";
            }
            
            // Clear journey timeline
            const journeyTimeline = document.getElementById('journeyTimeline');
            if (journeyTimeline) {
                journeyTimeline.innerHTML = '<p class="no-ev-selected">Select an EV to view its journey timeline.</p>';
            }
            
            // Reset EV selector and update with new data
            if (typeof updateEVSelector === 'function') {
                updateEVSelector();
            }
        }
    })
    .catch(error => console.error('Error resetting simulation:', error));
}

// Update simulation speed
function updateSpeed() {
    simulationSpeed = parseInt(speedSlider.value);
    speedValue.textContent = `${simulationSpeed}x`;
    
    // Adjust update interval if simulation is running
    if (simulationRunning) {
        clearInterval(updateInterval);
        updateInterval = setInterval(updateSimulationState, 1000 / simulationSpeed);
    }
}

// Generate new synthetic data
function generateNewData() {
    const numEVs = parseInt(numEVsInput.value);
    const numStations = parseInt(numStationsInput.value);
    const numNodes = parseInt(numNodesInput.value);
    const numRoutes = parseInt(numRoutesInput.value);
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            num_evs: numEVs,
            num_stations: numStations,
            num_nodes: numNodes,
            num_routes: numRoutes
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update map with new data
            if (typeof updateMap === 'function') {
                updateMap();
            }
            
            // Reset charts
            if (typeof initCharts === 'function') {
                initCharts();
            }
            
            // Update state immediately
            updateSimulationState();
            
            // Clear logs
            const optimizationLogsEl = document.getElementById('optimizationLogs');
            if (optimizationLogsEl) {
                optimizationLogsEl.textContent = "No optimization logs yet.";
            }
            
            // Reset journey view
            if (typeof updateEVSelector === 'function') {
                updateEVSelector();
            }
        }
    })
    .catch(error => console.error('Error generating new data:', error));
}

// Update simulation state from server
function updateSimulationState() {
    fetch('/api/simulation/state')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        
        // Update map
        if (typeof updateMapMarkers === 'function') {
            updateMapMarkers(data.evs, data.stations);
        }
        
        // Update metrics
        updateMetrics(data.metrics);
        
        // Update charts every 5 state updates to avoid performance issues
        stateUpdateCounter++;
        if (stateUpdateCounter % 5 === 0 && typeof updateCharts === 'function') {
            updateCharts(data);
        }
        
        // Update EV selector and journey timeline occasionally
        if (stateUpdateCounter % 20 === 0 && typeof updateEVSelector === 'function') {
            updateEVSelector();
        }
    })
    .catch(error => console.error('Error updating simulation state:', error));
}

// Update displayed metrics
function updateMetrics(metrics) {
    // Format wait time as minutes:seconds
    const waitMinutes = Math.floor(metrics.average_wait_time / 60);
    const waitSeconds = Math.floor(metrics.average_wait_time % 60);
    avgWaitTimeEl.textContent = `${waitMinutes}:${waitSeconds.toString().padStart(2, '0')}`;
    
    // Max queue length
    maxQueueLengthEl.textContent = metrics.max_queue_length;
    
    // Completion rate as percentage
    const completionPercent = (metrics.completion_rate * 100).toFixed(1);
    completionRateEl.textContent = `${completionPercent}%`;
    
    // Abandoned rate as percentage
    const abandonedPercent = (metrics.abandoned_rate * 100).toFixed(1);
    abandonedRateEl.textContent = `${abandonedPercent}%`;
    
    // Optimization time in milliseconds
    optimizationTimeEl.textContent = `${(metrics.optimization_time * 1000).toFixed(0)}ms`;
}