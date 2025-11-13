#!/usr/bin/env python3
"""
Test script to verify WiringPi pin mapping matches gpio commands
This script tests if our WiringPi backend produces the same results as manual gpio commands
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_pin_mapping():
    """Test if our pin mapping matches the gpio manual"""
    
    # Force WiringPi backend
    os.environ["USE_WIRINGPI"] = "1"
    os.environ["DEBUG_GPIO"] = "1"
    
    print("Testing WiringPi pin mapping...")
    print("Physical Pin 7 should map to WiringPi pin 2")
    print()
    
    try:
        import devices
        
        # Get debug info
        debug_info = devices.get_debug_info()
        pin_mapping = debug_info.get("pin_mapping", {})
        
        print("Pin mapping from backend:")
        for board_pin, wpi_pin in pin_mapping.items():
            print(f"  Physical pin {board_pin} -> WiringPi pin {wpi_pin}")
        
        print()
        
        # Test physical pin 7
        physical_pin_7_wpi = pin_mapping.get(7, "NOT FOUND")
        print(f"Physical pin 7 maps to WiringPi pin: {physical_pin_7_wpi}")
        
        if physical_pin_7_wpi == 2:
            print("✅ CORRECT: Physical pin 7 -> WiringPi pin 2")
            print("   This matches: gpio mode 2 out; gpio write 2 1")
        else:
            print(f"❌ WRONG: Expected WiringPi pin 2, got {physical_pin_7_wpi}")
        
        print()
        print("Manual GPIO commands equivalent:")
        print("  gpio mode 2 out     # Set WiringPi pin 2 as output")
        print("  gpio write 2 1      # Set WiringPi pin 2 HIGH")
        print("  gpio write 2 0      # Set WiringPi pin 2 LOW")
        
        return physical_pin_7_wpi == 2
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_pin_control():
    """Test controlling physical pin 7"""
    print("\n" + "="*50)
    print("Testing pin control for physical pin 7...")
    
    # Import after environment setup
    import devices
    
    try:
        # Test turning pin 7 on/off
        backend = devices._backend
        
        if hasattr(backend, 'wiringpi') and hasattr(backend, '_board_to_wpi'):
            wpi_pin = backend._board_to_wpi(7)
            print(f"Setting up physical pin 7 (WiringPi {wpi_pin}) as output...")
            
            # This should be equivalent to: gpio mode 2 out
            backend.wiringpi.pinMode(wpi_pin, 1)  # 1 = OUTPUT
            print(f"  Equivalent to: gpio mode {wpi_pin} out")
            
            # Turn ON - equivalent to: gpio write 2 1  
            backend.wiringpi.digitalWrite(wpi_pin, 1)
            print(f"  Pin ON  - Equivalent to: gpio write {wpi_pin} 1")
            
            # Turn OFF - equivalent to: gpio write 2 0
            backend.wiringpi.digitalWrite(wpi_pin, 0) 
            print(f"  Pin OFF - Equivalent to: gpio write {wpi_pin} 0")
            
            print("✅ Pin control test completed successfully")
            return True
        else:
            print("❌ WiringPi backend not available (probably running in mock mode)")
            return False
            
    except Exception as e:
        print(f"❌ Error during pin control: {e}")
        return False

def main():
    print("WiringPi Pin Mapping Verification")
    print("=" * 50)
    
    # Test 1: Verify mapping
    mapping_ok = test_pin_mapping()
    
    # Test 2: Test actual control (will fail in Windows/mock mode)
    control_ok = test_pin_control()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Pin mapping correct: {'✅ YES' if mapping_ok else '❌ NO'}")
    print(f"Pin control works:   {'✅ YES' if control_ok else '❌ NO (expected on Windows)'}")
    
    if mapping_ok:
        print("\n✅ The backend will correctly control physical pin 7 as WiringPi pin 2")
        print("   Command: python pin_control.py 7 on")
        print("   Equivalent to: gpio mode 2 out; gpio write 2 1")
    
    return 0 if mapping_ok else 1

if __name__ == "__main__":
    sys.exit(main())