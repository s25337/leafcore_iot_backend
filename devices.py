# devices.py
import os
import random
import time
from typing import Tuple, Optional

try:
    import config  # expects pins: TEMP_HUMIDITY_SENSOR_PIN, FAN_PIN, LIGHT_PIN, PUMP_PIN
except Exception as e:
    raise RuntimeError("Brak pliku config.py z definicją pinów!") from e


# --- Backendy ---------------------------------------------------------------

class BaseBackend:
    def __init__(self):
        self._fan_state = False
        self._light_state = False
        self._pump_state = False

    # OUTPUTS
    def set_fan(self, state: bool) -> None:
        self._fan_state = bool(state)

    def set_light(self, state: bool) -> None:
        self._light_state = bool(state)

    def set_pump(self, state: bool) -> None:
        self._pump_state = bool(state)

    # INPUTS
    def read_sensor(self) -> Tuple[Optional[float], Optional[float]]:
        """Return (temperature_C, humidity_percent) or (None, None) if unavailable."""
        return None, None

    def cleanup(self) -> None:
        pass


class MockBackend(BaseBackend):
    """Działa wszędzie (Windows/Linux) bez GPIO.losowe wartości."""
    def __init__(self):
        super().__init__()
        self._temp = 22.0 + random.uniform(-1.0, 1.0)
        self._hum = 60.0 + random.uniform(-3.0, 3.0)
        self._last_update = 0.0

    def _drift(self):
        # lekki dryf co ~1 s
        now = time.time()
        if now - self._last_update > 1.0:
            self._last_update = now
            #  wiatrak ON -> obniż wilgotność delikatnie
            if self._fan_state:
                self._hum += random.uniform(-0.6, 0.0)
            else:
                self._hum += random.uniform(-0.2, 0.3)

            # światło ON -> lekko podnosi temperaturę
            if self._light_state:
                self._temp += random.uniform(0.0, 0.15)
            else:
                self._temp += random.uniform(-0.08, 0.05)

            # pompka ON -> chwilowo podnosi wilgotność
            if self._pump_state:
                self._hum += random.uniform(0.3, 0.8)

            # ograniczenia
            self._temp = max(10.0, min(35.0, self._temp))
            self._hum = max(20.0, min(95.0, self._hum))

    def read_sensor(self) -> Tuple[float, float]:
        self._drift()
        return round(self._temp, 1), round(self._hum, 1)


