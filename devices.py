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


# --- Autowybór backendu -----------------------------------------------------

def _should_force_mock() -> bool:
    # Ustaw FORCE_MOCK=1, by wymusić mock nawet na OPi
    if os.getenv("FORCE_MOCK", "").strip() in {"1", "true", "True"}:
        return True
    # Windows -> zawsze mock
    if os.name == "nt":
        return True
    return False


def _make_backend():
    if _should_force_mock():
        return MockBackend()
    try:
        import OPi.GPIO  # noqa: F401
        return OPiGPIOBackend()
    except Exception:
        # brak OPi.GPIO lub błąd inicjalizacji -> mock
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


# Opcjonalnie: sprzątanie przy wyjściu
import atexit
atexit.register(cleanup)
