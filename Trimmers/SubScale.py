#!/usr/bin/python3

import time
import serial
import serial.tools.list_ports
ScaleBuffer = ""
LastWeight = None
scaleport = " "
ports = list(serial.tools.list_ports.comports())
for p in ports:
    if p.vid == 1027 and (p.pid == 24577 or p.pid == 24597):
        scaleport = p.device
        print("Connected to Scale " + scaleport)
        Scale = serial.Serial(
            port=scaleport,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1)
#time.sleep(2)  # wait for serial port to initialize
###########################################################
# this code works for Ohaus Scout SPX2201 scale
# Scale must be set to send continuous data, with units in grams
###########################################################

def GetWeight():
    global ScaleBuffer, LastWeight

    # Read whatever is waiting, don't block
    data = Scale.read(Scale.in_waiting or 0).decode(errors="ignore")
    if data:
        ScaleBuffer += data

        while "\r\n" in ScaleBuffer:
            line, ScaleBuffer = ScaleBuffer.split("\r\n", 1)
            line = line.strip()
            if not line:
                continue
            print("Scale line: '" + line + "'")
            parts = line.split()
            LastWeight =float(parts[0])
            Unit = parts[1] 
            print("Parsed weight: ", LastWeight, Unit)
#            val = _parse_ohaus_line(line)
#            if val is not None:
#                LastWeight = val

    return LastWeight

###########################################################
# this code works for Ohaus Ranger 3000 scale
# 
###########################################################

def OldGetWeight():
    Scale.reset_input_buffer()
    Scale.write("IP\r\n".encode())
#    Scale.write("P\r\n".encode())
    weight = str(Scale.readline())
    print("Raw weight string: " + weight)
    w = weight.split()
    print(w)
    Weight = '0'
    if len(w) < 3:
        Weight = 0
    elif w[2].find("g") == 0:
        Weight = str(int(w[1]))
    return Weight



#w = GetWeight()
#print("Weight is ", w)