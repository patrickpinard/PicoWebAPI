# V1 - main.py pour Raspberry Pico W
# Patrick Pinard - 2024


import json
import mm_wlan
from secrets import ssid, pwd, location, contact
from time import localtime, sleep
from machine import Pin, ADC, reset
import neopixel
import gc
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
    MAX_EVENTS = 50
    EVENTS_FILE = "events.json"

class PicoBoardRelay(object):
    
    def __init__(self):
        
        # Load log
        #self.events = []
        self.events=self.load_events()
        
        # Initialize relays with state tracking
        self.relays = {}
        self.relay_states = self._load_relay_states()
        
        # Initialize RGB LED and other system indicators
        self.led_rgb = neopixel.NeoPixel(Pin(Config.LED_PIN), Pin.OUT)
        self.onboard_led = Pin(Config.ONBOARD_LED_PIN, Pin.OUT)
        self.buzzer = Pin(Config.BUZZER_PIN, Pin.OUT)
        
        # Dynamically create relay pins
        self._setup_relays()
        self.led_rgb[0] = Config.COLORS["YELLOW"] 
        self.led_rgb.write()
        time.sleep(0.5)
        self.log_event("INFO: Relay System Initialized")

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
                self.log_event("INFO: Relay states loaded successfully")
                return states
        except (OSError, ValueError):
            # Return default states if file doesn't exist or is invalid
            default_states = {str(k): False for k in Config.RELAY_PINS.keys()}
            self.log_event("WARNING: Relay states reset to default")
            return default_states

    def save_relay_states(self):
        """Save current relay states to persistent storage"""
        try:
            with open(Config.STATE_FILE, 'w') as f:
                json.dump(self.relay_states, f)
            #self.log_event("INFO: Relay states saved")
        except OSError:
            self.log_event("ERROR: Failed to save relay states")

    def load_events(self):
        """Load events log from persistent storage"""
        try:
            with open(Config.EVENTS_FILE, 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            # Return empty events if events file doesn't exist or is invalid
            return []
        
    def save_events(self):
        """Save current events to persistent storage"""
        try:
            with open(Config.EVENTS_FILE, 'w') as f:
                json.dump(self.events, f)
            #self.log_event("INFO: Events log saved to persistent storage")
        except OSError:
            self.log_event("ERROR: Failed to save relay states")


    def set_relay(self, relay_id, state):
        """
        Set a specific relay state
        :param relay_id: Relay identifier (string)
        :param state: Boolean state (True/False)
        :return: Boolean indicating success
        """
        if relay_id not in self.relays:
            self.log_event(f"ERROR: Invalid relay ID : {relay_id}. Must be between 1..8")
            return False
        
        if state not in ["0","1"]:
            self.log_event(f"ERROR: Invalid state : {state} for relay ID : {relay_id}. Must be 1 or 0")
            return False
        
        # Set physical relay state
        self.relays[relay_id].value(state)
        
        # Update state tracking
        self.relay_states[relay_id] = state
        
        # Log the state change
        self.log_event(f"INFO: Relay {relay_id} set to {state}")
        
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
        
        self.log_event(f"INFO: All relays set to {state}")

    def log_event(self, message):
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
        self.save_events()
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

def create_app(PicoBoardRelay):
    """Factory function to create Microdot application"""
    from microdot import Microdot
    app = Microdot()

    @app.route('/relays')
    def get_relay_states(request):
        """Get the current state of all relays"""
        return json.dumps(PicoBoardRelay.relay_states), {"Content-Type": "application/json"}

    @app.route('/relay/<id>/<state>', methods=['GET', 'POST'])
    def control_relay(request, id, state):
        """Control a specific relay"""
        try:
            # Convert state to boolean
            relay_state = state == "1"
            success = PicoBoardRelay.set_relay(id, relay_state)
            
            if success:
                return json.dumps({f'Relay{id}': relay_state}), {"Content-Type": "application/json"}
            else:
                return json.dumps({"error": "Invalid command"}), {"status": 400, "Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"error": str(e)}), {"status": 500, "Content-Type": "application/json"}

    @app.route('/allrelays/<state>', methods=['GET', 'POST'])
    def control_all_relays(request, state):
        """Control all relays simultaneously"""
        try:
            relay_state = state == "1"
            PicoBoardRelay.set_all_relays(relay_state)
            return json.dumps(f"All relays set to {state}"), {"Content-Type": "application/json"}
        except Exception as e:
            return json.dumps({"error": str(e)}), {"status": 500, "Content-Type": "application/json"}

    @app.route('/system')
    def system_info(request):
        """Get system information"""
        return json.dumps(PicoBoardRelay.get_system_info()), {"Content-Type": "application/json"}

    @app.route('/reboot', methods=['GET', 'POST'])
    def system_reboot(request):
        """Perform system reboot"""
        PicoBoardRelay.log_event("INFO: Pico System reboot initiated")
        reset()

    
    @app.route("/events", methods=['GET', 'POST'])
    def events(request):

        return  json.dumps(PicoBoardRelay.events), {"Content-Type": "application/json"}

    return app

def main():
    """Main application entry point"""
  
    # Create Pico relay board system
    PicoBoard = PicoBoardRelay()

    # Initialize WiFi
    mm_wlan.connect_to_network(ssid, pwd)
    if not mm_wlan.is_connected():
        print("Failed to connect to WiFi")
        PicoBoard.log_event(f"WARNING: Failed to connect to WiFi")
        return
    PicoBoard.log_event(f"INFO: Wifi connected")

    # Create and run application
    app = create_app(PicoBoard)
    PicoBoard.log_event(f"INFO: Application started. Welcome !")
    try:
        PicoBoard.led_rgb[0] = Config.COLORS["GREEN"] 
        PicoBoard.led_rgb.write()
        app.run(host="0.0.0.0", port=80, debug=True)
    except Exception as e:
        
        PicoBoard.log_event(f"WARNING: Application startup failed: {e}")
        PicoBoard.led_rgb[0] = Config.COLORS["RED"] 
        PicoBoard.led_rgb.write()
        time.sleep(3)
    finally :
        PicoBoard.led_rgb[0] = Config.COLORS["OFF"] 
        PicoBoard.led_rgb.write()
        PicoBoard.log_event(f"INFO: Application stopped. Bye !")
        

if __name__ == "__main__":
    main()
    




