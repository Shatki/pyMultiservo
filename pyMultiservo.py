# -*- coding: utf-8 -*-
#   Библиотека для управления Multiservo на Paspberru Pi
#   pyMultiservo
#   Автор Seliverstov Dmitriy shatki@mail.ru
import wiringpi as wp
from enum import Enum




class MULTISERVO(object):
    class Error(Enum):
        OK                      =  0,
        DATA_TOO_LONG           = 'Data too long',
        NACK_ON_ADDRESS         = 'Nack on address',
        NACK_ON_DATA            = 'Nack on data',
        TWI_ERROR               = 'I2C error',
        BAD_PIN                 = 'Bad pin',
        BAD_PULSE               = 'Bad pulse',

    # Default
    I2C_DEFAULT_ADDRESS = 0x47
    # I2C_IDENTITY = 0xD3
    PULSE_MIN_DEFAULT = 490
    PULSE_MAX_DEFAULT = 2400
    PULSE_MAX_ABSOLUTE = 19000
    ATTEMPTS_DEFAULT = 4
    PIN_INVALID = 0xFF
    PIN_MAX = 18

    _twiAddress = I2C_DEFAULT_ADDRESS
    _pulseWidth = 0
    _iPin = PIN_INVALID
    _minPilse = 0
    _maxPulse = 0

    def __init__(self, address=I2C_DEFAULT_ADDRESS):
        # Setup I2C interface
        wp.wiringPiSetup()
        self._i2c = wp.I2C()
        self._io = self._i2c.setupInterface('/dev/i2c-' + str(self.getPiI2CBusNumber()), address)
#        self._gpioexp.write_byte(self._addr, GPIO_EXPANDER_RESET)

    @staticmethod
    def _map(x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    @staticmethod
    def reverse_uint16(data):
        result = ((data & 0xff) << 8) | ((data >> 8) & 0xff)
        return result

    @staticmethod
    def getPiI2CBusNumber():
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

    # Additional constants
    def writeMicroseconds(self, pin, pulse_width, address=I2C_DEFAULT_ADDRESS, retryAttempts=ATTEMPTS_DEFAULT):
        while (errorCode and --retryAttempts):
            self._i2c.write(self._io, pin)
            self._i2c.write(self._io, pulse_width)
            # self._i2c.write(pin)
            # self._i2c.write(pulse_width >> 8)
            # self._i2c.write(pulse_width & 0xFF)
            # errorCode = (Error)
            # self._i2c.endTransmission()
        return errorCode

    def analogWrite(self, pin, value):
        value = int(value*255)
        data = (pin & 0xff)|((value & 0xff)<<8)



    def attach(self, pin, min_pulse=PULSE_MIN_DEFAULT, max_pulse=PULSE_MAX_DEFAULT):
        if (pin < 0 or pin >= self.PIN_MAX):
            self.detach()
            return self.Error.BAD_PIN

        if (min_pulse < 0 or min_pulse >= self.PULSE_MAX_ABSOLUTE):
            self.detach()
            return self.Error.BAD_PULSE

        if (max_pulse < 0 or max_pulse >= self.PULSE_MAX_ABSOLUTE):
            self.detach()
            return self.Error.BAD_PULSE

        self._iPin = pin
        self._minPulse = min_pulse
        self._maxPulse = max_pulse
        return self.Error.OK

    def attached(self):
        return self._iPin != self.PIN_INVALID

    def read(self):
        return self._map(self._pulseWidth, self._minPilse, self._maxPulse, 0, 180)

    def detach(self):
        if not self.attached():
            return self.Error.OK
        err = self.writeMicroseconds(self._iPin, 0, self._twiAddress, self.ATTEMPTS_DEFAULT)
        if err:
             self._iPin = self.PIN_INVALID

        return err