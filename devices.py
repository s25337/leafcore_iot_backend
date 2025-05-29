# devices.py

import Adafruit_DHT
import RPi.GPIO as GPIO
import config

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(config.FAN_PIN, GPIO.OUT)
GPIO.setup(config.LIGHT_PIN, GPIO.OUT)
GPIO.setup(config.PUMP_PIN, GPIO.OUT)

def read_sensor():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, config.TEMP_HUMIDITY_SENSOR_PIN)
    return temperature, humidity

def set_fan(state):
    GPIO.output(config.FAN_PIN, GPIO.HIGH if state else GPIO.LOW)

def set_light(state):
    GPIO.output(config.LIGHT_PIN, GPIO.HIGH if state else GPIO.LOW)

def set_pump(state):
    GPIO.output(config.PUMP_PIN, GPIO.HIGH if state else GPIO.LOW)
