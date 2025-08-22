from blocked_ips import is_ip_blocked
#libraries for the SIEM 
from collections import deque
import logging
import datetime
import json
import time
import numpy as np
import os  # Added for file path handling


# Path to the logs database file
LOG_DB_PATH = os.path.join(os.path.dirname(__file__), "logs.json")  # Updated to use an absolute path for better compatibility

# Ensure the logs.json file exists
if not os.path.exists(LOG_DB_PATH):
    with open(LOG_DB_PATH, "w") as f:
        json.dump([], f)

# Helper to load logs from JSON file
def load_logs():
	try:
		with open(LOG_DB_PATH, "r") as f:
			logs = json.load(f)
		return logs[-500:]  # Only last 500 logs
	except Exception:
		return []

# Helper to save logs to JSON file
def save_logs(logs):
	try:
		with open(LOG_DB_PATH, "w") as f:
			json.dump(logs, f, indent=2)
	except Exception as e:
		print(f"Error saving logs to file: {e}")

# Flask server setup
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Added CORS for frontend compatibility

app = Flask(__name__)

# Dynamically configure CORS origins based on environment
trusted_origins = os.getenv("TRUSTED_ORIGINS", "http://localhost:8080").split(",")
CORS(app, resources={r"/*": {"origins": trusted_origins}})


def log_collection(src_ip, dest_ip, protocol, size, info=None):
    """
    Collects a log entry from network traffic and saves it to the logs database (JSON file).
    Also forwards the log to FastAPI server.
    """
    if is_ip_blocked(src_ip):
        print(f"Blocked IP {src_ip} attempted to send a packet. Ignored.")
        return
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "src_ip": src_ip,
        "dest_ip": dest_ip,
        "protocol": protocol,
        "size": size,
        "info": info
    }
    logs = load_logs()
    logs.append(log_entry)
    logs = logs[-500:]  # Keep only last 500 logs
    save_logs(logs)
    # Forward to FastAPI server
    try:
        import requests
        requests.post("http://127.0.0.1:8080/log", json=log_entry, timeout=5)
    except Exception as e:
        print(f"Error forwarding log to FastAPI: {e}")


# Endpoint to receive logs
@app.route("/log", methods=["POST"])
def receive_log():
    try:
        data = request.get_json()
        required_fields = ["src_ip", "dest_ip", "protocol", "size"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        log_collection(
            src_ip=data["src_ip"],
            dest_ip=data["dest_ip"],
            protocol=data["protocol"],
            size=data["size"],
            info=data.get("info")
        )
        return jsonify({"status": "Log received"}), 200
    except Exception as e:
        logging.error(f"Error in /log endpoint: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500


# Endpoint to view last 500 logs
@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        logs = load_logs()
        return jsonify(logs), 200
    except Exception as e:
        logging.error(f"Error in /logs endpoint: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

# Endpoint to refresh logs (for frontend button)
@app.route("/refresh", methods=["POST"])
def refresh_logs():
    try:
        logs = load_logs()
        return jsonify({"status": "Logs refreshed", "logs": logs}), 200
    except Exception as e:
        logging.error(f"Error in /refresh endpoint: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/")
def index():
    return render_template("index.html")  # Ensure the file name matches the one in the templates directory


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Use debug=True only in development, and ensure the port is configurable
    import os
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 8080))  # Allow overriding the port via an environment variable
    app.run(host="0.0.0.0", port=port, debug=debug_mode)


    port = int(os.getenv("PORT", 8080))  # Allow overriding the port via an environment variable
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

