import requests
import random
import string
import threading
import time

def spoofed_ip():
    return '.'.join(str(random.randint(1, 254)) for _ in range(4))

def send_attack_packet(server_ip, server_port):
    url = f"http://{server_ip}:{server_port}/log"
    src_ip = spoofed_ip()
    dest_ip = server_ip
    protocol = random.choice(["TCP", "UDP"])
    size = random.randint(100, 1500)
    info = 'packet: ' + ''.join(random.choices(string.ascii_letters + string.digits, k=20))
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
        print(f"Error sending attack packet: {e}")

def ddos_attack(server_ip, server_port, num_packets=1000, threads=50, duration=15):
    start_time = time.time()
    def attack_thread():
        while time.time() - start_time < duration:
            send_attack_packet(server_ip, server_port)
            time.sleep(0.01)
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=attack_thread)
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()

if __name__ == "__main__":
    # Point to FastAPI server
    ddos_attack("127.0.0.1", 8080, num_packets=1000, threads=50, duration=15)
