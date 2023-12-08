from Models.RpiPico import RpiPico
from Models.Api import Api
from time import sleep, time

from Models.Sensors.BH1750 import BH1750
from Models.Sensors.VEML6075 import VEML6075

# Importo variables de entorno
import env

# Tiempo entre subidas API en segundos, también utilizado para dormir
INTERVAL_API_UPLOAD = 288

# Momento de la última subida a la api.
last_upload_at = time()

# Id de dispositivo
hardware_device_id = env.DEVICE_ID

# Rpi Pico Model
if env.UPLOAD_API and env.AP_NAME and env.AP_PASS:
    controller = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=env.DEBUG)
else:
    controller = RpiPico(debug=env.DEBUG)

# Instancia de la api
api = Api(controller, env.API_URL, env.API_PATH, env.API_TOKEN, debug=env.DEBUG)

sleep(1)

sol = BH1750(i2c=controller.i2c_0, addr=0x23, debug=env.DEBUG)

sleep(1)

uv = VEML6075(i2c=controller.i2c_0, debug=env.DEBUG)

sleep(1)

def loop():
    global last_upload_at

    if env.DEBUG:
        print('')
        print('.')
        print('')

    controller.ledOn()

    lux = sol.measurement
    sleep(0.5)
    lumens = sol.get_lumens(lux)
    sleep(0.5)
    index = uv.uv_index
    sleep(0.2)
    uva = uv.uva
    uvb = uv.uvb

    # Muestro datos obtenidos
    if env.DEBUG:
        print('hardware_device_id: ', hardware_device_id)
        print('Lux: ', lux)
        print('Lumens: ', lumens)
        print('uv_index: ', index)
        print('uva: ', uva)
        print('uvb: ', uvb)
        sleep(1)

    # Subo a la api
    api.upload({
        'hardware_device_id': hardware_device_id,
        'lux': lux,
        'lumens': lumens,
        'uv_index': index,
        'uva': uva,
        'uvb': uvb
    })

    last_upload_at = time()

    controller.ledOff()


def main():
    while True:
        try:
            loop()
        except Exception as e:
            if env.DEBUG:
                print('Error: ', e)
        finally:
            if env.DEBUG:
                print('Durmiendo Microcontrolador')
                sleep(INTERVAL_API_UPLOAD)
            else:
                controller.deepsleep(INTERVAL_API_UPLOAD)

main()
