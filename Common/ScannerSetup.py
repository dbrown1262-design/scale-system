import serial
import serial.tools.list_ports
import time
import json
import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import subprocess   
import sys
from pathlib import Path

# Folder where THIS file lives (i.e., the common folder)
BASE_DIR = Path(__file__).resolve().parent

# Full path to config.json in the same folder
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_FONT = ("Arial", 14)

# BASE_DIR is the folder that contains menu.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def restart_menu():
    """Start menu.py again in a new process."""
    menu_path = os.path.join(BASE_DIR, "menu.py")
    subprocess.Popen([sys.executable, menu_path], cwd=BASE_DIR)


class ScannerSetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set dark mode theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Scanner Setup")
        self.geometry("700x700")
        
        self.scanning = False
        self.scan_thread = None
        
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(frame, text="QR Scanner Setup", font=("Arial", 20, "bold"))
        header.pack(pady=(0, 20))
        
        # Instructions
        instructions = ctk.CTkLabel(
            frame, 
            text="This utility will detect your Bluetooth QR scanner.\n"
                 "1. Make sure your scanner is paired via Bluetooth\n"
                 "2. Click 'Scan for Ports' to detect available ports\n"
                 "3. Select a port and click 'Test Scanner'\n"
                 "4. Scan a QR code when prompted\n"
                 "5. Click 'Save Configuration' when successful",
            font=DEFAULT_FONT,
            justify="left"
        )
        instructions.pack(pady=(0, 20))
        
        # Ports listbox area
        ports_label = ctk.CTkLabel(frame, text="Available Bluetooth Ports:", font=DEFAULT_FONT)
        ports_label.pack(anchor="w", pady=(10, 5))
        
        # Scrollable frame for ports
        self.ports_frame = ctk.CTkScrollableFrame(frame, height=150)
        self.ports_frame.pack(fill="x", pady=(0, 10))
        
        self.port_vars = []
        self.port_radios = []
        self.selected_port = ctk.StringVar(value="")
        
        # Buttons row 1
        btn_frame1 = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame1.pack(pady=10)
        
        self.btn_scan_ports = ctk.CTkButton(btn_frame1, text="Scan for Ports", font=DEFAULT_FONT, command=self.scan_for_ports)
        self.btn_scan_ports.pack(side="left", padx=5)
        
        self.btn_test = ctk.CTkButton(btn_frame1, text="Test Scanner", font=DEFAULT_FONT, command=self.test_scanner)
        self.btn_test.pack(side="left", padx=5)
        
        self.btn_save = ctk.CTkButton(btn_frame1, text="Save Configuration", font=DEFAULT_FONT, command=self.save_config, state="disabled")
        self.btn_save.pack(side="left", padx=5)
        
        self.btn_close = ctk.CTkButton(btn_frame1, text="Close", font=DEFAULT_FONT, command=self.close_app)
        self.btn_close.pack(side="left", padx=5)
        
        # Status text area
        status_label = ctk.CTkLabel(frame, text="Status Log:", font=DEFAULT_FONT)
        status_label.pack(anchor="w", pady=(10, 5))
        
        self.status_text = ctk.CTkTextbox(frame, height=100, font=("Consolas", 11))
        self.status_text.pack(fill="both", expand=True)
        
        self.log("Ready. Click 'Scan for Ports' to begin.")
        
        # Load existing config if available
        self.load_existing_config()
        
    def log(self, message):
        """Add a message to the status log"""
        try:
            self.status_text.insert("end", f"{message}\n")
            self.status_text.see("end")
        except:
            pass
    
    def load_existing_config(self):
        """Load and display existing configuration if available"""
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                port = config.get("scanner_com_port")
                if port:
                    self.log(f"Existing configuration found: {port}")
        except FileNotFoundError:
            self.log("No existing configuration found.")
        except Exception as e:
            self.log(f"Error loading config: {e}")
    
    def scan_for_ports(self):
        """Scan for available Bluetooth serial ports"""
        self.log("Scanning for Bluetooth ports...")
        
        # Clear existing radio buttons
        for radio in self.port_radios:
            radio.destroy()
        self.port_radios.clear()
        
        ports = list(serial.tools.list_ports.comports())
        bt_ports = []
        
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            
            if "bluetooth" in desc or "standard serial over bluetooth" in desc or "bthenum" in hwid:
                bt_ports.append((p.device, p.description))
#                self.log(f"Found: {p.device} - {p.description}")
        
        if not bt_ports:
            self.log("ERROR: No Bluetooth SPP ports found.")
            messagebox.showwarning("No Ports Found", "No Bluetooth serial ports detected.\nMake sure your scanner is paired via Bluetooth.")
            return
        
        # Create radio buttons for each port
        for port, desc in bt_ports:
            radio = ctk.CTkRadioButton(
                self.ports_frame,
                text=f"{port} - {desc}",
                variable=self.selected_port,
                value=port,
                font=DEFAULT_FONT
            )
            radio.pack(anchor="w", pady=2)
            self.port_radios.append(radio)
        
        # Select first port by default
        if bt_ports:
            self.selected_port.set(bt_ports[0][0])
        
