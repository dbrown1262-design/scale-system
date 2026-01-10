#!/usr/bin/python3

import time
import serial
import serial.tools.list_ports
from tkinter import messagebox
import sys

ScaleBuffer = ""
LastWeight = None
ScaleRanger = None
ScaleScout = None
ScoutConnected = False
RangerConnected = False

def ConnectScales():
    """Connect to Ohaus scales with retry logic. Call this after app initialization."""
    global ScaleRanger, ScaleScout, ScoutConnected, RangerConnected
    
#    while not (ScoutConnected or RangerConnected):
    try:
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
#            print(f"Found device: VID={p.vid}, PID={p.pid}, Device={p.device}")
            if p.vid == 1027 and p.pid == 24577:
                scaleport = p.device
                print("Connecting to Ranger Scale on " + scaleport)
                ScaleRanger = serial.Serial(port=scaleport, baudrate=9600, timeout=2)
                RangerConnected = True
                print("Connected to Ranger Scale " + scaleport)
            if p.vid == 1027 and p.pid == 24597:
                scaleport = p.device
                print("Connecting to Scout Scale on " + scaleport)
                ScaleScout = serial.Serial(port=scaleport, baudrate=9600, timeout=2)
                ScoutConnected = True
                print("Connected to Scout Scale " + scaleport)
        
        if not (ScoutConnected or RangerConnected):
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
#            if not retry:
#                sys.exit(1)

def GetScaleStatus():
    global ScoutConnected, RangerConnected
    return ScoutConnected, RangerConnected

###########################################################
# this code works for Ohaus Scout SPX2201 scale
# Scale must be set to send continuous data, with units in grams
###########################################################
def GetScoutWeight():
    global ScaleBuffer, LastWeight
    # Read whatever is waiting, don't block
    data = ScaleScout.read(ScaleScout.in_waiting or 0).decode(errors="ignore")
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

###########################################################
# this code works for Ohaus Ranger 3000 scale
# 
###########################################################

def GetRangerWeight():
    ScaleRanger.reset_input_buffer()
    ScaleRanger.write("IP\r\n".encode())
    weight = str(ScaleRanger.readline())
    w = weight.split()
#    print(w)
    Weight = '0'
    if len(w) < 3:
        Weight = 0
    elif w[2].find("g") == 0:
        Weight = str(round(float(w[1])))
    return Weight



ConnectScales()
#time.sleep(5)  # wait for scale to initialize
#w = GetScoutWeight()
#print("Weight is ", w)