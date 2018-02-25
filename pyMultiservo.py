# -*- coding: utf-8 -*-
#   Библиотека для управления Multiservo на Paspberru Pi
#   pyMultiservo
#   Автор Seliverstov Dmitriy shatki@mail.ru


class MULTISERVO(object):
    register = {
    }

"""
     error =  {
        OK= 0,
        DATA_TOO_LONG = 1,
        NACK_ON_ADDRESS,
        NACK_ON_DATA,
        TWI_ERROR,
        BAD_PIN,
        BAD_PULSE
    };
"""





    # Default
    I2C_DEFAULT_ADDRESS = 0x47
    # I2C_IDENTITY = 0xD3
    PULSE_MIN_DEFAULT = 490
    PULSE_MAX_DEFAULT = 2400
    PULSE_MAX_ABSOLUTE = 19000

    ATTEMPTS_DEFAULT = 4

    PIN_INVALID = 0xFF
    PIN_MAX = 18




    _addr = 0
    _ctrlReg1 = 0
    _ctrlReg2 = 0
    _ctrlReg3 = 0
    _ctrlReg4 = 0
    _ctrlReg5 = 0

    # Additional constants
    def write_microseconds(self, pin, pulse_width, address=I2C_DEFAULT_ADDRESS, attempts):
