import json
import os
import smtplib
import ssl
import subprocess
import time
from email.message import EmailMessage
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from supabase import create_client, Client
from datetime import datetime

supabase_url = "https://figubkupxgxcrxtvsoji.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpZ3Via3VweGd4Y3J4dHZzb2ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjAyNjk4NTksImV4cCI6MjAzNTg0NTg1OX0.049XyTPGjxGqliuBWnk1HWEBypP_J76h73qfLwCQxpw"
supabase: Client = create_client(supabase_url, supabase_key)

NAS_HOST = "192.168.1.10"   # <-- your NAS IP
DSM_URL = "https://192.168.1.10:5001/webman/3rdparty/SurveillanceStation/"
#DSM_URL = "https://192.168.1.153:5001"
#DSM_URL = "https://serviceadkhempco.us6.quickconnect.to/webman/3rdparty/SurveillanceStation/"

FAILS_REQUIRED = 3
CHECK_INTERVAL = 60  # seconds between checks
HEARTBEAT_INTERVAL = 86400  # seconds between heartbeats (24 hours)
#STATE_FILE = r"C:\nas_monitor\state.json"
import os

STATE_FILE = os.path.expanduser("~/nas_monitor/state.json")

# Gmail settings
#SMTP_SERVER = "smtp.gmail.com"
#SMTP_PORT = 465
#SMTP_USER = "service@adkhempco.com"
#SMTP_PASS = "hemphouse26"

SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 465
SMTP_USER = "dbrown1262@verizon.net"
SMTP_PASS = "metf eixc laeg yvir"

#ALERT_TO = "service@adkhempco.com"
ALERT_TO = "dbrown1262@verizon.net"


def log_to_supabase(status, logdesc):
    try:
        supabase.schema("scale").table("naslog").insert({"status": status, "logdesc": logdesc}).execute()
    except Exception as e:
        print(f"Supabase log error: {e}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"fail_count": 0, "is_down": False, "last_heartbeat": 0,
            "netstat": "up", "internet_down_since": None, "internet_fail_count": 0}


def save_state(state):
    print(f"Saving state: {state}")
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
    try:
        status = "down" if state["is_down"] else "ok"
        supabase.schema("scale").table("nasstat").update({"statdate": "now()", "status": status}).eq("id", 1).execute()
    except Exception as e:
        print(f"Supabase nasstat update error: {e}")

def send_email(subject, body):
    try:
        print(f"Sending email: {subject}\n{body}", flush=True)

        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_TO
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=15) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

    except Exception as e:
        print(f"Email error: {e}", flush=True)
        log_to_supabase("email_error", f"Email failed: {e}")

def ping_host(host):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "5000", host],
        capture_output=True
    )
    return result.returncode == 0


def check_internet():
    """Check internet by reaching a known external host."""
    try:
        ctx = ssl.create_default_context()
        req = Request("https://www.google.com", headers={"User-Agent": "NASMonitor"})
        with urlopen(req, timeout=5, context=ctx) as response:
            return True
    except Exception as e:
        print(f"Internet check failed: {e}", flush=True)
        return False


def check_dsm(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={"User-Agent": "NASMonitor"})
        with urlopen(req, timeout=5, context=ctx) as response:
            print(f"DSM check OK: {response.status}", flush=True)
            return True
    except Exception as e:
        print(f"DSM check failed: {e}", flush=True)
        return False


def main():
    state = load_state()

    # --- Internet connectivity check ---
    internet_ok = check_internet()
    if internet_ok:
        if state.get("netstat") == "down" and state.get("internet_down_since"):
            up_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            down_since = state["internet_down_since"]
            print(f"Internet restored at {up_time} (was down since {down_since})", flush=True)
            send_email(
                "AdkHempCo Internet RESTORED",
                f"Internet connectivity restored at {up_time}.\nWas down since {down_since}."
            )
            log_to_supabase("internet_up",
                f"Internet restored at {up_time}. Was down since {down_since}.")
            state["internet_down_since"] = None
        state["netstat"] = "up"
        state["internet_fail_count"] = 0
    else:
        state["internet_fail_count"] = state.get("internet_fail_count", 0) + 1
        print(f"Internet check failed (attempt {state['internet_fail_count']})", flush=True)
        if state["internet_fail_count"] == 1:
            log_to_supabase("internet_fail", f"Internet check failed (attempt 1) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")
        if state["internet_fail_count"] >= FAILS_REQUIRED and state.get("netstat") != "down":
            state["internet_down_since"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Internet marked down at {state['internet_down_since']}", flush=True)
            state["netstat"] = "down"
            log_to_supabase("internet_down", f"Internet went down at {state['internet_down_since']}.")

#    ok = ping_host(NAS_HOST) or check_dsm(DSM_URL)
    ok = check_dsm(DSM_URL)

    if ok:
        if state["is_down"]:
            send_email(
                "AdkHempCo NAS BACK ONLINE",
                f"{NAS_HOST} is responding again."
            )
            log_to_supabase("up", f"NAS is responding again.")
        state["fail_count"] = 0
        state["is_down"] = False
    else:
        state["fail_count"] += 1
        if state["fail_count"] >= FAILS_REQUIRED and not state["is_down"]:
            send_email(
                "ALERT: AdkHempCo NAS DOWN",
                f"{NAS_HOST} failed {state['fail_count']} checks."
            )
            log_to_supabase("down", f"NAS failed {state['fail_count']} checks.")
            state["is_down"] = True

    save_state(state)


if __name__ == "__main__":
    send_email("NAS Monitor Started", f"Monitoring started for camera storage unit (NAS). Initial state: {load_state()}")
    log_to_supabase("info", f"Monitoring started for camera storage unit (NAS). Initial state: {load_state()}")
    while True:
        main()
        state = load_state()
        print(f"Current state: {state}", flush=True)
        if time.time() - state.get("last_heartbeat", 0) >= HEARTBEAT_INTERVAL:
            send_email("NAS Monitor Heartbeat", f"NAS monitor is running. Current state: {state}")
            log_to_supabase("heartbeat", f"NAS monitor is running. Current state: {state}")
            state["last_heartbeat"] = time.time()
            state["last_heartbeat_str"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_state(state)
        time.sleep(CHECK_INTERVAL)
