# Company-Grade Task API (FastAPI + SQLite)

## What it is
A small but production-shaped REST API for managing tasks.
- CRUD endpoints
- SQLite persistence
- Auto API docs at `/docs`
- Small “stats” endpoint for dashboards

## Tech
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- Pydantic
- SQLite

## Run
```bash
cd FastAPI-Company-Task-API
python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Open:
- Browser homepage: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs

## Endpoints
- `GET /`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `GET /tasks/stats`
