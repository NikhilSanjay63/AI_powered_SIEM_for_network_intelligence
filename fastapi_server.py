from blocked_ips import is_ip_blocked
from honeypot import honeypot
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import datetime
from threading import Lock

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

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/log")
async def receive_log(request: Request):
    try:
        data = await request.json()
        src_ip = data.get("src_ip")
        print(f"[DEBUG] Received log from src_ip: {src_ip} (type: {type(src_ip)})")
        # Print current blocklist for debugging
        from blocked_ips import get_blocked_ips
        current_blocked = get_blocked_ips()
        print(f"[DEBUG] Current blocklist: {current_blocked}")
        print(f"[DEBUG] Is src_ip in blocklist? {src_ip in current_blocked}")
        # Step 1 & 2: Intercept and check against blocklist
        if src_ip and src_ip in current_blocked:
            print(f"[DEBUG] src_ip {src_ip} is BLOCKED. Triggering honeypot.")
            # Step 3 & 4: Redirect to honeypot
            return JSONResponse(honeypot(src_ip))
        else:
            print(f"[DEBUG] src_ip {src_ip} is NOT blocked. Proceeding with normal log.")
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
        print(f"[DEBUG] Log from src_ip {src_ip} processed normally.")
        return JSONResponse({"status": "Log received"})
    except Exception as e:
        print(f"[ERROR] Exception in /log route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs():
    with logs_lock:
        return JSONResponse(logs)

@app.post("/refresh")
async def refresh_logs():
    with logs_lock:
        return JSONResponse({"status": "Logs refreshed", "logs": logs})

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.mount("/static", StaticFiles(directory="static"), name="static")
