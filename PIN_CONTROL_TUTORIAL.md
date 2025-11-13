# Pin Control Tutorial - Jak używać pin_control.py

Prosty tutorial krok po kroku dla sterowania pinami GPIO na Orange Pi Zero 2W.

### 1. Sprawdź dostępne piny
```bash
python pin_control.py list
```
Wyświetla wszystkie dostępne piny GPIO z opisem funkcji.

### 2. Sprawdź status pinów
```bash
python pin_control.py status
```
Pokazuje aktualny stan skonfigurowanych pinów (fan, light, pump).

### 3. Podstawowe sterowanie
```bash
# Włącz pin
python pin_control.py 11 on

# Wyłącz pin  
python pin_control.py 11 off

# Przełącz stan pina
python pin_control.py 11 toggle

# Sprawdź stan pina
python pin_control.py 11 read
```

## 📋 Dostępne komendy

| Komenda | Opis | Przykład |
|---------|------|----------|
| `list` | Pokaż wszystkie dostępne piny | `python pin_control.py list` |
| `status` | Pokaż stan skonfigurowanych pinów | `python pin_control.py status` |
| `<pin> on` | Włącz pin | `python pin_control.py 16 on` |
| `<pin> off` | Wyłącz pin | `python pin_control.py 16 off` |
| `<pin> toggle` | Przełącz stan pina | `python pin_control.py 16 toggle` |
| `<pin> read` | Odczytaj stan pina | `python pin_control.py 16 read` |
| `<pin> on <czas>` | Włącz pin na określony czas | `python pin_control.py 16 on 5` |


### Sterowanie dowolnymi pinami GPIO
```bash
# Kontroluj pin 16 (PH04)
python pin_control.py 16 on
python pin_control.py 16 off

# Pin 26 na 3 sekundy
python pin_control.py 26 on 3

# Przełącz pin 29
python pin_control.py 29 toggle
```

### Odczyt sensora (pin 7)
```bash
# Odczytaj temperaturę i wilgotność
python pin_control.py 7 read
```

## ⚠️ Ostrzeżenia dla specjalnych pinów

Program automatycznie ostrzeże przed użyciem pinów o specjalnych funkcjach:

- **Piny 3,5**: I2C (SDA, SCL)
- **Piny 8,10**: UART (TX, RX)  
- **Piny 13,15,18-24**: Komunikacja SPI/serial

```bash
# Przykład ostrzeżenia
$ python pin_control.py 3 on
WARNING: Pin 3 is I2C (SDA.1 (I2C))
This may interfere with I2C devices. Continue? (y/N): 
```

## 🔧 Konfiguracja środowiska

### Zmienne środowiskowe
```bash
# Wymuś backend WiringPi
export USE_WIRINGPI=1

# Wyłącz debug (domyślnie włączony)
export DEBUG_GPIO=0

# Wymuś tryb symulacji
export FORCE_MOCK=1

# Ustaw typ sensora DHT
export DHT_SENSOR=DHT11
```

### Przykład z ustawieniami
```bash
# Użyj WiringPi z debugiem
USE_WIRINGPI=1 DEBUG_GPIO=1 python pin_control.py 11 on

# Tryb cichy (bez debug)
DEBUG_GPIO=0 python pin_control.py 13 toggle
```

## 📍 Mapowanie pinów

### Bezpieczne piny do użytku (★ = skonfigurowane)
- **Pin 11** ★ - Fan (PI01)
- **Pin 16** - PH04
- **Pin 19** - RXD.2
- **Pin 26** - PI00
- **Pin 29** - PI15
- **Pin 31** - PI12
- **Pin 33** - PI02
- **Pin 35** - PC12
- **Pin 37** - PI16
- **Pin 38** - PI04
- **Pin 40** - PI03

### PWM piny
- **Pin 7** ★ - PWM3 (sensor DHT)
- **Pin 12** - PWM4
- **Pin 32** - PWM1

## 🔍 Przykładowy workflow

```bash
# 1. Zobacz dostępne piny
python pin_control.py list

# 2. Sprawdź aktualny status
python pin_control.py status

# 3. Włącz LED na pin 16
python pin_control.py 16 on

# 4. Sprawdź czy działa
python pin_control.py 16 read

# 5. Wyłącz po 5 sekundach  
python pin_control.py 16 on 5

# 6. Odczytaj sensor
python pin_control.py 7 read
```

## 🚨 Rozwiązywanie problemów

### Backend nie działa
```bash
# Sprawdź jaki backend jest używany
python pin_control.py status

# Wymuś WiringPi
USE_WIRINGPI=1 python pin_control.py status

# Debug mode
DEBUG_GPIO=1 python pin_control.py 11 on
```

### Błędy uprawnień
```bash
# Dodaj się do grupy gpio
sudo usermod -a -G gpio $USER

# Lub uruchom z sudo (niezalecane dla GUI)
sudo python pin_control.py 11 on
```

### Pin nie odpowiada
1. Sprawdź fizyczne połączenia
2. Upewnij się, że pin nie jest używany przez inny proces
3. Sprawdź mapping pinów: `python pin_control.py list`

## 💡 Wskazówki

- **Zawsze sprawdź listę pinów** przed pierwszym użyciem
- **Unikaj pinów I2C/UART** jeśli nie musisz
- **Używaj debug mode** do diagnozowania problemów
- **Sprawdź status** przed i po operacjach
- **Używaj timeout** dla czasowych włączeń