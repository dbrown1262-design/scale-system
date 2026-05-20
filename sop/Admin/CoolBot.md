# SOP — CoolBot Pro Wi-Fi Setup and Remote Monitoring

## Section 1 — Purpose

This SOP describes the procedure for configuring the CoolBot Pro Wi-Fi interface for remote monitoring and alerting in the hash lab.

---

## Section 2 — Scope

This procedure applies to all CoolBot Pro units installed at the facility.

---

## Section 3 — Responsibilities

### Facility Staff
- Physically install and power the CoolBot system
- Connect the CoolBot to the facility Wi-Fi network
- Verify remote connectivity

### Management
- Maintain account credentials
- Respond to alarms or offline notifications
- Ensure continued network access

---

## Section 4 — Required Equipment

- CoolBot Pro controller
- CoolBot Jumper module
- Connected A/C unit
- Smartphone, tablet, or laptop with Wi-Fi
- Facility Wi-Fi network with internet access

---

## Section 5 — Network Requirements

The CoolBot system requires:
- 2.4 GHz Wi-Fi network
- Internet access
- WPA/WPA2 password-protected network

The CoolBot system may not function properly with:
- 5 GHz-only networks
- Hidden SSIDs
- Enterprise authentication systems
- Weak Wi-Fi signal areas

---

## Section 6 — Procedure

### 6.1 Verify Hardware Connections

1. Confirm the CoolBot Pro controller is powered on.
2. Confirm the CoolBot Jumper module is connected to the controller.
3. Verify all cables are fully seated.
4. Confirm indicator lights on the Jumper module are illuminated or blinking.

---

### 6.2 Connect to CoolBot Setup Network

1. Stand near the CoolBot unit.
2. Open Wi-Fi settings on the setup device.
3. Locate the temporary CoolBot wireless network.

Typical network names:
- CoolBot
- CoolBot-XXXX

4. Connect to the CoolBot network.

NOTE:
Internet access is not expected during this step.

---

### 6.3 Open Setup Portal

1. Open a web browser.
2. Navigate to:

https://cb.storeitcold.com

3. If the page does not load:
   - reconnect to the CoolBot Wi-Fi network
   - disable cellular data temporarily
   - try address:

     http://192.168.4.1

---

### 6.4 Configure Facility Wi-Fi

1. Select the facility Wi-Fi network.
2. Enter the Wi-Fi password.
3. Save settings.
4. Wait approximately 1–3 minutes for the CoolBot to reboot and connect.

---

### 6.5 Verify Remote Connectivity

1. Reconnect the setup device to the facility Wi-Fi network.
2. Open:

https://cb.storeitcold.com

3. Log into the CoolBot account.
4. Verify the unit appears online.
5. Confirm temperature data is updating properly.

---

## Section 7 — Troubleshooting

### 7.1 CoolBot Wi-Fi Network Not Visible

Possible causes:
- Jumper not connected
- Controller not powered
- Jumper malfunction

Corrective actions:
- Reboot the CoolBot
- Reconnect Jumper cable
- Move closer to the unit

---

### 7.2 CoolBot Will Not Connect to Facility Wi-Fi

Possible causes:
- Incorrect password
- Weak signal
- Unsupported Wi-Fi configuration
- 5 GHz-only network

Corrective actions:
- Verify password
- Verify 2.4 GHz Wi-Fi is enabled
- Move access point closer to the hash lab
- Install dedicated access point if needed

---

### 7.3 CoolBot Appears Offline

Possible causes:
- Internet outage
- Router reboot
- Weak signal
- DHCP/IP address change

Corrective actions:
- Reboot router
- Verify internet connectivity
- Verify Wi-Fi signal strength
- Configure DHCP reservation/static IP if available

---

## Section 8 — Monitoring

Management shall periodically verify:
- CoolBot is online
- Temperature data is updating
- Alerts are functioning properly

Any communication failure shall be investigated promptly.

---

## Section 9 — Records

The following records may be maintained:
- CoolBot account login information
- Wi-Fi configuration information
- Alarm notifications
- Maintenance or troubleshooting logs

---

## Section 10 — Revision History

Revision: 1
Effective Date: 2026-05-18
Approved By: President/CEO

Change Summary:
Rev 1 – Initial release