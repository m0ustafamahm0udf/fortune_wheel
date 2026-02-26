import serial
import time

ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)

print("Sending START...")
ser.write(b"START\r\n")

time.sleep(1)

print("Reading response...")
while ser.in_waiting > 0:
    print(ser.readline().decode('utf-8', errors='ignore').strip())

print("Sending STOP...")
ser.write(b"STOP\r\n")

print("Done.")
