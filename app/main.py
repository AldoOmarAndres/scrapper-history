from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.endpoints import router
import os

app = FastAPI(title="Monitor de Tasas")

# Configurar carpeta de templates
# Usamos una ruta absoluta para evitar errores de "directory not found"
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Incluir tus rutas de API
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Renderiza el dashboard principal"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)