# -*- coding: utf-8 -*-
#   Библиотека для управления Multiservo на Paspberru Pi
#   pyMultiservo
#   Автор Seliverstov Dmitriy shatki@mail.ru
import wiringpi as wp
from enum import enum




class MULTISERVO(object):
    Error = {
        'OK' = 0,
        'DATA_TOO_LONG',
        'NACK_ON_ADDRESS',
        'NACK_ON_DATA',
        'TWI_ERROR',
        'BAD_PIN',
        'BAD_PULSE',
    }


    register = {
    }

    # Default
    I2C_DEFAULT_ADDRESS = 0x47
    # I2C_IDENTITY = 0xD3
    PULSE_MIN_DEFAULT = 490
    PULSE_MAX_DEFAULT = 2400
    PULSE_MAX_ABSOLUTE = 19000
    ATTEMPTS_DEFAULT = 4
    PIN_INVALID = 0xFF
    PIN_MAX = 18

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


    def reverse_uint16(self, data):
        result = ((data & 0xff) << 8) | ((data >> 8) & 0xff)
        return result

    def getPiI2CBusNumber(self):
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
            self._i2c.beginTransmission(address)
            self._i2c.write(pin)
            self._i2c.write(pulse_width >> 8)
            self._i2c.write(pulse_width & 0xFF)
            # errorCode = (Error)
            self._i2c.endTransmission()
        return

    def attach(self, pin, min_pulse=PULSE_MIN_DEFAULT, max_pulse=PULSE_MAX_DEFAULT):
        if (pin < 0 or pin >= self.PIN_MAX):
            self.detach()
            return BAD_PIN

        if (minPulse < 0 or minPulse >= self.PULSE_MAX_ABSOLUTE):
            detach()
            return BAD_PULSE

        if (maxPulse < 0 or maxPulse >= self.PULSE_MAX_ABSOLUTE):
            detach()
            return BAD_PULSE

        self._iPin = pin
        self._minPulse = min_pulse
        self._maxPulse = max_pulse
        return OK
