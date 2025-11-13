#!/usr/bin/env python3
"""
GPIO Pin Control Utility for Orange Pi Zero 2W
Allows direct control of any GPIO pin from command line

Usage:
    python pin_control.py <pin> <on|off|toggle|read>
    python pin_control.py <pin> <on|off> [duration]
    python pin_control.py list
    python pin_control.py status

Examples:
    python pin_control.py 11 on              # Turn on pin 11 (fan)
    python pin_control.py 13 off             # Turn off pin 13 (light)
    python pin_control.py 15 toggle          # Toggle pin 15 (pump)
    python pin_control.py 7 read             # Read pin 7 (sensor)
    python pin_control.py 16 on 3            # Turn on pin 16 for 3 seconds
    python pin_control.py 18 toggle          # Toggle any GPIO pin
    python pin_control.py list               # List all available pins
    python pin_control.py status             # Show status of configured pins

Environment Variables:
    USE_WIRINGPI=1          # Force WiringPi backend
    DEBUG_GPIO=1            # Enable debug output
    FORCE_MOCK=1            # Use mock backend (simulation)

Available Pins (BOARD numbering):
    3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,37,38,40

Special Function Pins (use with caution):
    3,5:      I2C (SDA.1, SCL.1)
    8,10:     UART (TXD.0, RXD.0)  
    7,12,32:  PWM pins
    13,15,18,19,21,22,23,24: Communication pins (SPI-like functions)
"""

import sys
import time
import os
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """Setup environment for GPIO control"""
    # Default to debug mode for command line usage
    if not os.getenv("DEBUG_GPIO"):
        os.environ["DEBUG_GPIO"] = "1"

def get_pin_info():
    """Get information about configured pins and all available pins"""
    try:
        import config
        # Configured pins from config.py
        configured_pins = {
            config.FAN_PIN: "Fan",
            config.LIGHT_PIN: "Light", 
            config.PUMP_PIN: "Pump",
            config.TEMP_HUMIDITY_SENSOR_PIN: "DHT Sensor (input)"
        }
        
        # All available GPIO pins for Orange Pi Zero 2W (BOARD numbering)
        # Based on actual gpio readall output
        available_pins = {
            3: "SDA.1 (I2C)",           # GPIO 264, WPi 8
            5: "SCL.1 (I2C)",           # GPIO 263, WPi 1  
            7: "PWM3",                  # GPIO 269, WPi 2
            8: "TXD.0 (UART)",          # GPIO 224, WPi 3
            10: "RXD.0 (UART)",         # GPIO 225, WPi 4
            11: "PI01",                 # GPIO 257, WPi 6
            12: "PWM4",                 # GPIO 270, WPi 9
            13: "MOSI.1",               # GPIO 231, WPi 11
            15: "MISO.1",               # GPIO 232, WPi 12
            16: "PH04",                 # GPIO 228, WPi 10
            18: "SCLK.1",               # GPIO 230, WPi 14
            19: "RXD.2",                # GPIO 262, WPi 13
            21: "CE.0",                 # GPIO 229, WPi 15
            22: "CE.1",                 # GPIO 233, WPi 16
            23: "SCL.2",                # GPIO 265, WPi 18
            24: "SDA.2",                # GPIO 266, WPi 17
            26: "PI00",                 # GPIO 256, WPi 19
            29: "PI15",                 # GPIO 271, WPi 20
            31: "PI12",                 # GPIO 268, WPi 22
            32: "PWM1",                 # GPIO 267, WPi 21
            33: "PI02",                 # GPIO 258, WPi 23
            35: "PC12",                 # GPIO 76, WPi 24
            37: "PI16",                 # GPIO 272, WPi 25
            38: "PI04",                 # GPIO 260, WPi 26
            40: "PI03",                 # GPIO 259, WPi 27
        }
        
        # Merge configured pins with available pins
        for pin, description in available_pins.items():
            if pin in configured_pins:
                # Use configured name with GPIO info
                available_pins[pin] = f"{configured_pins[pin]} ({description})"
        
        return configured_pins, available_pins
    except ImportError:
        return {}, {}

def initialize_backend():
    """Initialize the devices backend"""
    try:
        import devices
        backend_info = devices.get_backend_info()
        debug_info = devices.get_debug_info()
        
        print(f"Backend: {backend_info}")
        if debug_info.get("backend_type") == "WiringPiBackend":
            print("Pin mapping:", debug_info.get("pin_mapping", {}))
        print()
        
        return devices
    except Exception as e:
        print(f"Error initializing backend: {e}")
        return None

