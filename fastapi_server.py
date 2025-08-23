from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from server_api import router as api_router
from ai_brain import AIBrainSIEM
import threading

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(api_router)

@app.on_event("startup")
def startup_event():
    ai_brain = AIBrainSIEM()
    # Run the AI brain in a separate thread
    thread = threading.Thread(target=run_ai_brain, args=(ai_brain,))
    thread.daemon = True
    thread.start()

def run_ai_brain(ai_brain: AIBrainSIEM):
    ai_brain.learn_baseline(duration=30)
    ai_brain.monitor()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.mount("/static", StaticFiles(directory="static"), name="static")