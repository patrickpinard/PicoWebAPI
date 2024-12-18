import json
import mm_wlan
from secrets import ssid, pwd, ssl_key, ssl_cert, location, contact
from time import localtime, sleep
from machine import Pin, ADC, reset
import neopixel
import gc
import uos
import time

class Config:
    """Centralized configuration management"""
    # Relay pin mapping
    RELAY_PINS = {
        "1": 21, "2": 20, "3": 19, "4": 18,
        "5": 17, "6": 16, "7": 15, "8": 14
    }
    
    # Color definitions
    COLORS = {
        'RED': (255, 0, 0),
        'GREEN': (0, 255, 0),
        'BLUE': (0, 0, 255),
        'YELLOW': (255, 255, 0),
        'OFF': (0, 0, 0)
    }
    
    LED_PIN = 13
    BUZZER_PIN = 6
    ONBOARD_LED_PIN = "LED"
    STATE_FILE = "relay_states.json"
    MAX_EVENTS = 200

class RelaySystem:
    
    def __init__(self):
        
        # Create log 
        self.events=[]
        
        # Initialize relays with state tracking
        self.relays = {}
        self.relay_states = self._load_relay_states()
        
        # Initialize RGB LED and other system indicators
        self.led_rgb = neopixel.NeoPixel(Pin(Config.LED_PIN), Pin.OUT)
        self.onboard_led = Pin(Config.ONBOARD_LED_PIN, Pin.OUT)
        self.buzzer = Pin(Config.BUZZER_PIN, Pin.OUT)
        
        # Dynamically create relay pins
        self._setup_relays()
        
        self._log_event("INFO: Relay System Initialized")

    def _setup_relays(self):
        """Set up relay pins based on configuration"""
        for relay_id, pin_num in Config.RELAY_PINS.items():
            relay_pin = Pin(pin_num, Pin.OUT)
            self.relays[relay_id] = relay_pin
            
            # Set initial state based on saved configuration
            initial_state = self.relay_states.get(relay_id, False)
            relay_pin.value(initial_state)

    def _load_relay_states(self):
        """Load relay states from persistent storage"""
        try:
            with open(Config.STATE_FILE, 'r') as f:
                states = json.load(f)
                self._log_event("INFO: Relay states loaded successfully")
                return states
        except (OSError, ValueError):
            # Return default states if file doesn't exist or is invalid
            default_states = {str(k): False for k in Config.RELAY_PINS.keys()}
            self._log_event("WARNING: Relay states reset to default")
            return default_states

    def save_relay_states(self):
        """Save current relay states to persistent storage"""
        try:
            with open(Config.STATE_FILE, 'w') as f:
                json.dump(self.relay_states, f)
            #self._log_event("INFO: Relay states saved")
        except OSError:
            self._log_event("ERROR: Failed to save relay states")

    def set_relay(self, relay_id, state):
        """
        Set a specific relay state
        :param relay_id: Relay identifier (string)
        :param state: Boolean state (True/False)
        :return: Boolean indicating success
        """
        if relay_id not in self.relays:
            self._log_event(f"ERROR: Invalid relay ID {relay_id}")
            return False
        
        # Set physical relay state
        self.relays[relay_id].value(state)
        
        # Update state tracking
        self.relay_states[relay_id] = state
        
        # Log the state change
        self._log_event(f"INFO: Relay {relay_id} set to {state}")
        
        # Save states after change
        self.save_relay_states()
        
        return True

    def set_all_relays(self, state):
        """
        Set all relays to a specific state
        :param state: Boolean state (True/False)
        """
        for relay_id in self.relays:
            self.set_relay(relay_id, state)
        
        self._log_event(f"INFO: All relays set to {state}")

    def _log_event(self, message):
        """
        Log system events with timestamp
        Maintains a rolling buffer of events
        """
        # Implement event logging logic similar to original code
        # This is a placeholder - you may want to implement full logging
        event = {
                'message': message,
                'time': "{:02d}:{:02d}:{:02d}".format(*localtime()[3:6]),
                'date': "{:02d}/{:02d}/{}".format(localtime()[2], localtime()[1], localtime()[0])  # jour/mois/année
            }
        
        if len(self.events) > Config.MAX_EVENTS :
            self.events.pop(0)

        self.events.insert(0, event)
        print(message)

    def get_system_info(self):
        """
        Collect and return system information
        """
        def read_temperature():
            sensor_temp = ADC(4)
            conversion_factor = 3.3 / (65535)
            reading = sensor_temp.read_u16() * conversion_factor 
            temperature = 27 - (reading - 0.706)/0.001721
            
            return f"{temperature:.2f}"

        def read_voltage():
            vsys = ADC(29)
            conversion_factor = 3 * 3.3 / 65535
            voltage = vsys.read_u16() * conversion_factor * 100
            return f"{voltage:.2f}"

        current_time = localtime()
        return {
            'ip_address': mm_wlan.get_ip(),
            'ssid': ssid,
            'free_memory': f"{(gc.mem_alloc() + gc.mem_free())/1000:.0f}",
            'memory': f"{(gc.mem_free()/1000):.0f}",
            'allocated_memory' : f"{(gc.mem_alloc()/1000):.0f}",
            'temperature': read_temperature(),
            'voltage': read_voltage(), 
            'time': f"{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}",
            'date': f"{current_time[2]:02d}.{current_time[1]:02d}.{current_time[0]}",
            'location': location,
            'contact': contact
        }