class OPiGPIOBackend(BaseBackend):
    """Backend dla Orange Pi Zero 2W z OPi.GPIO. Steruje wyjściami i próbuje odczytu DHT."""
    def __init__(self):
        super().__init__()

        # OPi.GPIO
        import OPi.GPIO as GPIO  # type: ignore
        self.GPIO = GPIO

        # Tryb numeracji: używamy fizycznych numerów pinów (BOARD),
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # Ustaw wyjścia
        self._setup_output(config.FAN_PIN, name="FAN")
        self._setup_output(config.LIGHT_PIN, name="LIGHT")
        self._setup_output(config.PUMP_PIN, name="PUMP")

        # SENSORY (DHT)
        self._dht_pin = getattr(config, "TEMP_HUMIDITY_SENSOR_PIN", None)
        self._dht = None
        self._dht_sensor_type = os.getenv("DHT_SENSOR", "DHT22").upper()

        # Spróbuj kilku popularnych bibliotek:
        # 1) OrangePi_DHT (często polecana na OPi)
        # 2) Adafruit_DHT (czasem działa, ale bywa kapryśna na OPi)
        # Jeśli nic nie zadziała -> zostaw _dht=None i zwracaj (None, None).

        # OrangePi_DHT
        try:
            import OrangePi_DHT  # type: ignore
            # Mapowanie typu
            sensor_map = {
                "DHT11": OrangePi_DHT.DHT11,
                "DHT22": OrangePi_DHT.DHT22,
                "AM2302": OrangePi_DHT.DHT22,
            }
            sensor_cls = sensor_map.get(self._dht_sensor_type, OrangePi_DHT.DHT22)

            # W OrangePi_DHT pin zwykle w trybie BOARD:
            # Jeśli biblioteka wymaga 'GPIO.BOARD' numeru – mamy spójność.
            self._dht = ("orangepi_dht", sensor_cls(self._dht_pin))
        except Exception:
            self._dht = None

        # Adafruit_DHT (fallback)
        if self._dht is None:
            try:
                import Adafruit_DHT  # type: ignore
                sensor_map = {
                    "DHT11": Adafruit_DHT.DHT11,
                    "DHT22": Adafruit_DHT.DHT22,
                    "AM2302": Adafruit_DHT.AM2302,
                }
                sensor = sensor_map.get(self._dht_sensor_type, Adafruit_DHT.DHT22)
                self._dht = ("adafruit_dht", (Adafruit_DHT, sensor))
            except Exception:
                self._dht = None

        # Wystartuj wyjścia w pozycji OFF
        self.set_fan(False)
        self.set_light(False)
        self.set_pump(False)

    def _setup_output(self, pin: int, name: str = ""):
        self.GPIO.setup(pin, self.GPIO.OUT, initial=self.GPIO.LOW)

    # OUTPUTS
    def _write_pin(self, pin: int, state: bool):
        self.GPIO.output(pin, self.GPIO.HIGH if state else self.GPIO.LOW)

    def set_fan(self, state: bool) -> None:
        super().set_fan(state)
        self._write_pin(config.FAN_PIN, state)

    def set_light(self, state: bool) -> None:
        super().set_light(state)
        self._write_pin(config.LIGHT_PIN, state)

    def set_pump(self, state: bool) -> None:
        super().set_pump(state)
        self._write_pin(config.PUMP_PIN, state)

    # INPUTS
    def read_sensor(self) -> Tuple[Optional[float], Optional[float]]:
        if not self._dht or self._dht_pin is None:
            return None, None

        kind = self._dht[0]

        try:
            if kind == "orangepi_dht":
                sensor = self._dht[1]
                # .read() zwykle zwraca (temp, hum) lub dict – zależnie od wersji
                data = sensor.read()
                if isinstance(data, dict):
                    temp = data.get("temperature")
                    hum = data.get("humidity")
                else:
                    # zakładamy krotkę (temp, hum)
                    temp, hum = data
                # sanity check
                if temp is None or hum is None:
                    return None, None
                return float(temp), float(hum)

            elif kind == "adafruit_dht":
                Adafruit_DHT, sensor = self._dht[1]
                # Uwaga: Adafruit_DHT zwykle używa numeracji BCM,
                # ale na OPi bywa patchowana – jeśli odczyty są None,
                # rozważ zmianę numeracji lub użycie OrangePi_DHT.
                hum, temp = Adafruit_DHT.read_retry(sensor, self._dht_pin)
                if temp is None or hum is None:
                    return None, None
                return float(temp), float(hum)

        except Exception:
            return None, None

        return None, None

    def cleanup(self) -> None:
        try:
            self.GPIO.cleanup()
        except Exception:
            pass


