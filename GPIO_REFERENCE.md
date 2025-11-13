# Orange Pi Zero 2W GPIO Pin Reference

Based on `gpio readall` output, here's the complete pin mapping:

## Physical Pin Layout (40-pin header)

```
     3.3V  [1] [2]  5V
    SDA.1  [3] [4]  5V
    SCL.1  [5] [6]  GND
     PWM3  [7] [8]  TXD.0
      GND  [9][10]  RXD.0
     PI01 [11][12]  PWM4
   MOSI.1 [13][14]  GND
   MISO.1 [15][16]  PH04
     3.3V [17][18]  SCLK.1
    RXD.2 [19][20]  GND
     CE.0 [21][22]  CE.1
    SCL.2 [23][24]  SDA.2
      GND [25][26]  PI00
     PI15 [29][30]  GND
     PI12 [31][32]  PWM1
     PI02 [33][34]  GND
     PC12 [35][36]  PI16
     PI16 [37][38]  PI04
      GND [39][40]  PI03
```

## Pin Mapping Table

| BOARD | Name    | WiringPi | Function        | Safe for GPIO? |
|-------|---------|----------|-----------------|----------------|
| 3     | SDA.1   | 8        | I2C Data        | ⚠️ Caution     |
| 5     | SCL.1   | 1        | I2C Clock       | ⚠️ Caution     |
| 7     | PWM3    | 2        | PWM/GPIO        | ✅ Good        |
| 8     | TXD.0   | 3        | UART TX         | ⚠️ Caution     |
| 10    | RXD.0   | 4        | UART RX         | ⚠️ Caution     |
| 11    | PI01    | 6        | GPIO            | ✅ Good        |
| 12    | PWM4    | 9        | PWM/GPIO        | ✅ Good        |
| 13    | MOSI.1  | 11       | SPI/GPIO        | ⚠️ Caution     |
| 15    | MISO.1  | 12       | SPI/GPIO        | ⚠️ Caution     |
| 16    | PH04    | 10       | GPIO            | ✅ Good        |
| 18    | SCLK.1  | 14       | SPI Clock/GPIO  | ⚠️ Caution     |
| 19    | RXD.2   | 13       | GPIO            | ✅ Good        |
| 21    | CE.0    | 15       | SPI CS/GPIO     | ⚠️ Caution     |
| 22    | CE.1    | 16       | SPI CS/GPIO     | ⚠️ Caution     |
| 23    | SCL.2   | 18       | I2C Clock/GPIO  | ⚠️ Caution     |
| 24    | SDA.2   | 17       | I2C Data/GPIO   | ⚠️ Caution     |
| 26    | PI00    | 19       | GPIO            | ✅ Good        |
| 29    | PI15    | 20       | GPIO            | ✅ Good        |
| 31    | PI12    | 22       | GPIO            | ✅ Good        |
| 32    | PWM1    | 21       | PWM/GPIO        | ✅ Good        |
| 33    | PI02    | 23       | GPIO            | ✅ Good        |
| 35    | PC12    | 24       | GPIO            | ✅ Good        |
| 37    | PI16    | 25       | GPIO            | ✅ Good        |
| 38    | PI04    | 26       | GPIO            | ✅ Good        |
| 40    | PI03    | 27       | GPIO            | ✅ Good        |

## Best GPIO Pins for General Use

**Recommended for relays/outputs:**
- Pin 11 (PI01) - Fan control ⭐
- Pin 16 (PH04) 
- Pin 19 (RXD.2)
- Pin 26 (PI00)
- Pin 29 (PI15)
- Pin 31 (PI12)
- Pin 33 (PI02)
- Pin 35 (PC12)
- Pin 37 (PI16)  
- Pin 38 (PI04)
- Pin 40 (PI03)

**Good for PWM:**
- Pin 7 (PWM3) - Sensor input ⭐
- Pin 12 (PWM4)
- Pin 32 (PWM1)

**Avoid unless necessary:**
- Pins 3,5 (I2C)
- Pins 8,10 (UART - used for console)
- Pins 13,15,18,21,22,23,24 (SPI functions)

## Usage Examples

```bash
# Safe GPIO pins
python pin_control.py 11 on        # Fan (recommended)
python pin_control.py 16 toggle    # PH04
python pin_control.py 26 on 5      # PI00 for 5 seconds

# PWM pins  
python pin_control.py 7 read       # PWM3 (sensor)
python pin_control.py 32 on        # PWM1

# Communication pins (with warnings)
python pin_control.py 13 on        # MOSI.1 (will warn)
python pin_control.py 3 on         # I2C (will warn)
```