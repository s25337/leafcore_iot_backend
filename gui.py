import PySimpleGUI as sg
import time
from datetime import datetime, timedelta
import devices  # moduł do obsługi pinów i sensorów (musisz zaimplementować)

sg.theme('LightGreen')

layout = [
    [sg.Text('Smart Szklarnia', font=('Any', 20), justification='center', expand_x=True)],

    # Czujniki
    [sg.Text('Temperatura:', size=(15,1)), sg.Text('', key='-TEMP-')],
    [sg.Text('Wilgotność:', size=(15,1)), sg.Text('', key='-HUM-')],

    # Sterowanie ręczne
    [sg.Button('Wiatrak OFF', key='-FAN-', size=(10,2), button_color=('white', 'red')),
     sg.Button('Światło OFF', key='-LIGHT-', size=(10,2), button_color=('white', 'red')),
     sg.Button('Pompka OFF', key='-PUMP-', size=(10,2), button_color=('white', 'red'))],

    [sg.HorizontalSeparator()],

    # Ustawienia automatyczne
    [sg.Checkbox('Tryb automatyczny', key='-AUTO-')],
    [sg.Text('Światło (godzin/24h):'), sg.Input('12', key='-LIGHT_HOURS-', size=(5,1))],
    [sg.Text('Temperatura docelowa (°C):'), sg.Input('22', key='-TARGET_TEMP-', size=(5,1))],
    [sg.Text('Wilgotność docelowa (%):'), sg.Input('60', key='-TARGET_HUM-', size=(5,1))],
    [sg.Text('Nawodnienie (razy/tydzień):'), sg.Input('3', key='-WATER_TIMES-', size=(5,1))],
    [sg.Text('Czas podlewania (sekundy):'), sg.Input('10', key='-WATER_SECONDS-', size=(5,1))],

    [sg.Button('Odśwież dane', key='-REFRESH-', size=(20,1))],
    [sg.Multiline(size=(50, 6), key='-LOG-', autoscroll=True, disabled=True)],
]

window = sg.Window('Smart Szklarnia', layout, finalize=True, resizable=True)

fan_on = False
light_on = False
pump_on = False

# Zmienna do śledzenia podlewania
last_watering_times = []

def log(text):
    window['-LOG-'].update(text + '\n', append=True)

def update_sensor_values():
    temp, hum = devices.read_sensor()
    window['-TEMP-'].update(f"{temp:.1f} °C" if temp else "Brak odczytu")
    window['-HUM-'].update(f"{hum:.1f} %" if hum else "Brak odczytu")
    return temp, hum

def set_devices(fan, light, pump):
    devices.set_fan(fan)
    devices.set_light(light)
    devices.set_pump(pump)

def should_water(today, water_days, water_times_per_week):
    # Sprawdzamy, czy dzisiaj podlewać (np. równomiernie co kilka dni)
    interval = 7 / water_times_per_week
    return (today - water_days[0]).days >= interval if water_days else True

update_sensor_values()

while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED:
        break

    temp, hum = update_sensor_values()

    if event == '-FAN-':
        fan_on = not fan_on
        devices.set_fan(fan_on)
        window['-FAN-'].update('Wiatrak ON' if fan_on else 'Wiatrak OFF',
                               button_color=('white', 'green') if fan_on else ('white', 'red'))

    if event == '-LIGHT-':
        light_on = not light_on
        devices.set_light(light_on)
        window['-LIGHT-'].update('Światło ON' if light_on else 'Światło OFF',
                                 button_color=('white', 'green') if light_on else ('white', 'red'))

    if event == '-PUMP-':
        pump_on = not pump_on
        devices.set_pump(pump_on)
        window['-PUMP-'].update('Pompka ON' if pump_on else 'Pompka OFF',
                                button_color=('white', 'green') if pump_on else ('white', 'red'))

    # Sterowanie automatyczne
    if values['-AUTO-']:
        # Światło wg godzin
        try:
            target_light_hours = float(values['-LIGHT_HOURS-'])
            current_hour = datetime.now().hour
            light_on = current_hour < target_light_hours
        except:
            light_on = False

        devices.set_light(light_on)
        window['-LIGHT-'].update('Światło ON' if light_on else 'Światło OFF',
                                 button_color=('white', 'green') if light_on else ('white', 'red'))

        # Temperatura docelowa - prosty regulator
        try:
            target_temp = float(values['-TARGET_TEMP-'])
        except:
            target_temp = None

        # Wilgotność docelowa
        try:
            target_hum = float(values['-TARGET_HUM-'])
        except:
            target_hum = None

        # Prosty regulator wilgotności - włącz wiatrak jeśli wilgotność za wysoka
        if hum is not None and target_hum is not None:
            if hum > target_hum:
                fan_on = True
            else:
                fan_on = False
            devices.set_fan(fan_on)
            window['-FAN-'].update('Wiatrak ON' if fan_on else 'Wiatrak OFF',
                                   button_color=('white', 'green') if fan_on else ('white', 'red'))

        # Nawodnienie (x razy na tydzień po y sekund)
        try:
            water_times = int(values['-WATER_TIMES-'])
            water_seconds = int(values['-WATER_SECONDS-'])
        except:
            water_times = 0
            water_seconds = 0

        today = datetime.now().date()
        # Sprawdzamy, czy dziś już podlewaliśmy (last_watering_times przechowuje daty podlewania)
        if water_times > 0 and water_seconds > 0:
            if len(last_watering_times) < water_times or (today - last_watering_times[-1]).days >= 1:
                # Podlewamy
                log(f"Automatyczne podlewanie: {water_seconds} sekund")
                devices.set_pump(True)
                window.refresh()
                time.sleep(water_seconds)
                devices.set_pump(False)
                last_watering_times.append(today)
                if len(last_watering_times) > water_times:
                    last_watering_times.pop(0)

    if event == '-REFRESH-':
        update_sensor_values()

window.close()
