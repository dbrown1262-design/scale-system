#!/usr/bin/python3

# Scout Scale: p.vid = 1027 p.pid = 24597
# Ranger Scale: p.vid = 1027 p.pid = 24577
import serial
import serial.tools.list_ports
scaleport = " "
ports = list(serial.tools.list_ports.comports())
for p in ports:
#    print(p.vid, p.pid, p.device)
    if p.vid == 1027 and (p.pid == 24577 or p.pid == 24597):
        scaleport = p.device
        print("Connected to Scale " + scaleport)
        Scale = serial.Serial(port=scaleport, baudrate=9600, timeout=2)


def GetWeight():
    Scale.reset_input_buffer()
    Scale.write("IP\r\n".encode())
    weight = str(Scale.readline())
    w = weight.split()
#    print(w)
    Weight = '0'
    if len(w) < 3:
        Weight = 0
    elif w[2].find("g") == 0:
        Weight = str(round(float(w[1])))
    return Weight



#w = GetWeight()
#print("Weight is ", w)