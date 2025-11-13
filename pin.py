#!/usr/bin/env python3
"""
Simple GPIO Pin Control - Quick pin control from command line

Usage:
    python pin.py <pin_number> <on|off>
    python pin.py <pin_number> on <seconds>

Examples:
    python pin.py 11 on          # Turn on pin 11
    python pin.py 11 off         # Turn off pin 11  
    python pin.py 13 on 3        # Turn on pin 13 for 3 seconds
"""

import sys
import time
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    if len(sys.argv) < 3:
        print("Usage: python pin.py <pin> <on|off> [seconds]")
        print("Examples:")
        print("  python pin.py 11 on")
        print("  python pin.py 11 off") 
        print("  python pin.py 13 on 5")
        return 1
    
    # Set debug mode for visibility
    os.environ["DEBUG_GPIO"] = "1"
    
    try:
        pin = int(sys.argv[1])
        action = sys.argv[2].lower()
        duration = float(sys.argv[3]) if len(sys.argv) > 3 else None
        
        # Import devices
        import devices
        import config
        
        print(f"Backend: {devices.get_backend_info()}")
        
        # Map pins to functions
        pin_map = {
            config.FAN_PIN: ("Fan", devices.set_fan),
            config.LIGHT_PIN: ("Light", devices.set_light),
            config.PUMP_PIN: ("Pump", devices.set_pump)
        }
        
        if pin not in pin_map:
            print(f"Pin {pin} not configured!")
            print(f"Available pins: {list(pin_map.keys())}")
            return 1
        
        name, func = pin_map[pin]
        
        if action == "on":
            func(True)
            print(f"✓ {name} (pin {pin}) ON")
            
            if duration:
                print(f"Waiting {duration} seconds...")
                time.sleep(duration)
                func(False)
                print(f"✓ {name} (pin {pin}) OFF after {duration}s")
                
        elif action == "off":
            func(False)
            print(f"✓ {name} (pin {pin}) OFF")
            
        else:
            print(f"Invalid action: {action}. Use 'on' or 'off'")
            return 1
            
        # Cleanup
        devices.cleanup()
        return 0
        
    except ValueError:
        print(f"Invalid pin number: {sys.argv[1]}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())