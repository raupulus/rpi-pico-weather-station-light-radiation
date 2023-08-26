from Models.RpiPico import RpiPico
#from Models.Api import Api
from time import sleep, time

from Models.Sensors.BH1750 import BH1750
from Models.Sensors.VEML6075 import VEML6075

# Importo variables de entorno
import env

# Instancia de la api
#api = Api(controller, channelSensors, env.API_URL, env.API_PATH, env.API_TOKEN, debug=env.DEBUG)

# Tiempo entre subidas API en segundos
INTERVAL_API_UPLOAD = 30

# Momento de la última subida a la api.
last_upload_at = time()


# Rpi Pico Model
if env.UPLOAD_API and env.AP_NAME and env.AP_PASS:
    controller = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=env.DEBUG)
else:
    controller = RpiPico(debug=env.DEBUG)

"""
print('')
print('Scan i2c bus...')
devices = controller.i2c_0.scan()

if len(devices) == 0:
    print("No i2c device !")
else:
    print('i2c devices found:',len(devices))

for device in devices:
    print("Decimal address: ",device," | Hexa address: ",hex(device))

print('Scan i2c bus... OK')
print('')
"""


sol = BH1750(i2c=controller.i2c_0, addr=0x23, debug=env.DEBUG)
sleep(1)
uv = VEML6075(i2c=controller.i2c_0, debug=env.DEBUG)
sleep(1)


def main():
    while True:
        if env.DEBUG:
            print('')
            print('.')
            print('')


        lux = sol.measurement
        lumens = sol.get_lumens(lux)
        uv_index = uv.uv_index
        uva = uv.uva
        uvb = uv.uvb

        # Muestro lux obtenidos
        print('Lux: ', lux)
        print('Lumens: ', lumens)
        print('uv_index: ', uv_index)
        print('uva: ', uva)
        print('uvb: ', uvb)

        sleep(1)


        """

        sol.power(on=True)     # Sensor Of Lux
        sol.set_mode(continuously=True, high_resolution=True)
        sol.measurement_accuracy = 1.0      # default value
        old_lux = curr_max = 1.0

        for lux in sol:
            if lux != old_lux:
                curr_max = max(lux, curr_max)
                lt = time.localtime()
                print(f"{lt[3:6]}\tIllumination [lux]: {lux}.\tmax: {curr_max}.\tNormalized [%]: {100*lux/curr_max}.")
            old_lux = lux
            time.sleep_ms(sol.get_conversion_cycle_time())
        """


main()
