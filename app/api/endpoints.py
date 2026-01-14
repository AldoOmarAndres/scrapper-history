from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
import os
import secrets
from dotenv import load_dotenv
from app.services.redis_db import get_historical_data, delete_all_data
import csv
import io

load_dotenv()


router = APIRouter()

@router.get("/history")
def get_history_endpoint():
    """Devuelve la serie histórica almacenada en Redis"""
    history = get_historical_data()

    flat_data = []
    
    for entry in history:
        for row in entry['content']:
            flat_data.append(row)
            
    return {
        "status": "success",
        "count": len(flat_data),
        "data": flat_data
    }


@router.get("/export")
def export_history():
    """Descarga todo el historial como archivo CSV"""
    history = get_historical_data()

    flat_data = []
    for entry in history:
        for row in entry['content']:
            flat_data.append(row)

    # Definir columnas en orden deseado
    fieldnames = ['plazo', 'tasa_tomadora', 'fecha_hora_web', 'timestamp_scraped', 'hora']

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in flat_data:
        # Asegurar que los valores son strings/serializables
        safe_row = {k: (row.get(k, '') if row.get(k, '') is not None else '') for k in fieldnames}
        writer.writerow(safe_row)

    # Añadir BOM para compatibilidad con Excel y servir como bytes
    content = output.getvalue()
    content_bytes = content.encode('utf-8-sig')
    return Response(content=content_bytes, media_type='text/csv', headers={"Content-Disposition": 'attachment; filename="tasas_history.csv"'})


@router.delete("/history")
def delete_history(key: str):
    """Elimina todo el historial guardado en Redis.
    Requiere una clave para autorizar la eliminación.
    """

    env_key = os.getenv('DELETE_KEY')

    if not key or not secrets.compare_digest(str(key), str(env_key)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: invalid key")

    delete_all_data()
    return {"status": "success", "message": "Historial eliminado"}