class WiringPiBackend(BaseBackend):
    """Backend dla Orange Pi Zero 2W z WiringPi. Steruje wyjściami i próbuje odczytu DHT z debugowaniem."""
    def __init__(self, debug=True):
        super().__init__()
        self.debug = debug
        
        try:
            import wiringpi  # type: ignore
            self.wiringpi = wiringpi
        except ImportError as e:
            raise RuntimeError("WiringPi library not found! Install it with: pip install wiringpi") from e

        if self.debug:
            print(f"[WiringPi DEBUG] Initializing WiringPi backend...")

        # Initialize WiringPi - używamy WiringPi pin numbering
        if self.wiringpi.wiringPiSetup() == -1:
            raise RuntimeError("Failed to initialize WiringPi!")
        
        if self.debug:
            print(f"[WiringPi DEBUG] WiringPi initialized successfully")

        # Mapowanie pinów z BOARD na WiringPi numbering
        # Orange Pi Zero 2W pin mapping (przykładowe)
        self.pin_map = {
            config.FAN_PIN: self._board_to_wpi(config.FAN_PIN),
            config.LIGHT_PIN: self._board_to_wpi(config.LIGHT_PIN), 
            config.PUMP_PIN: self._board_to_wpi(config.PUMP_PIN),
            getattr(config, "TEMP_HUMIDITY_SENSOR_PIN", 7): self._board_to_wpi(getattr(config, "TEMP_HUMIDITY_SENSOR_PIN", 7))
        }
        
        if self.debug:
            print(f"[WiringPi DEBUG] Pin mapping: {self.pin_map}")

        # Ustaw wyjścia
        self._setup_output(config.FAN_PIN, name="FAN")
        self._setup_output(config.LIGHT_PIN, name="LIGHT")
        self._setup_output(config.PUMP_PIN, name="PUMP")

        # SENSORY (DHT)
        self._dht_pin = getattr(config, "TEMP_HUMIDITY_SENSOR_PIN", None)
        self._dht_sensor_type = os.getenv("DHT_SENSOR", "DHT22").upper()
        
        if self.debug:
            print(f"[WiringPi DEBUG] DHT sensor pin: {self._dht_pin}, type: {self._dht_sensor_type}")

        # Próbuj zainicjalizować sensor DHT
        self._dht_lib = None
        self._init_dht_sensor()

        # Wystartuj wyjścia w pozycji OFF
        self.set_fan(False)
        self.set_light(False)
        self.set_pump(False)

        if self.debug:
            print(f"[WiringPi DEBUG] Backend initialization complete")

    def _board_to_wpi(self, board_pin):
        """Konwertuje BOARD pin number na WiringPi pin number dla Orange Pi Zero 2W"""
        # Orange Pi Zero 2W pin mapping based on gpio readall output
        board_to_wpi_map = {
            3: 8,    # SDA.1 -> WiringPi 8
            5: 1,    # SCL.1 -> WiringPi 1
            7: 2,    # PWM3 -> WiringPi 2
            8: 3,    # TXD.0 -> WiringPi 3
            10: 4,   # RXD.0 -> WiringPi 4
            11: 6,   # PI01 -> WiringPi 6
            12: 9,   # PWM4 -> WiringPi 9
            13: 11,  # MOSI.1 -> WiringPi 11
            15: 12,  # MISO.1 -> WiringPi 12
            16: 10,  # PH04 -> WiringPi 10
            18: 14,  # SCLK.1 -> WiringPi 14
            19: 13,  # RXD.2 -> WiringPi 13
            21: 15,  # CE.0 -> WiringPi 15
            22: 16,  # CE.1 -> WiringPi 16
            23: 18,  # SCL.2 -> WiringPi 18
            24: 17,  # SDA.2 -> WiringPi 17
            26: 19,  # PI00 -> WiringPi 19
            29: 20,  # PI15 -> WiringPi 20
            31: 22,  # PI12 -> WiringPi 22
            32: 21,  # PWM1 -> WiringPi 21
            33: 23,  # PI02 -> WiringPi 23
            35: 24,  # PC12 -> WiringPi 24
            37: 25,  # PI16 -> WiringPi 25
            38: 26,  # PI04 -> WiringPi 26
            40: 27,  # PI03 -> WiringPi 27
        }
        
        wpi_pin = board_to_wpi_map.get(board_pin, board_pin)
        if self.debug:
            print(f"[WiringPi DEBUG] Mapping BOARD pin {board_pin} -> WiringPi pin {wpi_pin}")
        return wpi_pin

    def _init_dht_sensor(self):
        """Inicjalizuje bibliotekę DHT"""
        try:
            import Adafruit_DHT  # type: ignore
            sensor_map = {
                "DHT11": Adafruit_DHT.DHT11,
                "DHT22": Adafruit_DHT.DHT22,
                "AM2302": Adafruit_DHT.AM2302,
            }
            self._dht_lib = ("adafruit", Adafruit_DHT, sensor_map.get(self._dht_sensor_type, Adafruit_DHT.DHT22))
            if self.debug:
                print(f"[WiringPi DEBUG] DHT sensor initialized with Adafruit_DHT")
        except ImportError:
            if self.debug:
                print(f"[WiringPi DEBUG] Adafruit_DHT not available, DHT sensor disabled")
            self._dht_lib = None

    def _setup_output(self, board_pin: int, name: str = ""):
        """Konfiguruje pin jako wyjście"""
        wpi_pin = self.pin_map[board_pin]
        self.wiringpi.pinMode(wpi_pin, 1)  # 1 = OUTPUT
        self.wiringpi.digitalWrite(wpi_pin, 0)  # Start LOW
        if self.debug:
            print(f"[WiringPi DEBUG] Setup output {name}: BOARD pin {board_pin} -> WiringPi pin {wpi_pin}")

    def _write_pin(self, board_pin: int, state: bool):
        """Zapisuje stan na pin"""
        wpi_pin = self.pin_map[board_pin]
        value = 1 if state else 0
        self.wiringpi.digitalWrite(wpi_pin, value)
        if self.debug:
            print(f"[WiringPi DEBUG] Pin {board_pin} (WiringPi {wpi_pin}) set to {'HIGH' if state else 'LOW'}")

    # OUTPUTS
    def set_fan(self, state: bool) -> None:
        super().set_fan(state)
        self._write_pin(config.FAN_PIN, state)
        if self.debug:
            print(f"[WiringPi DEBUG] FAN {'ON' if state else 'OFF'}")

    def set_light(self, state: bool) -> None:
        super().set_light(state)
        self._write_pin(config.LIGHT_PIN, state)
        if self.debug:
            print(f"[WiringPi DEBUG] LIGHT {'ON' if state else 'OFF'}")

    def set_pump(self, state: bool) -> None:
        super().set_pump(state)
        self._write_pin(config.PUMP_PIN, state)
        if self.debug:
            print(f"[WiringPi DEBUG] PUMP {'ON' if state else 'OFF'}")

    # INPUTS
    def read_sensor(self) -> Tuple[Optional[float], Optional[float]]:
        """Odczytuje dane z sensora DHT"""
        if not self._dht_lib or self._dht_pin is None:
            if self.debug:
                print(f"[WiringPi DEBUG] DHT sensor not available")
            return None, None

        lib_type, Adafruit_DHT, sensor_type = self._dht_lib
        
        try:
            if self.debug:
                print(f"[WiringPi DEBUG] Reading DHT sensor on pin {self._dht_pin}...")
                
            # Użyj BOARD pin number dla Adafruit_DHT
            humidity, temperature = Adafruit_DHT.read_retry(sensor_type, self._dht_pin, retries=3, delay_seconds=0.5)
            
            if temperature is not None and humidity is not None:
                temp_c = round(float(temperature), 1)
                hum_pct = round(float(humidity), 1)
                
                if self.debug:
                    print(f"[WiringPi DEBUG] Sensor reading: {temp_c}°C, {hum_pct}% RH")
                
                # Sprawdź czy wartości są rozsądne
                if -40 <= temp_c <= 80 and 0 <= hum_pct <= 100:
                    return temp_c, hum_pct
                else:
                    if self.debug:
                        print(f"[WiringPi DEBUG] Sensor values out of range: {temp_c}°C, {hum_pct}% RH")
                    return None, None
            else:
                if self.debug:
                    print(f"[WiringPi DEBUG] Failed to read sensor data")
                return None, None
                
        except Exception as e:
            if self.debug:
                print(f"[WiringPi DEBUG] Sensor read error: {e}")
            return None, None

    def cleanup(self) -> None:
        """Czyści zasoby"""
        try:
            # Wyłącz wszystkie wyjścia
            self.set_fan(False)
            self.set_light(False)
            self.set_pump(False)
            if self.debug:
                print(f"[WiringPi DEBUG] Cleanup complete")
        except Exception as e:
            if self.debug:
                print(f"[WiringPi DEBUG] Cleanup error: {e}")


