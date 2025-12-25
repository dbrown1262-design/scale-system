#!/usr/bin/python3

#import win32print
from supabase import create_client, Client
import time

import serial
import serial.tools.list_ports
supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase = create_client(supabase_url, supabase_key)

# Connect to Supabase
scaleschema = "scale"
supabase = supabase.schema(scaleschema)

scaleport = " "
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
    ps = str(p)
    if ps.find("CH340") > 0:
        ps1 = ps.split(" ")
        scaleport = ps1[0]
        print("Raw scaleport:", repr(scaleport))
        QrReader = serial.Serial(port=scaleport, baudrate=115200, timeout=1)
#        QrReader = serial.Serial(port="COM6", baudrate=9600, timeout=1)

def CheckQr():
    Qr1 = "none"; Qr2 = "none"
    if QrReader.in_waiting > 0:
        raw = QrReader.readline()
        print("raw =", raw)

        # Decode from bytes to text and strip whitespace
        ptext = raw.decode().strip()
        print("ptext =", ptext)

        # Split on '.' and extract second part safely
#        parts = ptext.split('.')
#        if len(parts) > 1:
#            Qr2 = parts[1].strip()
#            Qr1 = "202"
        Qr2 = ptext
        print("Qqr2 = ", Qr2)
    return (Qr2)

def CheckMetricQr():
    ptext = "none"
    if QrReader.in_waiting > 0:
        raw = QrReader.readline()
        print("raw =", raw)

        # Decode from bytes to text and strip whitespace
        ptext = raw.decode().strip()
        print("ptext =", ptext)
    return (ptext)

#while (ptext := CheckMetricQr()) == "none":
#    print("Waiting for QR code...")
#    time.sleep(1)