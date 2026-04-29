# SOP: UbiBot WS1 Sensor Setup and Remote Monitoring

## 1. Purpose
To define the procedure for installation, configuration, and verification of the UbiBot WS1 environmental sensor to ensure continuous remote monitoring and data availability for facility compliance and operational control.

## 2. Scope
This SOP applies to all UbiBot WS1 sensors deployed in cultivation, drying, curing, and storage areas.

## 3. Responsibilities
- **Owner / CEO**
  - Approves system configuration and alert thresholds
- **Facility Manager**
  - Installs and configures sensors
  - Verifies operation and alerts
- **Staff**
  - Respond to alerts and document corrective actions

## 4. Equipment and Materials
- UbiBot WS1 Sensor
- USB Power Adapter and Cable
- WiFi Network (2.4 GHz required)
- Mobile device or computer
- UbiBot App or web console
- UbiBot cloud account

## 5. Procedure

### 5.1 Account Setup
1. Access https://console.ubibot.com or install the UbiBot mobile app.
2. Create a UbiBot account using company email credentials.
3. Record login credentials in the facility password management system.

### 5.2 Device Power-Up
1. Connect the WS1 sensor to power using the USB cable.
2. Confirm the device powers on (LED indicator active).

### 5.3 Device Registration
1. Open the UbiBot App or web console.
2. Select **Add Device**.
3. Scan the QR code on the WS1 device or manually enter the Device ID.
4. Assign a device name using the format:


### 5.4 WiFi Configuration
1. Place the device in configuration mode (per manufacturer instructions).
2. Connect to the device hotspot (if prompted).
3. Select facility WiFi network (2.4 GHz only).
4. Enter WiFi credentials.
5. Confirm the device connects successfully to the network.

### 5.5 Sensor Placement
1. Install the sensor:
- At canopy height for grow rooms
- At product level for drying/curing areas
2. Avoid placement:
- Direct airflow from vents or fans
- Direct light or heat sources
3. Secure device to prevent movement or tampering.
4. Record sensor location in facility records.

### 5.6 Remote Access Verification
1. Log into the UbiBot App or web console.
2. Confirm:
- Device appears online
- Temperature and humidity readings are updating
3. Verify timestamp accuracy.

### 5.7 Alert Configuration
1. Configure alert thresholds per room SOP:
- Temperature
- Humidity
- Light (if used for photoperiod verification)
2. Enable notifications:
- Email alerts
- SMS alerts (if configured)
3. Assign alert recipients (Owner, Facility Manager).

### 5.8 Data Logging and Retention
1. Confirm data logging interval (recommended: 5–15 minutes).
2. Verify data is stored in UbiBot cloud.
3. Export data as required for compliance or internal records.

### 5.9 Functional Verification
1. Perform initial verification:
- Confirm readings are reasonable vs known conditions
2. Trigger a test alert by temporarily exceeding a threshold.
3. Confirm alert delivery.

### 5.10 Documentation
Record the following:
- Device ID
- Location
- Installation date
- Assigned name
- Alert thresholds
- Verification results

## 6. Monitoring and Maintenance
- Review sensor data daily during active operations
- Verify device connectivity at start of each workday
- Inspect physical placement weekly
- Replace or service device if:
- Data is not updating
- Readings are inconsistent
- Device goes offline repeatedly

## 7. Deviations and Corrective Actions
- If device goes offline:
- Check power supply
- Verify WiFi connectivity
- Restart device
- If alerts fail:
- Verify notification settings
- Confirm contact information
- Document all deviations and corrective actions

## 8. Records
- Sensor Installation Log
- Alert Configuration Record
- Daily Verification Log (if required)

## 9. Environmental Monitoring System (UbiBot)

### 9.1 System Overview
Environmental conditions are monitored using UbiBot wireless sensors installed in all active cultivation and processing areas, including grow rooms, nursery, drying, and processing spaces.
Sensors continuously record environmental parameters including, as applicable:
- Temperature
- Relative Humidity
- Light levels
- Other parameters depending on sensor configuration
All sensor data is transmitted to and stored in the UbiBot Cloud platform.

### 9.2 System of Record
The UbiBot Cloud platform is designated as the official system of record for environmental monitoring data.
- Sensor data is stored in the cloud with multi-year retention capability
- Historical data is accessible via the UbiBot web console and mobile application
- Data may be exported from the system as needed for audit, investigation, or regulatory review
No duplicate environmental database is maintained internally.

### 9.3 Data Review and Use
Authorized personnel may access environmental data via:
- UbiBot web console
- UbiBot mobile application
Data is used for:
- Monitoring environmental conditions
- Verifying compliance with cultivation and processing requirements
- Supporting batch records and investigations when required

### 9.4 Alert and Notification System
UbiBot is configured to generate automated alerts for defined conditions, including but not limited to:
- Sensor offline status
- Environmental parameters outside defined thresholds
Alerts are transmitted via email notification to designated personnel.
Personnel receiving alerts are responsible for:
- Promptly investigating the condition
- Taking corrective action as required
- Documenting significant deviations per applicable SOPs

### 9.5 Routine Verification
To ensure system reliability, the following verification is performed:
- A designated employee reviews sensor status and alert functionality at least weekly
- Verification includes confirmation that:
  - All sensors are online
  - Data is actively recording
  - Alert settings are properly configured
Verification may be documented via checklist, log entry, or electronic record.

### 9.6 Data Retention and Availability
- Environmental monitoring data is retained within the UbiBot Cloud system
- Data is available for retrieval for a minimum period consistent with regulatory requirements
- Data exports may be generated upon request for audits, inspections, or internal review

### 9.7 System Limitations and Contingency
In the event of:
- Sensor failure
- Loss of connectivity
- Alert notification
Personnel shall:
1. Investigate the issue immediately
2. Restore monitoring capability as soon as possible
3. Document the event and any impact on product or process