def create_app(relay_system):
    """Factory function to create Microdot application"""
    from microdot import Microdot
    app = Microdot()

    @app.route('/relays')
    def get_relay_states(request):
        """Get the current state of all relays"""
        return json.dumps(relay_system.relay_states), {"Content-Type": "application/json"}

    @app.route('/relay/<id>/<state>', methods=['GET', 'POST'])
    def control_relay(request, id, state):
        """Control a specific relay"""
        try:
            # Convert state to boolean
            relay_state = state == "1"
            success = relay_system.set_relay(id, relay_state)
            
            if success:
                return json.dumps({f'Relay{id}': relay_state}), {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Invalid relay"}), {"status": 400, "Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"error": str(e)}), {"status": 500, "Content-Type": "application/json"}

    @app.route('/allrelays/<state>', methods=['GET', 'POST'])
    def control_all_relays(request, state):
        """Control all relays simultaneously"""
        try:
            relay_state = state == "1"
            relay_system.set_all_relays(relay_state)
            return json.dumps(f"All relays set to {state}"), {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"error": str(e)}), {"status": 500, "Content-Type": "application/json"}

    @app.route('/system')
    def system_info(request):
        """Get system information"""
        return json.dumps(relay_system.get_system_info()), {"Content-Type": "application/json"}

    @app.route('/reboot', methods=['GET', 'POST'])
    def system_reboot(request):
        """Perform system reboot"""
        relay_system._log_event("INFO: Pico System reboot initiated")
        reset()

    
    @app.route("/events", methods=['GET', 'POST'])
    def events(request):

        return  json.dumps(relay_system.events), {"Content-Type": "application/json"}

    return app

def main():
    """Main application entry point"""
    # Initialize WiFi
    mm_wlan.connect_to_network(ssid, pwd)
    if not mm_wlan.is_connected():
        print("Failed to connect to WiFi")
        return
   
    # Create relay system
    relay_system = RelaySystem()

    # Create and run application
    app = create_app(relay_system)
    
    try:
        # Run with SSL if certificates are available
        if ssl_key and ssl_cert:
            app.run(port=443, ssl_cert=ssl_cert, ssl_key=ssl_key)
        else:
            app.run(port=80)
    except Exception as e:
        print(f"Application startup failed: {e}")
        relay_system.buzzer.on()
        time.sleep(1)
        relay_system.buzzer.off()
        app.run(port=80)

if __name__ == "__main__":
    main()

