import os
import uuid
from typing import Optional

import psycopg2
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="SportTrack Training Service")

# ===== DB CONFIG =====
DB_NAME = os.getenv("DB_NAME", "sporttrack")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Postgres123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

MEDIA_DIR = os.getenv("MEDIA_DIR", "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")


# ===== SCHEMAS =====
class CoachSendRequest(BaseModel):
    coach_id: int
    athlete_id: int


class RequestAnswer(BaseModel):
    link_id: int
    action: str  # accept | reject


class TaskCreate(BaseModel):
    coach_id: int
    athlete_id: int
    title: str
    description: Optional[str] = None


class ChatMessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    message: str


# ===== HEALTH =====
@app.get("/api/ping")
def ping():
    return {"status": "training-service ok"}


# ===== COACH <-> ATHLETE LINKS =====
@app.get("/api/coach/athletes")
def coach_athletes(coach_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, u.sport, ta.status
            FROM trainer_athletes ta
            JOIN users u ON u.id = ta.athlete_id
            WHERE ta.coach_id = %s
            ORDER BY u.username
            """,
            (coach_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "username": r[1],
                "email": r[2],
                "sport": r[3],
                "link_status": r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/coach/send-request")
def coach_send_request(data: CoachSendRequest):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # роли проверяем в users таблице (общая БД)
        cur.execute("SELECT role FROM users WHERE id=%s", (data.coach_id,))
        row = cur.fetchone()
        if not row or row[0] != "coach":
            raise HTTPException(400, "Тренер не найден")

        cur.execute("SELECT role FROM users WHERE id=%s", (data.athlete_id,))
        row = cur.fetchone()
        if not row or row[0] != "athlete":
            raise HTTPException(400, "Спортсмен не найден")

        # если уже есть связь
        cur.execute(
            "SELECT status FROM trainer_athletes WHERE coach_id=%s AND athlete_id=%s",
            (data.coach_id, data.athlete_id),
        )
        existing = cur.fetchone()
        if existing:
            status = existing[0]
            if status == "accepted":
                raise HTTPException(400, "Спортсмен уже привязан")
            if str(status).startswith("pending"):
                raise HTTPException(400, "Запрос уже существует")

        # создаём/обновляем pending
        cur.execute(
            """
            INSERT INTO trainer_athletes (coach_id, athlete_id, status)
            VALUES (%s, %s, 'pending_from_coach')
            ON CONFLICT (coach_id, athlete_id)
            DO UPDATE SET status = EXCLUDED.status
            """,
            (data.coach_id, data.athlete_id),
        )
        return {"message": "Запрос отправлен"}
    finally:
        cur.close()
        conn.close()


@app.get("/api/athlete/requests")
def athlete_requests(athlete_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT ta.id, u.id, u.username, u.email, ta.status
            FROM trainer_athletes ta
            JOIN users u ON u.id = ta.coach_id
            WHERE ta.athlete_id = %s AND ta.status = 'pending_from_coach'
            ORDER BY ta.created_at DESC
            """,
            (athlete_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "link_id": r[0],
                "coach_id": r[1],
                "username": r[2],
                "email": r[3],
                "status": r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/athlete/answer-request")
def athlete_answer_request(data: RequestAnswer):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT status FROM trainer_athletes WHERE id=%s", (data.link_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Связь не найдена")

        if data.action not in ("accept", "reject"):
            raise HTTPException(400, "action должен быть accept/reject")

        new_status = "accepted" if data.action == "accept" else "rejected"
        cur.execute(
            "UPDATE trainer_athletes SET status=%s WHERE id=%s",
            (new_status, data.link_id),
        )
        return {"message": f"ok: {new_status}"}
    finally:
        cur.close()
        conn.close()


# ===== TASKS =====
@app.post("/api/tasks")
def create_task(data: TaskCreate):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO tasks (coach_id, athlete_id, title, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (data.coach_id, data.athlete_id, data.title, data.description),
        )
        task_id = cur.fetchone()[0]
        return {"task_id": task_id}
    finally:
        cur.close()
        conn.close()


@app.get("/api/tasks/athlete")
def list_tasks_athlete(athlete_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, coach_id, title, description, created_at
            FROM tasks
            WHERE athlete_id = %s
            ORDER BY created_at DESC
            """,
            (athlete_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "coach_id": r[1],
                "title": r[2],
                "description": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/tasks/media")
def upload_media(task_id: int = Form(...), file: UploadFile = File(...)):
    ext = (file.filename or "file").split(".")[-1]
    new_name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(MEDIA_DIR, new_name)

    with open(path, "wb") as f:
        f.write(file.file.read())

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO task_media (task_id, file_path)
            VALUES (%s, %s)
            RETURNING id
            """,
            (task_id, path),
        )
        media_id = cur.fetchone()[0]
        return {"media_id": media_id, "file_path": path}
    finally:
        cur.close()
        conn.close()


@app.get("/api/tasks/media")
def get_task_media(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, file_path FROM task_media WHERE task_id=%s", (task_id,))
        rows = cur.fetchall()
        return [{"id": r[0], "file_path": r[1]} for r in rows]
    finally:
        cur.close()
        conn.close()


# ===== CHAT =====
@app.post("/api/chat/send")
def chat_send(data: ChatMessageCreate):
    if not data.message.strip():
        raise HTTPException(400, "Пустое сообщение")

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO chat_messages (sender_id, receiver_id, message)
            VALUES (%s, %s, %s)
            RETURNING id, created_at
            """,
            (data.sender_id, data.receiver_id, data.message),
        )
        row = cur.fetchone()
        return {"id": row[0], "created_at": row[1]}
    finally:
        cur.close()
        conn.close()


@app.get("/api/chat/history")
def chat_history(user_id: int, peer_id: int, limit: int = 50):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT sender_id, receiver_id, message, created_at
            FROM chat_messages
            WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (user_id, peer_id, peer_id, user_id, limit),
        )
        rows = cur.fetchall()
        return [
            {
                "sender_id": r[0],
                "receiver_id": r[1],
                "message": r[2],
                "created_at": r[3],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()
