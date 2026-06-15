from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Literal


from app.db import SessionLocal, engine
from app.models import Base, Task
from app.schemas import (
    TaskCreate,
    TaskListOut,
    TaskOut,
    TaskStatus,
    TaskStatsOut,
    TaskUpdate,
)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Company-Grade Task API", version="0.1.0")

HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Company-Grade Task API</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; padding: 0; background: #f4f6fb; color: #1f2937; }
    header { background: #2563eb; color: white; padding: 2rem 1.5rem; }
    main { max-width: 960px; margin: 0 auto; padding: 1.5rem; }
    button { background: #2563eb; color: white; border: none; padding: 0.75rem 1rem; border-radius: 0.5rem; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    .card { background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 10px 30px rgba(15,23,42,0.08); margin-bottom: 1rem; }
    .task { border-bottom: 1px solid #e5e7eb; padding: 0.75rem 0; }
    .task:last-child { border-bottom: none; }
    .task-title { font-weight: 700; margin: 0; }
    .task-meta { color: #6b7280; font-size: 0.95rem; margin-top: 0.35rem; }
    pre { background: #f8fafc; padding: 1rem; border-radius: 0.75rem; overflow-x: auto; }
  </style>
</head>
<body>
  <header>
    <h1>Company-Grade Task API</h1>
    <p>Browse tasks and explore the API directly from your browser.</p>
  </header>
  <main>
    <section class="card">
      <h2>Live task dashboard</h2>
      <p>Fetch the current task list from the API and display it here.</p>
      <button id="load-tasks">Load tasks</button>
      <div id="task-list" style="margin-top: 1rem;"></div>
    </section>
    <section class="card">
      <h2>Available endpoints</h2>
      <pre>
GET /         - Homepage
GET /tasks    - List tasks
GET /tasks/{task_id}
POST /tasks   - Create task
PATCH /tasks/{task_id}
DELETE /tasks/{task_id}
GET /tasks/stats
      </pre>
    </section>
  </main>
  <script>
    async function loadTasks() {
      const list = document.getElementById('task-list');
      list.innerHTML = 'Loading...';
      try {
        const response = await fetch('/tasks');
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to fetch tasks');
        if (!data.items.length) {
          list.innerHTML = '<p>No tasks available.</p>';
          return;
        }
        list.innerHTML = data.items.map(task => `
          <div class="task">
            <p class="task-title">${task.title}</p>
            <p class="task-meta">Status: ${task.status} · ID: ${task.id}</p>
            <p>${task.description || 'No description'}</p>
          </div>
        `).join('');
      } catch (error) {
        list.innerHTML = `<p style="color:#b91c1c;">${error.message}</p>`;
      }
    }
    document.getElementById('load-tasks').addEventListener('click', loadTasks);
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def homepage():
    return HTMLResponse(content=HOME_HTML)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=TaskListOut)
def list_tasks(
    status: TaskStatus | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_dir: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
):
    if skip < 0:
        raise HTTPException(status_code=400, detail="skip must be >= 0")
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 1000")

    allowed_sort_fields: dict[str, object] = {
        "id": Task.id,
        "title": Task.title,
        "status": Task.status,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {', '.join(allowed_sort_fields.keys())}",
        )

    order_col = allowed_sort_fields[sort_by]
    if sort_dir == "asc":
        order_expr = order_col.asc()
    else:
        order_expr = order_col.desc()

    base_stmt = select(Task)
    count_stmt = select(Task.id)

    if status is not None:
        base_stmt = base_stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)

    if q:
        pattern = f"%{q}%"
        base_stmt = base_stmt.where((Task.title.ilike(pattern)) | (Task.description.ilike(pattern)))
        count_stmt = count_stmt.where((Task.title.ilike(pattern)) | (Task.description.ilike(pattern)))

    total = db.execute(count_stmt).all()
    total_count = len(total)

    stmt = base_stmt.order_by(order_expr).offset(skip).limit(limit)
    items = db.execute(stmt).scalars().all()

    return TaskListOut(items=items, total=total_count, skip=skip, limit=limit)



@app.get("/tasks/stats", response_model=TaskStatsOut)
def task_stats(db: Session = Depends(get_db)):
    tasks = db.execute(select(Task)).scalars().all()

    by_status: dict[TaskStatus, int] = {"todo": 0, "in_progress": 0, "done": 0}
    for t in tasks:
        if t.status in by_status:
            by_status[t.status] += 1

    return TaskStatsOut(total=len(tasks), by_status=by_status)


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None