def list_pins():
    """List all configured and available pins"""
    configured_pins, available_pins = get_pin_info()
    
    if not available_pins:
        print("No pin information available!")
        return
    
    print("Available GPIO pins (BOARD numbering):")
    print("Pin | Function/Description")
    print("----|--------------------")
    for pin in sorted(available_pins.keys()):
        description = available_pins[pin]
        marker = "★" if pin in configured_pins else " "
        print(f"{marker}{pin:2d}  | {description}")
    
    print("\n★ = Configured in config.py")
    print("\nNote: Pins 3,5 are I2C, pins 8,10 are UART, pins 19,21,23,24,26 are SPI")

def show_status(devices):
    """Show status of all output pins"""
    if not devices:
        print("Backend not initialized!")
        return
    
    configured_pins, available_pins = get_pin_info()
    debug_info = devices.get_debug_info()
    
    print("Configured pin status:")
    print("Pin | Function | State")
    print("----|----------|-------")
    
    # Try to get current states from backend
    backend = devices._backend
    if hasattr(backend, '_fan_state'):
        fan_state = "ON" if backend._fan_state else "OFF"
    else:
        fan_state = "Unknown"
    
    if hasattr(backend, '_light_state'):
        light_state = "ON" if backend._light_state else "OFF" 
    else:
        light_state = "Unknown"
        
    if hasattr(backend, '_pump_state'):
        pump_state = "ON" if backend._pump_state else "OFF"
    else:
        pump_state = "Unknown"
    
    try:
        import config
        print(f"{config.FAN_PIN:2d}  | Fan      | {fan_state}")
        print(f"{config.LIGHT_PIN:2d}  | Light    | {light_state}")
        print(f"{config.PUMP_PIN:2d}  | Pump     | {pump_state}")
        
        # Show sensor reading if available
        temp, hum = devices.read_sensor()
        if temp is not None and hum is not None:
            print(f"{config.TEMP_HUMIDITY_SENSOR_PIN:2d}  | Sensor   | {temp}°C, {hum}%RH")
        else:
            print(f"{config.TEMP_HUMIDITY_SENSOR_PIN:2d}  | Sensor   | No reading")
    except ImportError:
        print("No configuration available")

