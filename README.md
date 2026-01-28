# Monitor de Tasas

Enlace: [Monitor de Tasas](https://scrapper-history.onrender.com/)

Una aplicación web construida con **FastAPI** que scrappea tasas de interés de un sitio web y las almacena en **Redis** para acceso histórico y análisis. La aplicación realiza scraping automático programado cada 2 minutos durante el horario de mercado (10:30 a 17:00 hora argentina).

## Descripción

Este proyecto monitorea tasas de interés (TNA) bancarias en pesos para diferentes plazos, extrae los datos automáticamente y los almacena con timestamps para análisis histórico. Proporciona una API REST y un dashboard web para consultar los datos.

Todos los servicios se encuentran desplegados en Render.

## Desafíos

El principal desafío que enfrenté fue mantener el servicio web de Render activo.
El free tier que ofrece Render es muy generoso y completo. Sin embargo la principal "desventaja" que tiene es que si un Web Service no detecta tráfico tras 15 minutos, el servicio pasa a un estado "inactivo" donde sigue desplegado pero se vuelve a inicializar recién cuando recibe una solicitud.
Esto genera no solo que cuando alguien quiera consultar el sitio tenga que esperar al rededor de 5 minutos hasta que termina de inicializarce el servicio, pero también implica que el scraper no podrá funcionar correctamente ya que Render lo da de baja.

Para solucionar esto, estoy usando [UptimeRobot](https://uptimerobot.com/), este servicio permite monitorear otros servicios enviando peticiones HEAD cada cierto tiempo. Este envío es suficiente para que Render detecte tráfico en el Web Service y no lo de de baja temporalmente.

## Características

- **Scraping Automático**: Extrae tasas de interés cada 2 minutos durante horario de mercado (10:30-17:00 Argentina)
- **Almacenamiento en Redis**: Persiste datos históricos con timestamps
- **API REST**: Endpoints para consultar datos actuales, históricos y exportar a CSV
- **Dashboard Web**: Interfaz HTML para visualización de datos
- **Validación de Datos**: Parseo y validación de tasas de interés con Pydantic
- **IaC** : Definición de recursos y servicios desplegados en el archivo ´render.yaml´.

## Estructura del Proyecto

```
scrapper-history/
 README.md                         
 requirements.txt               # Dependencias del proyecto
 .env.example                   # Ejemplo de definición de variables de entorno
 render.yaml                    # IaC
 app/
    __init__.py                  
    main.py                      
    templates/
       dashboard.html           # Dashboard
    api/
       endpoints.py             # Rutas de la API
    services/
        scraper.py              # Lógica de scraping
        redis_db.py             # Cliente y funciones de Redis
```


## Instalación

1. Clonar el repositorio:
`bash
git clone https://github.com/AldoOmarAndres/scrapper-history.git
cd scrapper-history
`

2. Instalar dependencias:
`bash
pip install -r requirements.txt
`

3. Configurar variables de entorno (crear archivo `.env`):
`bash
REDIS_URL=<URL de la base de datos Redis>
URL_TARGET=<URL del sitio web a scrapear>
DELETE_KEY=<Clave para autorizar eliminación de datos>
`

## Endpoints de la API

### Dashboard
- GET / - Dashboard web para visualizar datos

### Health Check
- HEAD / - Verificar que el servicio está activo (responde 200 OK)

### Datos
- GET /today - Obtiene los datos de tasas del día actual desde Redis
  - Retorna los registros almacenados en la clave del día actual
  
- GET /history - Obtiene el historial completo de tasas almacenado en Redis
  - Retorna todos los registros históricos disponibles

- GET /export - Descarga el historial completo como archivo CSV
  - Incluye columnas: plazo, tasa_tomadora, fecha_hora_web, timestamp_scraped, hora
  - Se descarga como 	asas_history.csv

### Administración
- DELETE /history - Elimina todo el historial almacenado
  - Requiere parámetro key con el DELETE_KEY configurado
  - Retorna error 401 si la clave es inválida

## Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| REDIS_URL | URL de conexión a Redis | Sí |
| URL_TARGET | URL del sitio web a scrapear | Sí |
| DELETE_KEY | Clave para autorizar eliminación de datos | Sí |

## Dependencias

- **fastapi** - Framework web moderno y rápido
- **uvicorn** - Servidor ASGI
- **redis** - Cliente para Redis
- **beautifulsoup4** - Parsing y scraping de HTML
- **requests** - Peticiones HTTP
- **pydantic** - Validación de datos
- **apscheduler** - Tareas programadas
- **jinja2** - Motor de templates HTML
- **python-dotenv** - Gestión de variables de entorno

## Flujo de Funcionamiento

1. **Scraping Programado**: El scheduler ejecuta scheduled_scraping_job() cada 2 minutos durante el horario de mercado
2. **Extracción de Datos**: 
un_scraping_logic() realiza el scraping del sitio web objetivo
3. **Validación**: Los datos se validan usando modelos Pydantic
4. **Almacenamiento**: Los datos se guardan en Redis con timestamp
5. **API**: Los endpoints permiten consultar los datos almacenados
6. **Dashboard**: Interfaz web para visualizar los datos

## Datos Capturados

Para cada tasa de interés se registra:
- **plazo**: Plazo en días (máximo 30 días, en pesos)
- **tasa_tomadora**: Tasa de interés (TNA) en porcentaje
- **fecha_hora_web**: Fecha y hora publicada en el sitio web
- **timestamp_scraped**: Timestamp del momento en que se capturó el dato

## Licencia

Este proyecto está disponible bajo licencia abierta.
