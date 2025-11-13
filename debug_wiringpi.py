#!/usr/bin/env python3
"""
Debug script for testing WiringPi backend on Orange Pi Zero 2W
Run this script to test GPIO control and sensor readings with detailed debugging.

Usage:
    python debug_wiringpi.py                    # Auto-detect backend
    USE_WIRINGPI=1 python debug_wiringpi.py     # Force WiringPi backend
    DEBUG_GPIO=1 python debug_wiringpi.py       # Enable debug output
    FORCE_MOCK=1 python debug_wiringpi.py       # Force mock backend
"""

import os
import time
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def print_environment():
    """Print current environment variables"""
    print("=== Environment Variables ===")
    env_vars = ["FORCE_MOCK", "USE_WIRINGPI", "DEBUG_GPIO", "DHT_SENSOR"]
    for var in env_vars:
        value = os.getenv(var, "Not set")
        print(f"{var}: {value}")
    print()

def test_backend_selection():
    """Test backend selection and initialization"""
    print("=== Backend Selection Test ===")
    
    try:
        import devices
        print(f"✓ Devices module imported successfully")
        
        backend_info = devices.get_backend_info()
        print(f"✓ {backend_info}")
        
        debug_info = devices.get_debug_info()
        print("✓ Debug info:")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        print()
        
        return True
    except Exception as e:
        print(f"✗ Backend initialization failed: {e}")
        return False

def test_sensor_reading():
    """Test sensor readings"""
    print("=== Sensor Reading Test ===")
    
    try:
        import devices
        
        for i in range(3):
            print(f"Reading {i+1}/3...")
            temp, hum = devices.read_sensor()
            
            if temp is not None and hum is not None:
                print(f"✓ Temperature: {temp}°C, Humidity: {hum}%")
            else:
                print("✗ Failed to read sensor data")
            
            if i < 2:  # Don't wait after last reading
                time.sleep(2)
        print()
        
    except Exception as e:
        print(f"✗ Sensor reading failed: {e}")

def test_gpio_control():
    """Test GPIO control"""
    print("=== GPIO Control Test ===")
    
    try:
        import devices
        
        # Test each output
        outputs = [
            ("Fan", devices.set_fan),
            ("Light", devices.set_light),
            ("Pump", devices.set_pump)
        ]
        
        for name, func in outputs:
            print(f"Testing {name}...")
            
            # Turn ON
            func(True)
            print(f"  {name} ON")
            time.sleep(1)
            
            # Turn OFF
            func(False)
            print(f"  {name} OFF")
            time.sleep(0.5)
            
        print("✓ All GPIO outputs tested")
        print()
        
    except Exception as e:
        print(f"✗ GPIO control failed: {e}")

def test_pin_mapping():
    """Test pin mapping (WiringPi only)"""
    print("=== Pin Mapping Test ===")
    
    try:
        import devices
        debug_info = devices.get_debug_info()
        
        if "pin_mapping" in debug_info:
            print("✓ Pin mapping available:")
            for board_pin, wpi_pin in debug_info["pin_mapping"].items():
                print(f"  BOARD pin {board_pin} -> WiringPi pin {wpi_pin}")
        else:
            print("ⓘ Pin mapping not available (not using WiringPi backend)")
        print()
        
    except Exception as e:
        print(f"✗ Pin mapping test failed: {e}")

def main():
    """Main test function"""
    print("Orange Pi Zero 2W - WiringPi Debug Script")
    print("=" * 50)
    
    # Print environment
    print_environment()
    
    # Test backend selection
    if not test_backend_selection():
        print("Backend initialization failed. Exiting.")
        return 1
    
    # Test pin mapping
    test_pin_mapping()
    
    # Test sensor reading
    test_sensor_reading()
    
    # Test GPIO control
    test_gpio_control()
    
    print("=== Test Complete ===")
    print("All tests completed. Check output above for any errors.")
    
    # Cleanup
    try:
        import devices
        devices.cleanup()
        print("✓ Cleanup completed")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)