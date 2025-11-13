#!/bin/bash
# Setup script for Orange Pi Zero 2W GPIO libraries
# Run this script on your Orange Pi to install required dependencies

echo "=== Orange Pi Zero 2W GPIO Setup ==="
echo "This script will install required libraries for GPIO control"
echo

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python development packages
echo "Installing Python development packages..."
sudo apt install -y python3-dev python3-pip python3-venv

# Install GPIO libraries build dependencies
echo "Installing build dependencies..."
sudo apt install -y build-essential git

# Install WiringPi for Orange Pi
echo "Installing WiringPi for Orange Pi..."
cd /tmp
git clone https://github.com/orangepi-xunlong/wiringOP.git
cd wiringOP
sudo ./build clean
sudo ./build

# Install Python WiringPi
echo "Installing Python WiringPi library..."
pip3 install wiringpi

# Install DHT sensor libraries
echo "Installing DHT sensor libraries..."
pip3 install Adafruit-DHT

# Try to install OrangePi-specific DHT library (if available)
echo "Attempting to install OrangePi DHT library..."
pip3 install OrangePi-DHT || echo "OrangePi-DHT not available, continuing..."

# Install other Python dependencies
echo "Installing other dependencies..."
pip3 install flask

echo
echo "=== Setup Complete ==="
echo "Libraries installed:"
echo "- WiringPi (system and Python)"
echo "- Adafruit_DHT"
echo "- Flask"
echo
echo "Next steps:"
echo "1. Copy your project files to Orange Pi"
echo "2. Test with: python3 debug_wiringpi.py"
echo "3. Use USE_WIRINGPI=1 to force WiringPi backend"
echo "4. Use DEBUG_GPIO=1 for debugging output"
echo
echo "Example usage:"
echo "  USE_WIRINGPI=1 DEBUG_GPIO=1 python3 debug_wiringpi.py"
echo "  USE_WIRINGPI=1 python3 gui.py"