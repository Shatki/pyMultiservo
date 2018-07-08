# -*- coding: utf-8 -*-
#   Библиотека для управления Multiservo на Raspberry Pi
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

    __twi_address = I2C_DEFAULT_ADDRESS
    __pulse_width = 0
    __iPin = PIN_INVALID
    __min_pulse = 0
    __max_pulse = 0

    @staticmethod
    def __map(x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    @staticmethod
    def __constrain(x, a, b):
        if x < a:
            return a
        elif x > b:
            return b
        return x

    @staticmethod
    def __reverse_uint16(data):
        result = ((data & 0xff) << 8) | ((data >> 8) & 0xff)
        return result

    def __get_pi__i2c_bus_number(self):
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
        except IOError:
            return self.Error.TWI_ERROR

    def __init__(self, port=1, address=I2C_DEFAULT_ADDRESS):
        # Setup I2C interface
        # Подключаемся к шине I2C
        self.__i2c = smbus.SMBus(port)
        self.__twi_address = address
        # self._gpioexp.write_byte(self._addr, GPIO_EXPANDER_RESET)

    # Additional constants
    def __write_microseconds(self, pin, pulse_width, retry_attempts=ATTEMPTS_DEFAULT):
        """
         Отдаёт команду послать на сервоприводимульс определённой длины, 
         является низкоуровневым аналогом предыдущей команды. Только для внутреннего использования.
         Синтаксис следующий: servo._write_microseconds(-----), где uS — длина импульса в микросекундах.
         :param pin: 
         :param pulse_width: 
         :param retry_attempts:
         :return: 
         """
        error_code = self.Error.OK
        while retry_attempts > 0:
            try:
                self.__i2c.write_word_data(self.__twi_address, pin, ((pulse_width & 0xff) << 8 ^ pulse_width >> 8))
            except IOError:
                # Error code after trying
                print(error_code)
                error_code = self.Error.TWI_ERROR
                retry_attempts -= 1
        return error_code

    def write_microseconds(self, pulse_width):
        """
         Отдаёт команду послать на сервоприводимульс определённой длины. .
         Синтаксис следующий: servo.write_microseconds(pulse_width)
         :param pulse_width: длина импульса в микросекундах
         :return: Код ошибки или 0 если ОK
         """
        if not self.attached():
            return self.Error.BAD_PIN
        pulse_width = self.__constrain(pulse_width, self.__min_pulse, self.__max_pulse)

        if pulse_width == self.__pulse_width:
            return self.Error.OK

        self.__pulse_width = pulse_width

        return self.__write_microseconds(self.__iPin, self.__pulse_width, self.ATTEMPTS_DEFAULT)

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

        self.__iPin = pin
        self.__min_pulse = min_pulse
        self.__max_pulse = max_pulse
        return self.Error.OK

    def detach(self):
        """
        Производит действие, обратное действию attach(),
        то есть отсоединяет переменную от пина, к которому она была приписана.
        Синтаксис следующий: servo.detach()
        :return: Код ошибки или 0 если ОK
        """
        if not self.attached():
            return self.Error.OK
        # Возврат сервы в положение 0
        err = self.__write_microseconds(self.__iPin, 0)
        if err:
            self.__iPin = self.PIN_INVALID
        #else:
        #    self.__i2c.close()
        return err

    def write(self, value):
        """
        Отдаёт команду сервоприводу принять некоторое значение параметра. Синтаксис следующий: servo.write(angle),
        :param value: угол, на который должен повернуться сервопривод
        :return: Код ошибки или 0 если ОK
        """
        # Если значение меньше минимального импульса, то значение указано в градусах
        if value < self.__min_pulse:
            # стабилизируем значение с диапазоне с 0 до 180 градусов
            value = self.__constrain(value, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT)
            # конвертируем в значение импульса
            value = self.__map(value, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT, self.__min_pulse, self.__max_pulse)
        return self.write_microseconds(value)

    def read(self):
        """
        Читает текущее значение угла, в котором находится сервопривод. 
        Синтаксис следующий: servo.read() 
        :return: возвращается целое значение от 0 до 180
        """
        return self.__map(self.__pulse_width, self.__min_pulse,
                         self.__max_pulse, self.ANGLE_MIN_DEFAULT, self.ANGLE_MAX_DEFAULT)

    def attached(self):
        """
        Проверка, была ли присоединена переменная к конкретному пину. 
        Синтаксис следующий: servo.attached(), 
        :return: Возвращается логическая истина, 
        если переменная была присоединена к какому-либо пину, или ложь в обратном случае.
        """
        return self.__iPin != self.PIN_INVALID
