# AI-Powered SIEM for Network Intelligence

This project is a simple yet powerful AI-powered Security Information and Event Management (SIEM) system designed to monitor network traffic, detect potential threats, and automatically block malicious IP addresses.

## Features

- **Real-time Log Collection:** Collects and displays network logs in real-time.
- **AI-Powered Threat Detection:** Utilizes a simple AI brain to learn baseline network behavior and detect anomalies.
- **Automatic IP Blocking:** Automatically blocks IPs that are identified as malicious.
- **Web-Based Dashboard:** A user-friendly web interface for monitoring network activity and viewing blocked IPs.
- **Simulated Attack and Normal Traffic:** Includes scripts to simulate both normal and malicious network traffic for testing and demonstration purposes.

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/AI_powered_SIEM_for_network_intelligence.git
    cd AI_powered_SIEM_for_network_intelligence
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the SIEM Server:**

    ```bash
    uvicorn fastapi_server:app --reload
    ```

    This will start the FastAPI server and the AI brain. The web interface will be available at `http://127.0.0.1:8000`.

2.  **Simulate Normal Traffic (Optional):**

    Open a new terminal and run the following command to simulate normal network traffic:

    ```bash
    python normal_traffic.py
    ```

3.  **Simulate an Attack (Optional):**

    Open another new terminal and run the following command to simulate an attack:

    ```bash
    python Attacker.py
    ```

    The AI brain will detect the attack and block the malicious IPs. You can view the blocked IPs in the `blocked_ips.json` file and on the web dashboard.

## Project Structure

```
├── .env.example
├── .gitignore
├── ai_brain.py
├── Attacker.py
├── blocked_ips.json
├── blocked_ips.py
├── fastapi_server.py
├── honeypot_ips.json
├── honeypot.py
├── logs.json
├── normal_traffic.py
├── README.md
├── requirements.txt
├── server_api.py
├── Server.py
├── test_honeypot.py
├── .git
│   └── ...
├── .vscode
│   └── tasks.json
├── static
└── templates
    └── index.html
```

-   `fastapi_server.py`: The main FastAPI application that serves the web interface and the API.
-   `server_api.py`: Defines the API endpoints for the SIEM.
-   `ai_brain.py`: The AI brain that monitors the logs, learns the baseline, and detects attacks.
-   `blocked_ips.py`: Manages the list of blocked IPs.
-   `Attacker.py`: A script to simulate a network attack.
-   `normal_traffic.py`: A script to simulate normal network traffic.
-   `logs.json`: A file to store the network logs.
-   `blocked_ips.json`: A file to store the blocked IPs.
-   `templates/index.html`: The HTML template for the web dashboard.
