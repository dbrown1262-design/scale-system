# Scanner Setup SOP

## 1. Purpose

To define the standardized procedure for detecting, testing, and configuring Bluetooth QR scanner hardware for use with the weighing and tracking applications. This ensures proper communication between the scanner device and the application software.

---

## 2. Inputs

- Bluetooth or USB QR scanner device
- config.json configuration file
- Serial port detection utilities

---


## 3. Procedure

### 3.1 Launch the Scanner Setup Application

1. From the main menu, navigate to Common → Scanner Setup.
2. The Scanner Setup window will open.
3. If an existing scanner configuration is found, it will be displayed in the status log.

---

### 3.2 Prepare the Scanner

**Bluetooth Pairing**

1. Ensure the Bluetooth QR scanner is powered on.
2. Verify the scanner is paired with the Windows workstation via Bluetooth settings.
	- Open Windows Settings → Bluetooth & Devices.
	- Confirm the scanner appears in the paired devices list.
3. If not paired, complete the Bluetooth pairing process before proceeding.

**USB Scanner Setup**

The full manual for the FS2208 scanner is stored in the adknet folder.  The USB setup is on page 98.  The file DS2208 scanner setup.pdf contains only page 98.

1. Connect the scanner to a USB port
2. Open "DS2208 scanner setup.pdf" in adknet folder.
3. Scan the USB CDC Host barcode
---

### 3.3 Scan for Available Ports

**Detect Scanner Serial Ports**

1. Click the **Scan for Ports** button.
2. The application will scan for all available Scanner serial ports (SPP).
3. Detected ports will be displayed in the "Available Scanner Ports" list.
	- Each port shows the COM port number and device description.
	- Example: "COM5 - Standard Serial over Bluetooth link"

**No Ports Found**

If no scanner ports are detected:

1. Verify the scanner is paired via Bluetooth or USB.
2. Restart the scanner device.
3. If using bluetooth, restart the Bluetooth service on the workstation.
4. Click **Scan for Ports** again.

---

### 3.4 Test the Scanner

**Select a Port**

1. In the "Available Scanner Ports" list, select the appropriate port by clicking the radio button.
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

### 3.5 Save Configuration

**Finalize Setup**

1. After a successful scanner test, click the **Save Configuration** button.
2. The application will save the selected COM port to `Common/config.json`.
3. A confirmation message will display: "Scanner port [port] has been saved to config.json"

**Verification**

The configuration is now saved and will be used by all weighing and tracking applications that require QR scanner input.

---

### 3.6 Close the Application

1. Review the status log to confirm successful configuration.
2. Click the **Close** button to exit the Scanner Setup application.

---


## Section 4 — Revision History

Revision: 2
- Effective Date: 2026-04-29
- Approved By: President/CEO

Change Summary:
- Rev 1 – Initial release
- Rev 2 - Add USB Barcode Scanner