#        self.log(f"Found {len(bt_ports)} Bluetooth port(s).")
    
    def test_scanner(self):
        """Test the selected port by waiting for a scan"""
        port = self.selected_port.get()
        
        if not port:
            messagebox.showwarning("No Port Selected", "Please select a port first.")
            return
        
        if self.scanning:
            messagebox.showinfo("Already Scanning", "A scan test is already in progress.")
            return
        
        self.log(f"Testing port: {port}")
        self.log("Please scan a QR code now...")
        
        # Disable buttons during scan
        self.btn_test.configure(state="disabled")
        self.btn_scan_ports.configure(state="disabled")
        self.scanning = True
        
        # Run scan in background thread
        self.scan_thread = threading.Thread(target=self.run_scan_test, args=(port,), daemon=True)
        self.scan_thread.start()
    
    def run_scan_test(self, port):
        """Run the scanner test in a background thread"""
        success = False
        try:
#            self.log(f"Opening {port}...")
            with serial.Serial(port, baudrate=115200, timeout=0.5) as s:
#                self.log(f"Listening on {port}. Waiting for scan (10 seconds)...")
                
                deadline = time.time() + 10
                while time.time() < deadline:
                    if s.in_waiting > 0:
                        data = s.readline().decode(errors="ignore").strip()
                        if data:
                            self.log(f"SUCCESS: Received data: {data}")
                            success = True
                            break
                    time.sleep(0.1)
                
                if not success:
                    self.log("ERROR: Timed out waiting for scan.")
        except Exception as e:
            self.log(f"ERROR: Could not open {port}: {e}")
        
        # Re-enable buttons on main thread
        self.after(0, lambda: self.scan_complete(success))
    
    def scan_complete(self, success):
        """Called when scan test completes"""
        self.scanning = False
        self.btn_test.configure(state="normal")
        self.btn_scan_ports.configure(state="normal")
        
        if success:
            self.btn_save.configure(state="normal")
            messagebox.showinfo("Success", "Scanner detected successfully!\nClick 'Save Configuration' to save this port.")
        else:
            messagebox.showerror("Test Failed", "No data received from scanner.\nMake sure the scanner is on and try again.")
    
    def save_config(self):
        """Save the selected port to config file"""
        port = self.selected_port.get()
        
        if not port:
            messagebox.showwarning("No Port Selected", "Please select and test a port first.")
            return
        
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"scanner_com_port": port}, f, indent=2)
            
            self.log(f"Configuration saved: {port}")
            messagebox.showinfo("Configuration Saved", f"Scanner port {port} has been saved to {CONFIG_PATH}")
        except Exception as e:
            self.log(f"ERROR saving config: {e}")
            messagebox.showerror("Save Failed", f"Could not save configuration:\n{e}")
    
    def close_app(self):
        """Close the application"""
        if self.scanning:
            resp = messagebox.askyesno("Scan in Progress", "A scan test is in progress. Close anyway?")
            if not resp:
                return
        self.destroy()


def find_scanner_port(baudrate=9600, test_seconds=10):
    print("FUNCTION: find_scanner_port() CALLED")

    ports = list(serial.tools.list_ports.comports())
    print("INFO: All detected ports:")
    for p in ports:
        print(" ", p.device, "-", p.description)

    bt_ports = []

    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()

        if "bluetooth" in desc or "standard serial over bluetooth" in desc or "bthenum" in hwid:
            bt_ports.append(p.device)

    print("INFO: Candidate Bluetooth SPP ports:", bt_ports)

    if not bt_ports:
        print("ERROR: No Bluetooth SPP ports found.")
        return None

    print("INFO: Please scan one barcode now...")

    deadline = time.time() + test_seconds

    while time.time() < deadline:
        for dev in bt_ports:
            try:
                print(f"INFO: Opening {dev}...")
                with serial.Serial(dev, baudrate=baudrate, timeout=0.2) as s:
                    print(f"INFO: Listening on {dev}. Waiting 5 seconds...")
                    time.sleep(5)
                    data = s.readline().decode(errors="ignore").strip()
                    print(f"DEBUG: Data from {dev!r}: {data!r}")
                    if data:
                        print(f"SUCCESS: Scanner detected on {dev}")
                        return dev
            except Exception as e:
                print(f"ERROR: Could not open {dev}: {e}")

    print("ERROR: Timed out waiting for data.")
    return None


def save_config(port):
    print(f"SAVING CONFIG: Port = {port}")
    with open(CONFIG_PATH, "w") as f:
        json.dump({"scanner_com_port": port}, f)
    print(f"CONFIG SAVED to {CONFIG_PATH}")


# ---------- MAIN BLOCK ----------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = ScannerSetupApp()
    app.mainloop()
    restart_menu()