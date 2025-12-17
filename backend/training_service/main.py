import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import psycopg
import uuid
import os

from backend.auth_service.main import DB_NAME

app = FastAPI(title="SportTrack Training Service")


DB_NAME="sporttrack"
DB_USER="postgres"
DB_PASSWORD = "Postgres123"
DB_HOST = "localhost"
DB_PORT = 5432


MEDIA_DIR = "media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)


def get_connection():
    try:
        print("DB_NAME:", repr(DB_NAME))
        print("DB_USER:", repr(DB_USER))
        print("DB_PASSWORD:", repr(DB_PASSWORD))
        print("DB_HOST:", repr(DB_HOST))
        print("DB_PORT:", repr(DB_PORT))

        conn = psycopg.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print("DB CONNECT ERROR (RAW):", repr(e))
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")





class PlanCreate(BaseModel):
    coach_id: int
    title: str
    description: str | None = None
    level: str | None = None


class WorkoutCreate(BaseModel):
    plan_id: int
    day_number: int | None = None
    name: str
    notes: str | None = None


class WorkoutResultCreate(BaseModel):
    athlete_id: int
    workout_id: int
    is_completed: bool = True
    comment: str | None = None


class TaskCreate(BaseModel):
    coach_id: int
    athlete_id: int
    title: str
    description: str | None = None


@app.get("/api/ping")
def ping():
    return {"status": "training-service ok"}


@app.post("/api/plans")
def create_plan(data: PlanCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO training_plans (coach_id, title, description, level)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (data.coach_id, data.title, data.description, data.level)
        )
        plan_id = cur.fetchone()[0]
        return {"plan_id": plan_id}
    finally:
        cur.close()
        conn.close()


@app.get("/api/plans")
def list_plans(coach_id: int | None = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if coach_id:
            cur.execute(
                """SELECT id, coach_id, title, description, level, created_at
                   FROM training_plans WHERE coach_id = %s
                   ORDER BY created_at DESC""",
                (coach_id,)
            )
        else:
            cur.execute(
                """SELECT id, coach_id, title, description, level, created_at
                   FROM training_plans ORDER BY created_at DESC"""
            )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "coach_id": r[1],
                "title": r[2],
                "description": r[3],
                "level": r[4],
                "created_at": r[5]
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/workouts")
def create_workout(data: WorkoutCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM training_plans WHERE id = %s", (data.plan_id,))
        if not cur.fetchone():
            raise HTTPException(400, "План не найден")

        cur.execute(
            """INSERT INTO workouts (plan_id, day_number, name, notes)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (data.plan_id, data.day_number, data.name, data.notes)
        )
        workout_id = cur.fetchone()[0]
        return {"workout_id": workout_id}
    finally:
        cur.close()
        conn.close()


@app.get("/api/workouts")
def list_workouts(plan_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, plan_id, day_number, name, notes
               FROM workouts WHERE plan_id = %s
               ORDER BY day_number NULLS LAST, id""",
            (plan_id,)
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "plan_id": r[1],
                "day_number": r[2],
                "name": r[3],
                "notes": r[4]
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/workouts/result")
def add_workout_result(data: WorkoutResultCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM workouts WHERE id = %s", (data.workout_id,))
        if not cur.fetchone():
            raise HTTPException(400, "Тренировка не найдена")

        cur.execute(
            """INSERT INTO workout_results
               (athlete_id, workout_id, is_completed, comment, completed_at)
               VALUES (%s, %s, %s, %s, NOW())
               RETURNING id""",
            (data.athlete_id, data.workout_id, data.is_completed, data.comment)
        )
        result_id = cur.fetchone()[0]
        return {"result_id": result_id}
    finally:
        cur.close()
        conn.close()


@app.get("/api/athlete/{athlete_id}/progress")
def athlete_progress(athlete_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT
                   COUNT(*) FILTER (WHERE wr.is_completed = TRUE) AS done,
                   COUNT(w.id) AS total
               FROM workouts w
               LEFT JOIN workout_results wr
               ON wr.workout_id = w.id AND wr.athlete_id = %s""",
            (athlete_id,)
        )
        done, total = cur.fetchone()
        percent = (done / total * 100) if total > 0 else 0
        return {"done": done, "total": total, "percent": round(percent, 1)}
    finally:
        cur.close()
        conn.close()


@app.post("/api/tasks")
def create_task(data: TaskCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO tasks (coach_id, athlete_id, title, description)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (data.coach_id, data.athlete_id, data.title, data.description)
        )
        task_id = cur.fetchone()[0]
        return {"task_id": task_id}
    finally:
        cur.close()
        conn.close()


@app.get("/api/tasks/athlete")
def list_tasks_athlete(athlete_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, coach_id, title, description, created_at
               FROM tasks WHERE athlete_id = %s
               ORDER BY created_at DESC""",
            (athlete_id,)
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "coach_id": r[1],
                "title": r[2],
                "description": r[3],
                "created_at": r[4]
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/tasks/media")
def upload_media(task_id: int = Form(...), file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    new_name = f"{uuid.uuid4()}.{ext}"
    path = f"{MEDIA_DIR}/{new_name}"

    with open(path, "wb") as f:
        f.write(file.file.read())

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO task_media (task_id, file_path)
               VALUES (%s, %s) RETURNING id""",
            (task_id, path)
        )
        media_id = cur.fetchone()[0]
        return {"media_id": media_id, "file_path": path}
    finally:
        cur.close()
        conn.close()


@app.get("/api/tasks/media")
def get_task_media(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, file_path FROM task_media WHERE task_id = %s",
            (task_id,)
        )
        rows = cur.fetchall()
        return [{"id": r[0], "file_path": r[1]} for r in rows]
    finally:
        cur.close()
        conn.close()
