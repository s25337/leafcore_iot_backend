# Orange Pi Zero 2W - WiringPi Setup Guide

This guide explains how to set up and use WiringPi library for GPIO control on Orange Pi Zero 2W with debugging capabilities.

## Features Added

1. **WiringPiBackend** - New GPIO backend using WiringPi library
2. **Debug Output** - Comprehensive logging for troubleshooting
3. **Pin Mapping** - Automatic conversion from BOARD to WiringPi pin numbering
4. **Fallback System** - Auto-detection of available GPIO libraries
5. **Environment Controls** - Easy switching between backends

## Environment Variables

Control the behavior using these environment variables:

- `USE_WIRINGPI=1` - Force use of WiringPi backend
- `DEBUG_GPIO=1` - Enable detailed debug output (default: enabled)
- `FORCE_MOCK=1` - Force mock backend (no real GPIO)
- `DHT_SENSOR=DHT22` - Specify DHT sensor type (DHT11, DHT22, AM2302)

## Installation on Orange Pi Zero 2W

### 1. Run the setup script:
```bash
chmod +x setup_orangepi.sh
./setup_orangepi.sh
```

### 2. Or install manually:
```bash
# System packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-dev python3-pip build-essential git

# WiringPi system library
cd /tmp
git clone https://github.com/orangepi-xunlong/wiringOP.git
cd wiringOP
sudo ./build clean
sudo ./build

# Python libraries
pip3 install wiringpi Adafruit-DHT flask
```

## Pin Configuration

The system uses BOARD pin numbering (physical pin numbers):

| Function | BOARD Pin | GPIO | WiringPi Pin |
|----------|-----------|------|--------------|
| DHT Sensor | 7 | GPIO4 | 7 |
| Fan Relay | 11 | GPIO17 | 0 |
| Light Relay | 13 | GPIO27 | 2 |
| Pump Relay | 15 | GPIO22 | 3 |

You can modify these in `config.py`.

## Testing

### 1. Basic test (auto-detect backend):
```bash
python3 debug_wiringpi.py
```

### 2. Force WiringPi with debugging:
```bash
USE_WIRINGPI=1 DEBUG_GPIO=1 python3 debug_wiringpi.py
```

### 3. Test specific functions:
```bash
# Test only sensor reading
USE_WIRINGPI=1 python3 -c "import devices; print(devices.read_sensor())"

# Test GPIO control
USE_WIRINGPI=1 python3 -c "import devices; devices.set_fan(True); import time; time.sleep(2); devices.set_fan(False)"
```

## Running the GUI

### 1. With auto-detected backend:
```bash
python3 gui.py
```

### 2. Force WiringPi backend:
```bash
USE_WIRINGPI=1 python3 gui.py
```

### 3. With debugging enabled:
```bash
USE_WIRINGPI=1 DEBUG_GPIO=1 python3 gui.py
```

## Debug Output Examples

When `DEBUG_GPIO=1` is set, you'll see output like:

```
[WiringPi DEBUG] Initializing WiringPi backend...
[WiringPi DEBUG] WiringPi initialized successfully
[WiringPi DEBUG] Pin mapping: {11: 0, 13: 2, 15: 3, 7: 7}
[WiringPi DEBUG] Setup output FAN: BOARD pin 11 -> WiringPi pin 0
[WiringPi DEBUG] Setup output LIGHT: BOARD pin 13 -> WiringPi pin 2
[WiringPi DEBUG] Setup output PUMP: BOARD pin 15 -> WiringPi pin 3
[WiringPi DEBUG] DHT sensor pin: 7, type: DHT22
[WiringPi DEBUG] DHT sensor initialized with Adafruit_DHT
[WiringPi DEBUG] Backend initialization complete
[WiringPi DEBUG] FAN OFF
[WiringPi DEBUG] LIGHT OFF
[WiringPi DEBUG] PUMP OFF
```

## Backend Selection Logic

1. **FORCE_MOCK=1**: Always use mock backend (Windows default)
2. **USE_WIRINGPI=1**: Force WiringPi backend
3. **Auto-detect**: Try WiringPi first, then OPi.GPIO, then mock

## Troubleshooting

### WiringPi not found:
```bash
# Reinstall WiringPi system library
cd /tmp
git clone https://github.com/orangepi-xunlong/wiringOP.git
cd wiringOP
sudo ./build clean
sudo ./build

# Reinstall Python WiringPi
pip3 install --force-reinstall wiringpi
```

### Permission errors:
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Reboot or re-login

# Or run with sudo (not recommended for GUI)
sudo python3 debug_wiringpi.py
```

### DHT sensor issues:
```bash
# Check wiring and sensor type
DHT_SENSOR=DHT11 DEBUG_GPIO=1 python3 debug_wiringpi.py

# Try different delay settings in code
```

### Pin conflicts:
- Check if other processes are using GPIO pins
- Verify pin connections match config.py
- Use debug output to see pin mapping

## File Structure

```
leafcore_iot_backend/
├── devices.py              # Main GPIO backend with WiringPi support
├── config.py               # Pin configuration
├── debug_wiringpi.py       # Debug and test script
├── setup_orangepi.sh       # Installation script
├── requirements-orangepi.txt # Python dependencies
├── gui.py                  # GUI application
└── README_wiringpi.md      # This guide
```

## API Usage

```python
import devices

# Get backend info
print(devices.get_backend_info())
print(devices.get_debug_info())

# Read sensor
temp, humidity = devices.read_sensor()

# Control outputs
devices.set_fan(True)
devices.set_light(True) 
devices.set_pump(True)

# Cleanup
devices.cleanup()
```