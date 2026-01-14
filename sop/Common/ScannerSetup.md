# Scanner Setup SOP

## 1. Purpose

To define the standardized procedure for detecting, testing, and configuring Bluetooth QR scanner hardware for use with the weighing and tracking applications. This ensures proper communication between the scanner device and the application software.

---

## 2. Inputs

- Bluetooth QR scanner device (paired with workstation)
- Windows Bluetooth serial port (SPP)
- config.json configuration file
- Serial port detection utilities

---

## 3. Responsibilities

- **IT Administrator:** Pair Bluetooth scanner with workstation and verify device connectivity.
- **Harvest/Packaging Technician:** Perform scanner setup and validation testing.
- **System Administrator (Admin Menu):** Monitor scanner configuration and troubleshoot communication issues.

---

## 4. Procedure

### 4.1 Launch the Scanner Setup Application

1. From the main menu, navigate to Common → Scanner Setup.
2. The Scanner Setup window will open.
3. If an existing scanner configuration is found, it will be displayed in the status log.

---

### 4.2 Prepare the Scanner

**Bluetooth Pairing**

1. Ensure the Bluetooth QR scanner is powered on.
2. Verify the scanner is paired with the Windows workstation via Bluetooth settings.
	- Open Windows Settings → Bluetooth & Devices.
	- Confirm the scanner appears in the paired devices list.
3. If not paired, complete the Bluetooth pairing process before proceeding.

---

### 4.3 Scan for Available Ports

**Detect Bluetooth Serial Ports**

1. Click the **Scan for Ports** button.
2. The application will scan for all available Bluetooth serial ports (SPP).
3. Detected ports will be displayed in the "Available Bluetooth Ports" list.
	- Each port shows the COM port number and device description.
	- Example: "COM5 - Standard Serial over Bluetooth link"

**No Ports Found**

If no Bluetooth ports are detected:

1. Verify the scanner is paired via Bluetooth.
2. Restart the scanner device.
3. Restart the Bluetooth service on the workstation.
4. Click **Scan for Ports** again.

---

### 4.4 Test the Scanner

**Select a Port**

1. In the "Available Bluetooth Ports" list, select the appropriate port by clicking the radio button.
	- The first detected port is selected by default.

**Run Scanner Test**

1. Click the **Test Scanner** button.
2. The status log will display: "Please scan a QR code now..."
3. Scan any QR code or barcode with the scanner within 10 seconds.

**Test Results**

- **Success:** The status log displays "SUCCESS: Received data: [scanned data]"
	- The scanned data will be shown.
	- The **Save Configuration** button becomes enabled.
- **Failure:** The status log displays "ERROR: Timed out waiting for scan."
	- Verify the scanner is on and within Bluetooth range.
	- Try a different port from the list.
	- Click **Test Scanner** again.

---

### 4.5 Save Configuration

**Finalize Setup**

1. After a successful scanner test, click the **Save Configuration** button.
2. The application will save the selected COM port to `Common/config.json`.
3. A confirmation message will display: "Scanner port [port] has been saved to config.json"

**Verification**

The configuration is now saved and will be used by all weighing and tracking applications that require QR scanner input.

---

### 4.6 Close the Application

1. Review the status log to confirm successful configuration.
2. Click the **Close** button to exit the Scanner Setup application.

---

## 5. Quality & Compliance Checks

- The scanner must be successfully paired via Bluetooth before running the setup.
- Test scans must return data within the 10-second timeout window.
- The saved COM port in config.json must match the port where the scanner was successfully detected.
- If the scanner stops working after configuration, re-run the setup process to detect port changes.
- Bluetooth serial port assignments may change if devices are unpaired and re-paired.

---

## 6. Records

- Common/config.json file containing scanner_com_port value
- Status log showing detected ports and test results
- Bluetooth device pairing records in Windows settings
