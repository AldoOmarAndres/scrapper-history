import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os

load_dotenv()

TARGET_URL = os.getenv("URL_TARGET") or ""

class RateRecord(BaseModel):
    plazo: str
    tasa_tomadora: float
    fecha_hora_web: datetime

    # Validador para convertir TNA de str a float
    @field_validator("tasa_tomadora", mode='before')
    @classmethod
    def parse_float(cls, v):
        if isinstance(v, str):
            clean = v.replace('$', '').replace('%', '').strip()
            clean = clean.replace('.', '', -1).replace(',', '.', -1).strip()
            try:
                return float(clean)
            except ValueError:
                return 0.0
        return v

    @field_validator("fecha_hora_web", mode='before')
    @classmethod
    def parse_fecha(cls, v):
        # Acepta strings en formato dd/mm/YYYY HH:MM:SS o ISO, o datetime
        if isinstance(v, str):
            try:
                dt = datetime.strptime(v, "%d/%m/%Y %H:%M:%S")
                return dt.replace(tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
            except Exception:
                try:
                    return datetime.fromisoformat(v)
                except Exception:
                    return datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
            return v

        return v

def run_scraping_logic() -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.select_one('table')         
        if not table:
            return {"status": "error", "message": "No se encontró la tabla", "data": []}

        extracted_data = []
        rows = table.find_all('tr')

        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 7:
                continue

            try:
                plazo = cols[0].text.strip()
                moneda = cols[1].text.strip()
                if moneda != "PESOS" or int(plazo) > 30:
                    continue

                # fecha autogenerada en horario de Argentina (tipo datetime con tz)
                fecha_dt = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

                record = RateRecord(
                    plazo=plazo,
                    tasa_tomadora=cols[5].text.strip(),
                    fecha_hora_web=fecha_dt,
                )

                extracted_data.append(record)
            except Exception as e:
                print(f"Error parseando fila: {e}")
                continue

        # Ordenar por el campo datetime y serializar a formato JSON compatible
        try:
            extracted_data.sort(key=lambda r: r.fecha_hora_web)
            serialized = [r.model_dump(mode="json") for r in extracted_data]
        except Exception:
            serialized = [r.model_dump(mode="json") if isinstance(r, RateRecord) else r for r in extracted_data]

        return {
            "status": "success",
            "total_records": len(serialized),
            "data": serialized
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}