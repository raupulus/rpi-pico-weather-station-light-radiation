import micropython
import ustruct

class BH1750Custom:

    def __init__(self, i2c, address = 0x23, debug=False):
        self.i2c = i2c
        self.DEBUG = debug
        self.address = address

        self._high_resolution = False
        self._continuously = False

        self.big_byte_order = True

    def __iter__(self):
        return self

    def __del__(self):
        self.power(False)   # power off before delete

    def _send_cmd(self, command: int):
        """send 1 byte command to device"""
        bo = self._get_byteorder_as_str()[0]    # big, little
        #self.adapter.write(self.address, command.to_bytes(1, bo))
        self.i2c.writeto(self.address, command.to_bytes(1, bo))

    def soft_reset(self):
        """Software reset."""
        self._send_cmd(0b0000_0111)

    def power(self, on: bool = True):
        """Sensor powering"""
        self._send_cmd(0b0000_0001 if on else 0b0000_0000)

    def set_mode(self, continuously: bool = True, high_resolution: bool = True):
        """
        Set sensor mode.
        High resolution mode 2 not implemented.
        """
        if continuously:
            cmd = 0b0001_0000  # continuously mode
        else:
            cmd = 0b0010_0000  # one shot mode

        if not high_resolution:
            cmd |= 0b11    # L-Resolution Mode

        self._send_cmd(cmd)
        #
        self._high_resolution = high_resolution
        self._continuously = continuously


    def _get_byteorder_as_str(self) -> tuple:
        """Return byteorder as string"""
        if self.is_big_byteorder():
            return 'big', '>'
        else:
            return 'little', '<'

    def is_big_byteorder(self) -> bool:
        return self.big_byte_order

    def get_illumination(self) -> float:
        """
        Devuelve la iluminancia en lux. El parámetro Measurement_accuracy se define en la hoja de datos.
        Sin embargo, se puede ignorar, ya que está cerca de la unidad, ¡de 0,96 a 1,44!
        """
        tmp = self.i2c.read(self.address, 2)
        # typical measurement_accuracy is 1.2 (from 0.96 to 1.44 times). Pls. see Measurement Accuracy in datasheet!
        return self.unpack("H", tmp)[0] / self._measurement_accuracy

    def __next__(self) -> float:
        return self.get_illumination()

    def get_conversion_cycle_time(self, max_value: bool = False) -> int:
        """
        Devuelve el tiempo de conversión en [ms] por parte del sensor dependiendo de su configuración.

        Si max_value == True, el método devuelve el valor más alto (para sensores particularmente malos del lote),
        por lo demás típico. Consulte la nota técnica del BH1750FVI,

        Características eléctricas (V CC = 3,0 V, DVI = 3,0 V, Ta = 25 ºC, a menos que se indique lo contrario)
        """
        offs = 2 * int(self._high_resolution) + int(max_value)
        # low resolution:   16, 24
        # hi resolution:    120, 180
        t = 16, 24, 120, 180
        return t[offs]

    def unpack(self, fmt_char: str, source: bytes, redefine_byte_order = None) -> tuple:
        """
        desembalar la matriz leída del sensor.

        Si redefine_byte_order! = Ninguno, entonces bo (ver más abajo) = redefine_byte_order

        fmt_char: c, b, B, h, H, i, I, l, L, q, Q. Consulte: https://docs.python.org/3/library/struct.html
        """

        if not fmt_char:
            raise ValueError(f"Invalid length fmt_char parameter: {len(fmt_char)}")
        bo = self._get_byteorder_as_str()[1]
        if redefine_byte_order is not None:
            bo = redefine_byte_order[0]
        return ustruct.unpack(bo + fmt_char, source)

    @property
    def high_resolution(self) -> bool:
        """Hi (return True) or Low (return False) resolution mode. Use set_mode method!!!
        In hi mode resolution is 1 lux.
        In low mode resolution is 4 lux."""
        return self._high_resolution

    @property
    def continuously(self) -> bool:
        """
        Modo de conversión continua o bajo pedido. Para configurar, utilice el método set_mode.
        """
        return self._continuously

    @property
    def measurement_accuracy(self) -> float:
        """
        Value from the datasheet in the range from 0.96 to 1.44.
        """
        return self._measurement_accuracy

    @measurement_accuracy.setter
    def measurement_accuracy(self, value: float):
        if not 0.96 <= value <= 1.44:
            raise ValueError(f"Invalid measurement accuracy value: {value}")

        self._measurement_accuracy = value
