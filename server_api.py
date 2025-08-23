from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import datetime
from threading import Lock
from collections import Counter
from blocked_ips import is_ip_blocked, add_blocked_ip, get_blocked_ips, remove_blocked_ip
from honeypot import honeypot

LOG_DB_PATH = os.path.join(os.path.dirname(__file__), "logs.json")
if not os.path.exists(LOG_DB_PATH):
    with open(LOG_DB_PATH, "w") as f:
        json.dump([], f)

logs_lock = Lock()
try:
    with open(LOG_DB_PATH, "r") as f:
        logs = json.load(f)
except Exception:
    logs = []
flush_interval = 50
packet_counter = 0

router = APIRouter()

@router.post("/log")
async def receive_log(request: Request):
    try:
        data = await request.json()
        src_ip = data.get("src_ip")
        
        if src_ip and is_ip_blocked(src_ip):
            return JSONResponse(honeypot(src_ip))
        
        required_fields = ["src_ip", "dest_ip", "protocol", "size"]
        if not all(field in data for field in required_fields):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "src_ip": data["src_ip"],
            "dest_ip": data["dest_ip"],
            "protocol": data["protocol"],
            "size": data["size"],
            "info": data.get("info")
        }
        
        global logs, packet_counter
        with logs_lock:
            logs.append(log_entry)
            packet_counter += 1
            if packet_counter >= flush_interval:
                with open(LOG_DB_PATH, "w") as f:
                    json.dump(logs, f, indent=2)
                packet_counter = 0
        
        return JSONResponse({"status": "Log received"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs():
    with logs_lock:
        return JSONResponse(logs)

@router.post("/refresh")
async def refresh_logs():
    with logs_lock:
        return JSONResponse({"status": "Logs refreshed", "logs": logs})

@router.post("/block_ip")
async def block_ip(request: Request):
    try:
        data = await request.json()
        ip_to_block = data.get("ip")
        if ip_to_block:
            add_blocked_ip(ip_to_block)
            return JSONResponse({"status": f"IP {ip_to_block} blocked successfully."})
        else:
            raise HTTPException(status_code=400, detail="IP address not provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unblock_ip")
async def unblock_ip(request: Request):
    try:
        data = await request.json()
        ip_to_unblock = data.get("ip")
        if ip_to_unblock:
            remove_blocked_ip(ip_to_unblock)
            return JSONResponse({"status": f"IP {ip_to_unblock} unblocked successfully."})
        else:
            raise HTTPException(status_code=400, detail="IP address not provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blocked_ips")
async def get_blocked_ips_route():
    return JSONResponse({"blocked_ips": get_blocked_ips()})

@router.get("/protocol_distribution")
async def get_protocol_distribution():
    with logs_lock:
        protocols = [log.get("protocol") for log in logs]
        protocol_counts = Counter(protocols)
        return JSONResponse(protocol_counts)

@router.get("/log_trend")
async def get_log_trend():
    with logs_lock:
        log_times = [datetime.datetime.fromisoformat(log.get("timestamp")) for log in logs]
        log_times.sort()
        trend_data = {}
        for time in log_times:
            hour = time.strftime("%Y-%m-%d %H:00:00")
            if hour in trend_data:
                trend_data[hour] += 1
            else:
                trend_data[hour] = 1
        return JSONResponse(trend_data)