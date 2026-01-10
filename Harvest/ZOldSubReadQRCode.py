#!/usr/bin/python3

from supabase import create_client, Client
import time
import serial
import serial.tools.list_ports
import json
from pathlib import Path
from tkinter import messagebox
import sys

# Folder where THIS file lives (i.e., the Harvest folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# Full path to config.json in Common folder
CONFIG_PATH = BASE_DIR / "Common" / "config.json"

def load_scanner_port():
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
    return cfg["scanner_com_port"]

scanner_port = load_scanner_port()

# QR reader will be initialized by ConnectScanner()
QrReader = None

def ConnectScanner():
    """Connect to QR scanner with retry logic. Call this after app initialization."""
    global QrReader
    
    while QrReader is None:
        try:
            QrReader = serial.Serial(scanner_port, 115200, timeout=1)
            print("Scanner ready on", scanner_port)
        except Exception as e:
            print(f"Failed to open scanner on {scanner_port}: {e}")
            retry = messagebox.askretrycancel(
                "Scanner Not Available",
                f"Could not connect to QR scanner on {scanner_port}.\n\n"
                f"Please check:\n"
                f"1. Scanner is turned on\n"
                f"2. Scanner is paired via Bluetooth\n"
                f"3. Scanner is not being used by another application\n\n"
                f"Error: {e}\n\n"
                f"Click Retry to try again, or Cancel to exit."
            )
            if not retry:
                sys.exit(1)

def CheckQr():
    Qr1 = "none"; Qr2 = "none"
    if QrReader and QrReader.in_waiting > 0:
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
    if QrReader and QrReader.in_waiting > 0:
        raw = QrReader.readline()
        print("raw =", raw)

        # Decode from bytes to text and strip whitespace
        ptext = raw.decode().strip()
        print("ptext =", ptext)
    return (ptext)