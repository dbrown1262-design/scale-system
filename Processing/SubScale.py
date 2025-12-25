#!/usr/bin/python3

import serial
import serial.tools.list_ports
import time
from tkinter import messagebox
import sys

ScaleBuffer = ""
LastWeight = None
Scale = None
ScaleConnected = False

def ConnectScales():
    """Connect to Ohaus scale with retry logic. Call this after app initialization."""
    global Scale, ScaleConnected
    
    while not ScaleConnected:
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if p.vid == 1027 and (p.pid == 24577 or p.pid == 24597):
                    scaleport = p.device
                    print("Connecting to Scale on " + scaleport)
                    Scale = serial.Serial(port=scaleport, baudrate=9600, timeout=2)
                    ScaleConnected = True
                    print("Connected to Scale " + scaleport)
                    break
            
            if not ScaleConnected:
                raise Exception("No Ohaus scale detected")
                
        except Exception as e:
            print(f"Failed to connect to scale: {e}")
            retry = messagebox.askretrycancel(
                "Scale Not Available",
                f"Could not connect to scale.\n\n"
                f"Please check:\n"
                f"1. Scale is turned on and connected via USB\n"
                f"2. Scale is not being used by another application\n"
                f"3. USB cable is properly connected\n\n"
                f"Error: {e}\n\n"
                f"Click Retry to try again, or Cancel to exit."
            )
            if not retry:
                sys.exit(1)

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
#            print("Scale line: '" + line + "'")
            parts = line.split()
            LastWeight =float(parts[0])
            Unit = parts[1] 
#            print("Parsed weight: ", LastWeight, Unit)
#            val = _parse_ohaus_line(line)
#            if val is not None:
#                LastWeight = val

    return LastWeight



def OldGetWeight():
    Scale.reset_input_buffer()
    Scale.write("IP\r\n".encode())
    weight = str(Scale.readline())
    w = weight.split()
#    print(w)
    Weight = '0'
    if len(w) < 3:
        Weight = 0
    elif w[2].find("g") == 0:
        Weight = str(int(w[1]))
    return Weight



#w = GetWeight()
#print("Weight is ", w)