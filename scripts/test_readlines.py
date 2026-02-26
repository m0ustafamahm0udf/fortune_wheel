import serial

ser = serial.Serial()
# We can't really test serial without a device easily, but readlines() is known to be blocking.
