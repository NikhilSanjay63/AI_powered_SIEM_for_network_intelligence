
#libraries for the SIEM 
from collections import deque
import logging
import datetime
import json
import time
import numpy as np


# Path to the logs database file
LOG_DB_PATH = "logs.json"

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

app = Flask(__name__)


def log_collection(src_ip, dest_ip, protocol, size, info=None):
	"""
	Collects a log entry from network traffic and saves it to the logs database (JSON file).
	"""
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


# Endpoint to receive logs
@app.route("/log", methods=["POST"])
def receive_log():
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



# Endpoint to view last 500 logs
@app.route("/logs", methods=["GET"])
def get_logs():
	logs = load_logs()
	return jsonify(logs), 200


# Endpoint to refresh logs (for frontend button)
@app.route("/refresh", methods=["POST"])
def refresh_logs():
	logs = load_logs()
	return jsonify({"status": "Logs refreshed", "logs": logs}), 200



# Route to serve the frontend log viewer
@app.route("/")
def index():
	return render_template("index.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)

