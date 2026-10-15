import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="DevOps Task API", version="1.0.0")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "devops-postgres"),
        port=5432,
        dbname=os.getenv("DB_NAME", "devopsdb"),
        user=os.getenv("DB_USER", "devops"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


@app.get("/")
def home():
    return {"application": "DevOps Task API", "version": "1.0.0"}


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "UP", "database": "CONNECTED"}
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tasks (title)
                    VALUES (%s)
                    RETURNING id, title, status
                    """,
                    (task.title,),
                )
                row = cur.fetchone()
                return {
                    "id": row[0],
                    "title": row[1],
                    "status": row[2],
                }
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        )


@app.get("/tasks")
def list_tasks():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, status FROM tasks ORDER BY id"
                )
                rows = cur.fetchall()
                return [
                    {"id": r[0], "title": r[1], "status": r[2]}
                    for r in rows
                ]
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        )
