import json
import os
import smtplib
import ssl
import subprocess
from email.message import EmailMessage
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

NAS_HOST = "192.168.1.153"   # <-- your NAS IP
#DSM_URL = "https://192.168.1.153:5001"
DSM_URL = "https://serviceadkhempco.us6.quickconnect.to/webman/3rdparty/SurveillanceStation/"

FAILS_REQUIRED = 3
STATE_FILE = r"C:\nas_monitor\state.json"

# Gmail settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "service@adkhempco.com"
SMTP_PASS = "PUT_APP_PASSWORD_HERE"

ALERT_TO = "service@adkhempco.com"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"fail_count": 0, "is_down": False}


def save_state(state):
    print(f"Saving state: {state}")
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def send_email(subject, body):
    print(f"Sending email: {subject}\n{body}")
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
#        smtp.login(SMTP_USER, SMTP_PASS)
#        smtp.send_message(msg)


def ping_host(host):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "5000", host],
        capture_output=True
    )
    return result.returncode == 0


def check_dsm(url):
    try:
        req = Request(url, headers={"User-Agent": "NASMonitor"})
        with urlopen(req, timeout=5) as response:
#            print(f"DSM check response code: {response.status}")
            return True
    except:
        return False


def main():
    state = load_state()

#    ok = ping_host(NAS_HOST) or check_dsm(DSM_URL)
    ok = check_dsm(DSM_URL)

    if ok:
        if state["is_down"]:
            send_email(
                "AdkHempCo NAS BACK ONLINE",
                f"{NAS_HOST} is responding again."
            )
        state["fail_count"] = 0
        state["is_down"] = False
    else:
        state["fail_count"] += 1
        if state["fail_count"] >= FAILS_REQUIRED and not state["is_down"]:
            send_email(
                "ALERT: AdkHempCo NAS DOWN",
                f"{NAS_HOST} failed {state['fail_count']} checks."
            )
            state["is_down"] = True

    save_state(state)


if __name__ == "__main__":
    main()