import json
import os

HONEYPOT_IPS_PATH = os.path.join(os.path.dirname(__file__), "honeypot_ips.json")

def log_honeypot_ip(ip):
    try:
        with open(HONEYPOT_IPS_PATH, "r") as f:
            honeypot_ips = set(json.load(f))
    except Exception:
        honeypot_ips = set()
    honeypot_ips.add(ip)
    with open(HONEYPOT_IPS_PATH, "w") as f:
        json.dump(list(honeypot_ips), f, indent=2)

def honeypot(ip):
    log_honeypot_ip(ip)
    return {"message": "Access Denied"}
