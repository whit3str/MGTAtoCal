from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn

from config import logger
from database import get_connection, init_db
from scryfall_fetcher import fetch_upcoming_sets
from wallpaper_downloader import download_missing_wallpapers
from calendar_manager import sync_calendar_events

def run_all_tasks():
    """Automated task that runs the full pipeline."""
    logger.info("=== STARTING AUTOMATED DAILY SYNC ===")
    try:
        fetch_upcoming_sets()
        download_missing_wallpapers()
        sync_calendar_events()
        logger.info("=== AUTOMATED SYNC COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        logger.error(f"Error during automated sync: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and start Scheduler
    init_db()
    
    scheduler = BackgroundScheduler()
    # Run once every 24 hours
    scheduler.add_job(run_all_tasks, 'interval', hours=24)
    scheduler.start()
    logger.info("Background Scheduler started (Daily sync every 24h)")
    
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="MGTAtoCal Dashboard", lifespan=lifespan)

# app.mount and other routes follow...

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code, name, release_date, wallpaper_downloaded, gcal_created FROM magic_sets ORDER BY release_date")
        sets = [dict(row) for row in cursor.fetchall()]
        
    return templates.TemplateResponse(request=request, name="index.html", context={"sets": sets})

@app.post("/api/fetch")
async def api_fetch(background_tasks: BackgroundTasks):
    background_tasks.add_task(fetch_upcoming_sets)
    return {"message": "Synchronisation Scryfall démarrée en arrière-plan."}

@app.post("/api/wallpapers")
async def api_wallpapers(background_tasks: BackgroundTasks):
    background_tasks.add_task(download_missing_wallpapers)
    return {"message": "Téléchargement des Wallpapers démarré en arrière-plan."}

@app.post("/api/calendar")
async def api_calendar(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_calendar_events)
    return {"message": "Création Google Calendar démarrée en arrière-plan."}

@app.post("/api/all")
async def api_all(background_tasks: BackgroundTasks):
    def run_all():
        fetch_upcoming_sets()
        download_missing_wallpapers()
        sync_calendar_events()
    background_tasks.add_task(run_all)
    return {"message": "Pipeline complet démarré en arrière-plan."}

if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
