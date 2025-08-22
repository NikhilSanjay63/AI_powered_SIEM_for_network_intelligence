import time
import random
import string
import requests

# Function to generate a random IP address
def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

# Function to simulate sending packets to the server at a normal rate
def send_normal_traffic(server_ip, server_port, packet_count=100, interval=0.5):
    url = f"http://{server_ip}:{server_port}/log"
    for _ in range(packet_count):
        src_ip = random_ip()
        dest_ip = server_ip
        protocol = random.choice(["TCP", "UDP"])
        size = random.randint(40, 1500)
        info = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        payload = {
            "src_ip": src_ip,
            "dest_ip": dest_ip,
            "protocol": protocol,
            "size": size,
            "info": info
        }
        try:
            response = requests.post(url, json=payload)
            print(f"Sent: {payload} | Response: {response.status_code}")
        except Exception as e:
            print(f"Error sending log: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    # Example usage: send packets to localhost:8080
    send_normal_traffic("127.0.0.1", 8080)