def control_pin(devices, pin, action, duration=None):
    """Control a specific pin"""
    if not devices:
        print("Backend not initialized!")
        return False
    
    configured_pins, available_pins = get_pin_info()
    
    # Check if pin is valid
    if pin not in available_pins:
        print(f"Pin {pin} is not a valid GPIO pin!")
        print("Use 'list' command to see available pins")
        return False
    
    pin_description = available_pins[pin]
    
    try:
        import config
        # Handle special case - sensor pin (read-only)
        if pin == config.TEMP_HUMIDITY_SENSOR_PIN:
            if action == "read":
                temp, hum = devices.read_sensor()
                if temp is not None and hum is not None:
                    print(f"Sensor reading: {temp}°C, {hum}% RH")
                else:
                    print("Failed to read sensor")
                return True
            else:
                print(f"Pin {pin} ({pin_description}) is configured as sensor input - use 'read' action")
                return False
        
        # Handle configured output pins with specific functions
        if pin == config.FAN_PIN:
            control_func = devices.set_fan
            get_state = lambda: devices._backend._fan_state if hasattr(devices._backend, '_fan_state') else False
        elif pin == config.LIGHT_PIN:
            control_func = devices.set_light
            get_state = lambda: devices._backend._light_state if hasattr(devices._backend, '_light_state') else False
        elif pin == config.PUMP_PIN:
            control_func = devices.set_pump
            get_state = lambda: devices._backend._pump_state if hasattr(devices._backend, '_pump_state') else False
        else:
            # Generic pin control for non-configured pins
            control_func = lambda state: control_generic_pin(devices, pin, state)
            get_state = lambda: get_generic_pin_state(devices, pin)
    
    except ImportError:
        # No config.py - treat all pins as generic
        control_func = lambda state: control_generic_pin(devices, pin, state)
        get_state = lambda: get_generic_pin_state(devices, pin)
    
    # Warn about special function pins
    i2c_pins = [3, 5]          # I2C pins
    uart_pins = [8, 10]        # UART pins  
    pwm_pins = [7, 12, 32]     # PWM pins
    spi_like_pins = [13, 15, 18, 19, 21, 22, 23, 24]  # SPI and similar communication pins
    
    if pin in i2c_pins:
        print(f"WARNING: Pin {pin} is I2C ({pin_description})")
        response = input("This may interfere with I2C devices. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return False
    elif pin in uart_pins:
        print(f"WARNING: Pin {pin} is UART ({pin_description})")
        response = input("This may interfere with serial communication. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return False
    elif pin in spi_like_pins:
        print(f"WARNING: Pin {pin} has communication function ({pin_description})")
        response = input("This may interfere with SPI/communication devices. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return False
    
    # Execute action
    if action == "on":
        control_func(True)
        print(f"Pin {pin} ({pin_description}) turned ON")
        
        if duration is not None:
            print(f"Waiting {duration} seconds...")
            time.sleep(duration)
            control_func(False)
            print(f"Pin {pin} ({pin_description}) turned OFF after {duration}s")
            
    elif action == "off":
        control_func(False)
        print(f"Pin {pin} ({pin_description}) turned OFF")
        
    elif action == "toggle":
        try:
            current_state = get_state()
            new_state = not current_state
            control_func(new_state)
            state_str = "ON" if new_state else "OFF"
            print(f"Pin {pin} ({pin_description}) toggled to {state_str}")
        except:
            print("Cannot read current state, setting to ON")
            control_func(True)
            print(f"Pin {pin} ({pin_description}) set to ON")
        
    elif action == "read":
        try:
            current_state = get_state()
            state_str = "ON" if current_state else "OFF"
            print(f"Pin {pin} ({pin_description}) state: {state_str}")
        except:
            print(f"Cannot read state of pin {pin}")
            return False
        
    else:
        print(f"Unknown action: {action}")
        return False
    
    return True


def control_generic_pin(devices, pin, state):
    """Control a generic GPIO pin directly through the backend"""
    backend = devices._backend
    
    if hasattr(backend, 'wiringpi'):
        # WiringPi backend
        wpi_pin = backend._board_to_wpi(pin)
        backend.wiringpi.pinMode(wpi_pin, 1)  # OUTPUT
        backend.wiringpi.digitalWrite(wpi_pin, 1 if state else 0)
        if backend.debug:
            print(f"[WiringPi DEBUG] Generic pin {pin} (WiringPi {wpi_pin}) set to {'HIGH' if state else 'LOW'}")
    
    elif hasattr(backend, 'GPIO'):
        # OPi.GPIO backend
        backend.GPIO.setup(pin, backend.GPIO.OUT)
        backend.GPIO.output(pin, backend.GPIO.HIGH if state else backend.GPIO.LOW)
        print(f"[OPi.GPIO] Pin {pin} set to {'HIGH' if state else 'LOW'}")
    
    else:
        # Mock backend
        print(f"[Mock] Pin {pin} set to {'HIGH' if state else 'LOW'}")


def get_generic_pin_state(devices, pin):
    """Get state of a generic GPIO pin"""
    backend = devices._backend
    
    if hasattr(backend, 'wiringpi'):
        # WiringPi backend - try to read pin state
        wpi_pin = backend._board_to_wpi(pin)
        try:
            return backend.wiringpi.digitalRead(wpi_pin) == 1
        except:
            return False
    
    elif hasattr(backend, 'GPIO'):
        # OPi.GPIO backend - try to read pin state  
        try:
            return backend.GPIO.input(pin) == backend.GPIO.HIGH
        except:
            return False
    
    else:
        # Mock backend - cannot read state
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="GPIO Pin Control Utility for Orange Pi Zero 2W",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 11 on              # Turn on pin 11 (fan)
  %(prog)s 13 off             # Turn off pin 13 (light) 
  %(prog)s 15 toggle          # Toggle pin 15 (pump)
  %(prog)s 7 read             # Read pin 7 (sensor)
  %(prog)s 16 on 3            # Turn on pin 16 for 3 seconds
  %(prog)s 22 toggle          # Toggle any GPIO pin
  %(prog)s list               # List all available pins
  %(prog)s status             # Show status of configured pins

Available pins (BOARD numbering):
  3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40

Special function pins (use with caution):
  3,5: I2C    8,10: UART    19,21,23,24,26: SPI

Environment Variables:
  USE_WIRINGPI=1              # Force WiringPi backend
  DEBUG_GPIO=1                # Enable debug output  
  FORCE_MOCK=1                # Use mock backend (simulation)
        """
    )
    
    parser.add_argument('pin_or_command', help='Pin number (3-40) or command (list,status)')
    parser.add_argument('action', nargs='?', help='Action: on, off, toggle, read')
    parser.add_argument('duration', type=float, nargs='?', help='Duration in seconds (for on action)')
    
    # Handle no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return 1
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Handle special commands
    if args.pin_or_command == "list":
        list_pins()
        return 0
    elif args.pin_or_command == "status":
        devices = initialize_backend()
        show_status(devices)
        return 0
    
    # Parse pin number
    try:
        pin = int(args.pin_or_command)
    except ValueError:
        print(f"Invalid pin number: {args.pin_or_command}")
        return 1
    
    if not args.action:
        print("Action required (on, off, toggle, read)")
        return 1
    
    # Initialize backend
    devices = initialize_backend()
    if not devices:
        return 1
    
    try:
        # Control pin
        success = control_pin(devices, pin, args.action.lower(), args.duration)
        
        # Cleanup
        if args.action.lower() in ["off", "toggle"]:
            # Small delay to ensure command completes
            time.sleep(0.1)
        
        devices.cleanup()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nInterrupted! Cleaning up...")
        devices.cleanup()
        return 1
    except Exception as e:
        print(f"Error: {e}")
        devices.cleanup()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)