# Scrapper History

A FastAPI-based web for financial history with Redis storage for managing and accessing historical scraping data.

## Project Structure

```
app/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI entry point
├── core/
│   └── config.py           # Environment variables (Redis URL, etc.)
├── services/
│   ├── scraper.py          # BeautifulSoup scraping logic
│   └── redis_db.py         # Redis client and functions
├── scheduler/
│   └── tasks.py            # Scheduled scraping tasks
└── api/
    └── endpoints.py        # API routes for historical data
requirements.txt             # Project dependencies
```

## Features

- **FastAPI Backend**: Modern, fast web framework for building APIs
- **BeautifulSoup Scraping**: Pure scraping logic for extracting web data
- **Redis Storage**: Historical data storage with timestamp-based retrieval
- **Scheduled Tasks**: Periodic scraping with configurable intervals
- **RESTful API**: Endpoints for scraping, retrieving history, and managing data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AldoOmarAndres/scrapper-history.git
cd scrapper-history
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Make sure Redis is running:
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install Redis locally
# https://redis.io/docs/getting-started/installation/
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Application health check
- `GET /api/health` - API and Redis health check

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `REDIS_DB` | Redis database number | `0` |
| `REDIS_DECODE_RESPONSES` | Decode responses as strings | `True` |
| `SCRAPER_USER_AGENT` | User agent for web requests | `Mozilla/5.0 (compatible; ScraperBot/1.0)` |
| `SCRAPER_TIMEOUT` | Request timeout in seconds | `30` |
| `SCHEDULER_INTERVAL` | Scraping interval in seconds | `3600` |

## Development

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/
```

## License

MIT License