# --- Autowybór backendu -----------------------------------------------------

def _should_force_mock() -> bool:
    # Ustaw FORCE_MOCK=1, by wymusić mock nawet na OPi
    if os.getenv("FORCE_MOCK", "").strip() in {"1", "true", "True"}:
        return True
    # Windows -> zawsze mock
    if os.name == "nt":
        return True
    return False


def _should_use_wiringpi() -> bool:
    # Ustaw USE_WIRINGPI=1, by wymusić WiringPi
    return os.getenv("USE_WIRINGPI", "").strip() in {"1", "true", "True"}


def _should_debug() -> bool:
    # Ustaw DEBUG_GPIO=1, by włączyć debug
    return os.getenv("DEBUG_GPIO", "1").strip() in {"1", "true", "True"}


def _make_backend():
    if _should_force_mock():
        print("[BACKEND] Using MockBackend (forced)")
        return MockBackend()
    
    debug_mode = _should_debug()
    
    # Najpierw spróbuj WiringPi jeśli wymuszony lub dostępny
    if _should_use_wiringpi():
        try:
            print("[BACKEND] Attempting WiringPi backend (forced)...")
            return WiringPiBackend(debug=debug_mode)
        except Exception as e:
            print(f"[BACKEND] WiringPi backend failed: {e}")
    else:
        # Auto-detect: spróbuj WiringPi najpierw
        try:
            import wiringpi  # noqa: F401
            print("[BACKEND] WiringPi available, trying WiringPi backend...")
            return WiringPiBackend(debug=debug_mode)
        except ImportError:
            print("[BACKEND] WiringPi not available, trying OPi.GPIO...")
        except Exception as e:
            print(f"[BACKEND] WiringPi backend failed: {e}, trying OPi.GPIO...")
    
    # Fallback do OPi.GPIO
    try:
        import OPi.GPIO  # noqa: F401
        print("[BACKEND] Using OPiGPIOBackend")
        return OPiGPIOBackend()
    except Exception as e:
        print(f"[BACKEND] OPi.GPIO backend failed: {e}, using MockBackend")
        return MockBackend()


