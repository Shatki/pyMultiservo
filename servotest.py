from pyMultiservo import MULTISERVO

my_servo = MULTISERVO()

err1 = my_servo.attach(6)
print(err1)

err2 = my_servo.write(50)
print(err2)