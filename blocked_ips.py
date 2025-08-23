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

def add_blocked_ip(ip):
    blocked_ips = get_blocked_ips()
    blocked_ips.add(ip)
    with open(BLOCKED_IPS_PATH, "w") as f:
        json.dump(list(blocked_ips), f, indent=2)

def remove_blocked_ip(ip):
    blocked_ips = get_blocked_ips()
    blocked_ips.discard(ip)
    with open(BLOCKED_IPS_PATH, "w") as f:
        json.dump(list(blocked_ips), f, indent=2)