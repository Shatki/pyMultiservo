# -*- coding: utf-8 -*-
#   Библиотека для управления Multiservo на Raspberru Pi
#   pyMultiservo
#   Автор Seliverstov Dmitriy shatki@mail.ru
import smbus
from enum import Enum


class MULTISERVO(object):
    class Error(Enum):
        OK = 0,
        DATA_TOO_LONG = 1,
        NACK_ON_ADDRESS = 2,
        NACK_ON_DATA = 3,
        TWI_ERROR = 4,
        BAD_PIN = 5,
        BAD_PULSE = 6

    # Библиотека smbus не поддерживает прием ACK_ON_ADDRESS или ACK_ON_DATA от slave.
    # Вместо этого библиотека прижимает линию DATA к низкому логическому уровню.

    # Default
    I2C_DEFAULT_ADDRESS = 0x47
    I2C_DEFAULT_PORT = 1
    # I2C_IDENTITY = 0xD3
    PULSE_MIN_DEFAULT = 490
    PULSE_MAX_DEFAULT = 2400
    PULSE_MAX_ABSOLUTE = 19000
    ANGLE_MIN_DEFAULT = 0
    ANGLE_MAX_DEFAULT = 180
    ATTEMPTS_DEFAULT = 4
    PIN_INVALID = 0xFF
    PIN_MAX = 18
    DEVICE_PREFIX = '/dev/i2c-{}'

    _twi_address = I2C_DEFAULT_ADDRESS
    _pulse_width = 0
    _iPin = PIN_INVALID
    _min_pulse = 0
    _max_pulse = 0

    @staticmethod
    def _map(x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    @staticmethod
    def _constrain(x, a, b):
        if x < a:
            return a
        elif x > b:
            return b
        return x

    @staticmethod
    def _reverse_uint16(data):
        return (data & 0xff) << 8 ^ data >> 8

    @staticmethod
    def _get_pi_i2c_bus_number():
        """
        Returns the I2C bus number (/dev/i2c-#) for the Raspberry Pi being used.
        Courtesy quick2wire-python-api
        https://github.com/quick2wire/quick2wire-python-api
        """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Revision'):
                        return 1
        except:
            return 0

    def __init__(self, port=1, address=I2C_DEFAULT_ADDRESS):
        # Setup I2C interface
        # Подключаемся к шине I2C
        self._i2c = smbus.SMBus(port)
        self._twi_address = address

    # Additional constants
    def _write_microseconds(self, pin, pulse_width, retry_attempts=ATTEMPTS_DEFAULT):
        """
         Отдаёт команду послать на сервоприводимульс определённой длины, 
         является низкоуровневым аналогом предыдущей команды. 
         Синтаксис: servo.write_microseconds(-----), где uS — длина импульса в микросекундах.
         :param pin: 
         :param pulse_width: 
         :param retry_attempts:
         :return: 
         """
        error_code = self.Error.OK
        while retry_attempts > 0:
            try:
                self._i2c.write_word_data(self._twi_address, pin, self._reverse_uint16(pulse_width))
            except:
                # IOError
                # EREMOTEIO 121 Remote I/O error
                error_code = self.Error.TWI_ERROR
                retry_attempts -= 1
        return error_code

    def write_microseconds(self, pulse_width):
        """
         Отдаёт команду послать на сервоприводимульс определённой длины, 
         является низкоуровневым аналогом предыдущей команды. 
         Синтаксис: servo.write_microseconds(pulse_width)
         :param pulse_width: длина импульса в микросекундах
         :return: Код ошибки или 0 если ОK
         """
        if not self.attached():
            return self.Error.BAD_PIN
        pulse_width = self._constrain(pulse_width, self._min_pulse, self._max_pulse)

        if pulse_width == self._pulse_width:
            return self.Error.OK

        self._pulse_width = pulse_width

        return self._write_microseconds(self._iPin, self._pulse_width, self.ATTEMPTS_DEFAULT)

    def attach(self, pin, min_pulse=PULSE_MIN_DEFAULT, max_pulse=PULSE_MAX_DEFAULT):
        """
        Присоединяет переменную к конкретному пину. 
        Возможны два варианта синтаксиса для этой функции: servo.attach(pin) и servo.attach(pin, min, max). 
        По умолчанию выставляются равными 490 мкс и 2400 мкс соответственно.
        
        :param pin: номер пина, к которому присоединяют сервопривод
        :param min_pulse: минимальная длина импульса в микросекундах, соответствующая углу поворота 0°
        :param max_pulse: максимальная длина импульса в микросекундах, соответствующая углу поворота 180°
        :return: Код ошибки или 0 если ОK
        """
        print(pin, min_pulse, max_pulse)
        if pin < 0 or pin >= self.PIN_MAX:
            self.detach()
            return self.Error.BAD_PIN

        if min_pulse < 0 or min_pulse >= self.PULSE_MAX_ABSOLUTE:
            self.detach()
            return self.Error.BAD_PULSE

        if max_pulse < 0 or max_pulse >= self.PULSE_MAX_ABSOLUTE:
            self.detach()
            return self.Error.BAD_PULSE

        self._iPin = pin
        self._min_pulse = min_pulse
        self._max_pulse = max_pulse
        return self.Error.OK

    def write(self, value):
        """
        Отдаёт команду сервоприводу принять некоторое значение параметра. Синтаксис следующий: servo.write(angle),
        :param value: угол, на который должен повернуться сервопривод
        :return: Код ошибки или 0 если ОK
        """
        # Если значение меньше минимального импульса, то значение указано в градусах
        if value < self._min_pulse:
            # стабилизируем значение с диапазоне с 0 до 180 градусов
            value = self._constrain(value, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT)
            # конвертируем в значение импульса
            value = self._map(value, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT, self._min_pulse, self._max_pulse)
        return self.write_microseconds(value)

    def read(self):
        """
        Читает текущее значение угла, в котором находится сервопривод. 
        Синтаксис: servo.read() 
        :return: возвращается целое значение от 0 до 180
        """
        return self._map(self._pulse_width, self._min_pulse,
                         self._max_pulse, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT)

    def attached(self):
        """
        Проверка, была ли присоединена переменная к конкретному пину. 
        Синтаксис: servo.attached(), 
        :return: Возвращается логическая истина, 
        если переменная была присоединена к какому-либо пину, или ложь в обратном случае.
        """
        return self._iPin != self.PIN_INVALID

    def detach(self):
        """
        Производит действие, обратное действию attach(), 
        то есть отсоединяет переменную от пина, к которому она была приписана. 
        Синтаксис: servo.detach()
        :return: Код ошибки или 0 если ОK
        """
        if not self.attached():
            return self.Error.OK
        err = self._write_microseconds(self._iPin, 0)
        if err:
            self._iPin = self.PIN_INVALID
        else:
            self._i2c.close()
        return err





