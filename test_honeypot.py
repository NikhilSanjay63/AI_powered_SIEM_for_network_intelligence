import requests
import json
import os

BLOCKED_IPS_PATH = os.path.join(os.path.dirname(__file__), "blocked_ips.json")

def get_blocked_ips():
    try:
        with open(BLOCKED_IPS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []

def send_blocked_ip_request(server_ip, server_port):
    blocked_ips = get_blocked_ips()
    if not blocked_ips:
        print("No blocked IPs found.")
        return
    for ip in blocked_ips:
        payload = {
            "src_ip": ip,
            "dest_ip": server_ip,
            "protocol": "TCP",
            "size": 100,
            "info": "Test honeypot request"
        }
        try:
            response = requests.post(f"http://{server_ip}:{server_port}/log", json=payload)
            print(f"Sent request from blocked IP {ip}. Response: {response.json()}")
        except Exception as e:
            print(f"Error sending request from blocked IP {ip}: {e}")

if __name__ == "__main__":
    send_blocked_ip_request("127.0.0.1", 8080)
