from blocked_ips import is_ip_blocked
import requests
import random
import string
import threading
import time
from blocked_ips import is_ip_blocked

def random_ip():
    return '.'.join(str(random.randint(1, 254)) for _ in range(4))

def send_packet(server_ip, server_port, src_ip, packet_type="normal"):
    url = f"http://{server_ip}:{server_port}/log"
    if is_ip_blocked(src_ip):
        print(f"IP {src_ip} is blocked. Skipping packet.")
        return
    dest_ip = server_ip
    protocol = random.choice(["TCP", "UDP", "ICMP"])
    size = random.randint(40, 1500)
    info = f'{packet_type} packet: ' + ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    payload = {
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "protocol": protocol,
        "size": size,
        "info": info
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Server responded with status {response.status_code}: {response.text}")
    except requests.exceptions.Timeout:
        print("Timeout error: Server did not respond within 10 seconds.")
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server.")
    except Exception as e:
        print(f"Error sending packet: {e}")


def simulate_attack(server_ip, server_port, duration=30):
    attack_ips = [
        "192.168.1.100", "10.0.0.5", "172.16.0.9", "203.0.113.77", "198.51.100.23",
        "8.8.8.8", "185.199.108.153", "45.33.32.156", "123.45.67.89", "156.154.70.1"
    ]
    start_time = time.time()
    while time.time() - start_time < duration:
        # Simulate distributed attack: pick random attack IPs for each burst
        burst_ips = random.sample(attack_ips, k=random.randint(2, 5))
        for ip in burst_ips:
            for _ in range(random.randint(10, 30)):
                send_packet(server_ip, server_port, ip, packet_type="attack")
                time.sleep(random.uniform(0.005, 0.02))
        # Short pause between bursts
        time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    # Simulate realistic attack traffic for 30 seconds
    simulate_attack("127.0.0.1", 8080, duration=30)
