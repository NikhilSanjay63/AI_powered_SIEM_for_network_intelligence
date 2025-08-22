import json
import os

BLOCKED_IPS_PATH = os.path.join(os.path.dirname(__file__), "blocked_ips.json")

def get_blocked_ips():
    try:
        with open(BLOCKED_IPS_PATH, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def is_ip_blocked(ip):
    return ip in get_blocked_ips()
