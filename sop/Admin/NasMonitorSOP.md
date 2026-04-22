# NAS Monitor Raspberry Pi Setup SOP (Supabase Integrated)

## 1. Purpose

This SOP defines the procedure to configure a Raspberry Pi to run a Python-based NAS monitoring service that logs all activity to Supabase for audit, alerting, and compliance purposes.

---

## 2. System Overview

The NAS Monitor system:

* Runs continuously as a system service
* Monitors NAS availability
* Sends alerts on failure/recovery
* Logs all events to Supabase

### Data Storage

Data are stored in Supabase tables in the Cloud:

* `scale.naslog` → Event history (audit log)
* `scale.nasstat` → Current status (latest state)

---

## 3. Hardware & Software Requirements

* Raspberry Pi 4
* MicroSD card (16GB+)
* Ethernet connection
* Power supply
* Workstation with Raspberry Pi Imager
* Python 3
* Supabase project (API + service key)

---

## 4. Flash Operating System

1. Download Raspberry Pi Imager and place in:

   ```
   scale/Admin
   ```

2. Run Imager:

   * Device: **Pi 4**
   * OS: **Raspberry Pi OS Lite (64-bit)**

3. Configure settings:

   * Hostname: `nas-monitor`
   * Username: `adkadmin`
   * Password: `Adk1891`
   * Enable SSH

4. Flash SD card and insert into Pi.

---

## 5. Initial Boot & Access

```bash
ping nas-monitor
ssh adkadmin@nas-monitor
```

---

## 6. System Update

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 7. Install Python Environment

```bash
sudo apt install python3-pip -y
sudo apt install python3-venv -y

python3 -m venv ~/nas-env
source ~/nas-env/bin/activate
```

---

## 8. Install Python Packages

```bash
pip install requests
pip install supabase
```

(Optional)

```bash
pip install python-dotenv websocket-client pytz
```

Save environment:

```bash
pip freeze > ~/requirements.txt
```

---

## 9. Deploy Monitoring Script

```bash
scp "C:\Users\Adk\Documents\scale\Common\NASmonitor.py" adkadmin@nas-monitor:~
```

Verify:

```bash
ls -l ~
```

---

## 10. Supabase Configuration

Ensure the script contains:

* Supabase URL
* Service key
* Correct schema: `scale`

### Required Tables

#### `scale.naslog` (Event Log)

Recommended structure:

* timestamp
* status
* message

#### `scale.nasstat` (Current Status)

Recommended structure:

* stat_date
* current_status

---

## 11. Test Script Manually

```bash
source ~/nas-env/bin/activate
python ~/NASmonitor.py
```

Confirm:

* Script runs without errors
* NAS connectivity works
* Email alerts function
* Record is written to `scale.naslog`
* `scale.nasstat` updates correctly

---

## 12. Create System Service

```bash
sudo nano /etc/systemd/system/nas-monitor.service
```

```ini
[Unit]
Description=NAS Monitor Python Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=adkadmin
WorkingDirectory=/home/adkadmin

ExecStartPre=/bin/sleep 10
ExecStart=/home/adkadmin/nas-env/bin/python /home/adkadmin/NASmonitor.py

Restart=always
RestartSec=10

StandardOutput=append:/home/adkadmin/nas-monitor.log
StandardError=append:/home/adkadmin/nas-monitor.log

[Install]
WantedBy=multi-user.target
```

---

## 13. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable nas-monitor.service
sudo systemctl start nas-monitor.service
```

---

## 14. Verify Service

```bash
sudo systemctl status nas-monitor.service
```

Expected:

```
Active: active (running)
```

---

## 15. Monitor Logs

```bash
journalctl -u nas-monitor.service -f
tail -f ~/nas-monitor.log
```

Primary audit log is stored in Supabase (`scale.naslog`).

---

## 16. Reboot Validation

```bash
sudo reboot
```

After reboot:

```bash
ssh adkadmin@nas-monitor
sudo systemctl status nas-monitor.service
```

---

## 17. Functional Testing

Perform the following:

* Confirm normal logging to `scale.naslog`
* Confirm `scale.nasstat` updates
* Simulate NAS outage → verify:

  * Alert sent
  * Failure logged in `naslog`
* Restore NAS → verify:

  * Recovery logged
  * Status updated

---

## 18. Network Configuration

Assign a stable IP:

* DHCP reservation in router
  **OR**
* Static IP on Pi

---

## 19. NAS Log View Application

The NAS log can be viewed using the NAS View application, which is accessed through the Administration Menu.  The application displays the current status of the NAS and a list of log entries.  User can enter Start and End date to limit the list to a specific period.

---

## 20. Revision History

| Version | Date       | Description                |
| ------- | ---------- | -------------------------- |
| 1.0     | 2026-04-20 | Initial version            |
