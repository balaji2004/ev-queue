import uuid
from datetime import datetime
from models.maps_service import calculate_distance

class EV:
    def __init__(self, id=None, origin=None, destination=None, 
                 battery_capacity=None, initial_soc=None, 
                 consumption_rate=None, route=None):
        self.id = id or str(uuid.uuid4())
        self.origin = origin  # (lat, lng)
        self.destination = destination  # (lat, lng)
        self.battery_capacity = battery_capacity  # kWh
        self.soc = initial_soc  # State of Charge (0-1)
        self.consumption_rate = consumption_rate  # kWh/km
        
        self.current_position = origin  # Start at origin
        self.route = route or []  # List of points along route [(lat, lng), ...]
        self.route_index = 0  # Current position in route
        
        self.assigned_station = None  # Station assigned for charging
        self.charging = False  # Currently at a charger
        self.in_queue = False  # Waiting in a queue
        self.queue_arrival_time = None  # When EV arrived at queue
        self.charging_start_time = None  # When EV started charging
        self.waiting_time = 0  # Total time spent waiting in queue
        self.target_soc = 0.8  # Default target SoC is 80%
        
        self.trip_completed = False
        self.trip_start_time = datetime.now()
        self.trip_end_time = None
    
    def move(self, time_step_seconds):
        """Move the EV along its route for one time step"""
        if self.trip_completed or self.charging or self.in_queue:
            return
        
        if self.route_index >= len(self.route) - 1:
            # Reached destination
            self.current_position = self.destination
            self.trip_completed = True
            self.trip_end_time = datetime.now()
            return
        
        # Calculate distance that can be traveled in this time step
        current_point = self.route[self.route_index]
        next_point = self.route[self.route_index + 1]
        segment_distance = self._calculate_distance(current_point, next_point)
        
        # Calculate energy required
        energy_required = segment_distance * self.consumption_rate
        
        # Check if enough battery to complete segment
        if self.soc * self.battery_capacity >= energy_required:
            # Move to next point
            self.route_index += 1
            self.current_position = self.route[self.route_index]
            # Update battery
            self.soc -= energy_required / self.battery_capacity
        else:
            # Cannot complete segment, move as far as possible
            # For simplicity, just stay at current position
            pass
    
    def needs_charging(self, threshold):
        """Check if EV needs charging"""
        if self.charging or self.in_queue or self.trip_completed:
            return False
        return self.soc <= threshold
    
    def start_charging(self, station):
        """Start charging at a station"""
        self.assigned_station = station
        self.charging = True
        self.in_queue = False
        self.charging_start_time = datetime.now()
    
    def join_queue(self, station):
        """Join the queue at a station"""
        self.assigned_station = station
        self.in_queue = True
        self.queue_arrival_time = datetime.now()
    
    def update_waiting_time(self, time_step_seconds):
        """Update waiting time for EV in queue"""
        if self.in_queue:
            self.waiting_time += time_step_seconds
    
    def calculate_energy_needed_for_destination(self):
        """Calculate energy needed to reach destination from current position"""
        try:
            # Calculate remaining distance to destination
            remaining_distance = self.calculate_remaining_distance()
            
            # Calculate energy needed
            energy_needed = remaining_distance * self.consumption_rate
            
            # Add buffer (10 km worth of energy)
            buffer_energy = 10 * self.consumption_rate
            
            return energy_needed + buffer_energy
        except Exception as e:
            # Default to a reasonable value if calculation fails
            return 0.5 * self.battery_capacity  # Charge to 50% as fallback
    
    def calculate_remaining_distance(self):
        """Calculate remaining distance to destination"""
        try:
            if not self.route or len(self.route) < 2:
                return 0
            
            if self.route_index >= len(self.route) - 1:
                return 0
            
            # Ensure route_index is valid
            safe_index = min(max(0, self.route_index), len(self.route) - 1)
            
            total_distance = 0
            for i in range(safe_index, len(self.route) - 1):
                dist = self._calculate_distance(self.route[i], self.route[i + 1])
                # Check for invalid distance calculation
                if dist < 0 or dist > 1000:  # Sanity check: no segment should be >1000km
                    dist = 0
                total_distance += dist
            
            return total_distance
        except Exception as e:
            # Return a default distance if calculation fails
            return 50  # Default 50km as fallback
    
    def calculate_target_soc(self, queue_length):
        """
        Calculate target SoC based on queue length and energy needed
        
        If queue is empty, can charge to 100%
        Otherwise, charge only enough to reach destination + 10km buffer,
        but not more than 80%
        """
        if queue_length == 0:
            return 1.0  # Charge to 100% if queue is empty
        
        # Calculate energy needed to reach destination plus buffer
        energy_needed = self.calculate_energy_needed_for_destination()
        
        # Calculate SoC needed
        soc_needed = min(0.8, self.soc + (energy_needed / self.battery_capacity))
        
        return soc_needed
    
    def charge(self, time_step_seconds, charging_rate, queue_length):
        """Charge the EV for one time step"""
        if not self.charging:
            return
        
        # Calculate target SoC based on queue length and energy needed
        self.target_soc = self.calculate_target_soc(queue_length)
        
        # Calculate energy received in this time step (kWh)
        energy_received = charging_rate * (time_step_seconds / 3600)  # Convert seconds to hours
        
        # Update SOC
        new_soc = self.soc + (energy_received / self.battery_capacity)
        self.soc = min(new_soc, self.target_soc)  # Cap at target SoC
        
        # Check if charging is complete (reached target SoC)
        if self.soc >= self.target_soc:
            self.finish_charging()
    
    def finish_charging(self):
        """Finish charging and continue journey"""
        self.charging = False
        self.assigned_station = None
        self.waiting_time = 0  # Reset waiting time when charging completes
    
    def can_reach_station(self, station_location):
        """Check if the EV can reach the station with current battery"""
        try:
            distance = self._calculate_distance(self.current_position, station_location)
            # Sanity check on distance
            if distance < 0 or distance > 1000:  # No station should be >1000km away
                distance = 50  # Default reasonable distance
            
            energy_required = distance * self.consumption_rate
            return self.soc * self.battery_capacity >= energy_required
        except Exception as e:
            # Default to saying we can reach it, and let other checks determine suitability
            return True
    
    def is_station_on_route(self, station_location, max_detour=1000):
        """
        Check if station is on or close to the route
        
        Args:
            station_location: (lat, lng) of the station
            max_detour: Maximum allowed detour in meters
            
        Returns:
            bool: True if station is on route within max_detour
        """
        try:
            if not self.route or self.route_index >= len(self.route):
                return False
            
            # Ensure route_index is valid
            safe_index = min(max(0, self.route_index), len(self.route) - 1)
            
            # Check distance from each point in remaining route to station
            for i in range(safe_index, len(self.route)):
                route_point = self.route[i]
                try:
                    distance_to_station = calculate_distance(route_point, station_location)
                    
                    if distance_to_station <= max_detour:
                        return True
                except Exception:
                    # Skip this point if calculation fails
                    continue
            
            return False
        except Exception as e:
            # Default to False if overall calculation fails
            return False
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points (simplified)"""
        try:
            lat1, lng1 = point1
            lat2, lng2 = point2
            
            # Validate inputs
            if not all(isinstance(coord, (int, float)) for coord in [lat1, lng1, lat2, lng2]):
                return 0
            
            # Very simplified distance calculation - in reality, use haversine formula
            distance = ((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2) ** 0.5 * 111  # Rough km conversion
            
            # Sanity check the result
            if distance < 0 or distance > 1000:  # No segment should be >1000km
                return 0
            
            return distance
        except Exception as e:
            # Return a small non-zero value as fallback
            return 0.1  # 100m as default
        
    def to_dict(self):
        """Convert EV to dictionary for API response"""
        return {
            'id': self.id,
            'current_position': self.current_position,
            'soc': self.soc,
            'target_soc': self.target_soc,
            'charging': self.charging,
            'in_queue': self.in_queue,
            'assigned_station': self.assigned_station.id if self.assigned_station else None,
            'waiting_time': self.waiting_time,
            'trip_completed': self.trip_completed
        }