import time
from pyMultiservo import MULTISERVO
import smbus

n = 490

bus = smbus.SMBus(1)
#bus.write_word_data(0x47, 6, 0x1EA)
try:
    bus.write_word_data(0x47, 0x6, ((n & 0xff) << 8 ^ n >> 8))
except IOError as error_code:
    print(error_code.args)

#bus.write_byte(0x47, 0)
#bus.write_byte(0x47, 0)
#time.sleep(1)
#print(bus.read_byte(31))
#bus.close()



my_servo = MULTISERVO()

#bus.write_word_data(31, 6, 0x00)

#err1 = my_servo.attach(6)
#print(err1)

#err2 = my_servo.write(0)
#print(err2)

#time.sleep(5)

#err3 = my_servo.write(1)
#print(err3)

my_servo.detach()

