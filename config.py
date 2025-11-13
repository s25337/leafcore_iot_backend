# config.py
# Orange Pi Zero 2W Pin Configuration
# Using BOARD pin numbering (physical pin numbers on the 40-pin header)
# Based on actual gpio readall output from Orange Pi Zero 2W

# DHT22/DHT11 Temperature & Humidity Sensor
TEMP_HUMIDITY_SENSOR_PIN = 7   # BOARD pin 7 (PWM3, WiringPi 2)

# Fan control relay
FAN_PIN = 11                   # BOARD pin 11 (PI01, WiringPi 6)

# Light control relay  
LIGHT_PIN = 13                 # BOARD pin 13 (MOSI.1, WiringPi 11)

# Water pump control relay
PUMP_PIN = 15                  # BOARD pin 15 (MISO.1, WiringPi 12)

# Pin mapping reference for Orange Pi Zero 2W (BOARD -> Name -> WiringPi):
# Pin 3  -> SDA.1 (I2C) -> WPi 8
# Pin 5  -> SCL.1 (I2C) -> WPi 1
# Pin 7  -> PWM3 -> WPi 2
# Pin 8  -> TXD.0 (UART) -> WPi 3
# Pin 10 -> RXD.0 (UART) -> WPi 4
# Pin 11 -> PI01 -> WPi 6
# Pin 12 -> PWM4 -> WPi 9
# Pin 13 -> MOSI.1 -> WPi 11
# Pin 15 -> MISO.1 -> WPi 12
# Pin 16 -> PH04 -> WPi 10
# Pin 18 -> SCLK.1 -> WPi 14
# Pin 19 -> RXD.2 -> WPi 13
# Pin 21 -> CE.0 -> WPi 15
# Pin 22 -> CE.1 -> WPi 16
# Pin 23 -> SCL.2 -> WPi 18
# Pin 24 -> SDA.2 -> WPi 17
# Pin 26 -> PI00 -> WPi 19
# Pin 29 -> PI15 -> WPi 20
# Pin 31 -> PI12 -> WPi 22
# Pin 32 -> PWM1 -> WPi 21
# Pin 33 -> PI02 -> WPi 23
# Pin 35 -> PC12 -> WPi 24
# Pin 37 -> PI16 -> WPi 25
# Pin 38 -> PI04 -> WPi 26
# Pin 40 -> PI03 -> WPi 27

# Notes:
# - Avoid pins 3,5 (I2C), 8,10 (UART) for general GPIO unless necessary
# - PWM pins (7,12,32) can be used for PWM control
# - SPI pins (13,15,18) are used here but could conflict with SPI devices
