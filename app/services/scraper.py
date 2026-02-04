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
    fecha_hora_web: str

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

                # fecha autogenerada en horario de Argentina (formato dd/mm/YYYY HH:MM:SS)
                fecha_str = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%d/%m/%Y %H:%M:%S")

                record = RateRecord(
                    plazo=plazo,
                    tasa_tomadora=cols[5].text.strip(),
                    fecha_hora_web=fecha_str,
                )

                rd = record.model_dump(mode="json")
                extracted_data.append(rd)
            except Exception as e:
                print(f"Error parseando fila: {e}")
                continue

        try:
            extracted_data.sort(key=lambda x: datetime.strptime(x.get('fecha_hora_web') or "01/01/1900 00:00:00", "%d/%m/%Y %H:%M:%S"))
        except Exception:
            pass

        return {
            "status": "success",
            "total_records": len(extracted_data),
            "data": extracted_data
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}