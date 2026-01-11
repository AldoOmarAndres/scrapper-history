from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
import os
from app.api.endpoints import router
from app.services.scraper import run_scraping_logic
from app.services.redis_db import save_scraped_data

ARG_TIMEZONE = ZoneInfo("America/Argentina/Buenos_Aires")

# SCHEDULER
def scheduled_scraping_job():
    data = run_scraping_logic()
    
    if data.get("status") == "success":
        save_scraped_data(data["data"])
        print("Datos guardados en Redis.")
    else:
        print(f"Fallo en el scraping programado: {data.get('message')}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    
    # CONFIGURACIÓN DEL HORARIO (10:30 a 17:00 Argentina)

    # Regla para horario de 10:30 a 10:55
    scheduler.add_job(
        scheduled_scraping_job,
        trigger=CronTrigger(
            hour=10, 
            minute='30-59/5', 
            timezone=ARG_TIMEZONE
        )
    )

    # Regla para horario de 11:00 a 16:55 (cada 5 min para las horas completas)
    scheduler.add_job(
        scheduled_scraping_job,
        trigger=CronTrigger(
            hour='11-16', 
            minute='*/5', 
            timezone=ARG_TIMEZONE
        )
    )

    scheduler.start()
    print(f"Scheduler iniciado. Zona horaria: {ARG_TIMEZONE}")
    
    yield
    
    scheduler.shutdown()


app = FastAPI(title="Monitor de Tasas", lifespan=lifespan)
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})