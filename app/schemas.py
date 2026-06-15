import datetime
from typing import Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = "todo"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class TaskStatsOut(BaseModel):
    total: int
    by_status: dict[TaskStatus, int]


class TaskListOut(BaseModel):
    items: list[TaskOut]
    total: int
    skip: int
    limit: int