_backend: BaseBackend = _make_backend()


# --- API modułu używane przez Twoją aplikację --------------------------------

def read_sensor() -> Tuple[Optional[float], Optional[float]]:
    return _backend.read_sensor()


def set_fan(state: bool) -> None:
    _backend.set_fan(state)


def set_light(state: bool) -> None:
    _backend.set_light(state)


def set_pump(state: bool) -> None:
    _backend.set_pump(state)


def cleanup() -> None:
    _backend.cleanup()


def get_backend_info() -> str:
    """Zwraca informację o aktualnie używanym backendzie"""
    backend_type = type(_backend).__name__
    return f"Current backend: {backend_type}"


def get_debug_info() -> dict:
    """Zwraca informacje debugowe o backendzie"""
    info = {
        "backend_type": type(_backend).__name__,
        "environment_vars": {
            "FORCE_MOCK": os.getenv("FORCE_MOCK", ""),
            "USE_WIRINGPI": os.getenv("USE_WIRINGPI", ""),
            "DEBUG_GPIO": os.getenv("DEBUG_GPIO", ""),
            "DHT_SENSOR": os.getenv("DHT_SENSOR", "DHT22")
        }
    }
    
    if hasattr(_backend, 'debug'):
        info["debug_enabled"] = _backend.debug
    if hasattr(_backend, 'pin_map'):
        info["pin_mapping"] = _backend.pin_map
        
    return info


# Opcjonalnie: sprzątanie przy wyjściu
import atexit
atexit.register(cleanup)
