import os
import json
import random
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Literal, Any, Dict, List
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
import uuid
import psycopg2
import psycopg2.extras
from psycopg2.extras import Json

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from fastapi import Form


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="SportTrack")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")




@app.get("/")
def root():
    fp = STATIC_DIR / "register.html"
    if not fp.exists():
        return {"detail": "Put register.html into backend/app/static/register.html"}
    return FileResponse(str(fp))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = os.getenv("DB_NAME", "SPORTTRACKKK")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Postgres123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "sporttrack.project@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "cfng hixo xptz kmfm")  # лучше в .env

PEPPER = os.getenv("PEPPER", "super_secret_pepper_123")


def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True

        psycopg2.extras.register_default_json(conn)
        psycopg2.extras.register_default_jsonb(conn)

        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    data = (password + PEPPER + salt).encode("utf-8")
    pwd_hash = hashlib.sha256(data).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain: str, stored: str) -> bool:
    try:
        salt, stored_hash = stored.split("$", 1)
    except ValueError:
        return False
    data = (plain + PEPPER + salt).encode("utf-8")
    return hashlib.sha256(data).hexdigest() == stored_hash


def send_email(to_email: str, subject: str, text: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(text)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def assert_admin(cur, admin_id: int):
    cur.execute("SELECT role FROM users WHERE id=%s", (admin_id,))
    row = cur.fetchone()
    if not row or (row[0] or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Только администратор")


def assert_coach(cur, coach_id: int):
    cur.execute("SELECT role FROM users WHERE id=%s", (coach_id,))
    row = cur.fetchone()
    if not row or (row[0] or "").lower() != "coach":
        raise HTTPException(status_code=403, detail="Только тренер")


def assert_athlete(cur, athlete_id: int):
    cur.execute("SELECT role FROM users WHERE id=%s", (athlete_id,))
    row = cur.fetchone()
    if not row or (row[0] or "").lower() != "athlete":
        raise HTTPException(status_code=403, detail="Только спортсмен")


def log_admin_action(
    cur,
    admin_id: int,
    action: str,
    title: str,
    message: str,
    target_user_id: Optional[int] = None,
):
    cur.execute(
        """
        INSERT INTO admin_activity (admin_id, action, target_user_id, title, message)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (admin_id, action, target_user_id, title, message),
    )


def create_notification(
    cur,
    user_id: int,
    title: str,
    message: str,
    kind: str = "info",
    meta: Optional[Dict[str, Any]] = None,
):
    meta = meta or {}
    cur.execute(
        """
        INSERT INTO notifications (user_id, title, message, kind, meta)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (user_id, title, message, kind, Json(meta)),
    )

def save_upload(file: UploadFile) -> Optional[str]:
    if not file:
        return None
    ext = Path(file.filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    out_path = UPLOADS_DIR / safe_name
    with out_path.open("wb") as f:
        f.write(file.file.read())
    return f"/static/uploads/{safe_name}"

def save_upload(file: UploadFile) -> Optional[str]:
    if not file:
        return None
    ext = Path(file.filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    out_path = UPLOADS_DIR / safe_name
    with out_path.open("wb") as f:
        f.write(file.file.read())
    return f"/uploads/{safe_name}"



class EmailSendCode(BaseModel):
    email: EmailStr


class EmailCheckCode(BaseModel):
    email: EmailStr
    code: str


class UserRegisterAfterConfirm(BaseModel):
    email: EmailStr
    code: str
    username: str
    last_name: Optional[str] = None
    password: str
    role: str
    sport: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class CoachRequestCreate(BaseModel):
    athlete_id: int
    coach_id: int


class CoachAthleteRemove(BaseModel):
    coach_id: int
    athlete_id: int


class AthleteRequestRespond(BaseModel):
    athlete_id: int
    coach_id: int
    decision: Literal["accepted", "declined"]

class TaskCreate(BaseModel):
    coach_id: int
    athlete_id: int
    title: str
    description: str
    due_date: Optional[str] = None  # "YYYY-MM-DD"
    media_url: Optional[str] = None

class PlanCreate(BaseModel):
    coach_id: int
    athlete_id: int
    name: str
    body: str
    media_url: Optional[str] = None

class TaskDone(BaseModel):
    athlete_id: int

class TaskRate(BaseModel):
    coach_id: int
    rating: int

@app.get("/api/ping")
def ping():
    return {"ok": True, "service": "sporttrack"}


@app.post("/api/email/send-code")
def email_send_code(data: EmailSendCode, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        email = data.email
        code = str(random.randint(100000, 999999))

        cur.execute(
            "UPDATE pending_users SET is_used=TRUE WHERE email=%s AND is_used=FALSE",
            (email,),
        )
        cur.execute(
            """
            INSERT INTO pending_users (email, username, last_name, password_hash, role, sport, code, is_used)
            VALUES (%s, '', NULL, '', 'athlete', NULL, %s, FALSE)
            RETURNING id
            """,
            (email, code),
        )
        pending_id = cur.fetchone()[0]
        bg.add_task(send_email, email, "SportTrack: код подтверждения", f"Ваш код: {code}")
        return {"pending_id": pending_id, "message": "Код отправлен"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/email/check-code")
def email_check_code(data: EmailCheckCode):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, is_used FROM pending_users
            WHERE email=%s AND code=%s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (data.email, data.code),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Неверный код")
        pending_id, is_used = row
        if is_used:
            raise HTTPException(status_code=400, detail="Код уже использован")
        return {"ok": True, "pending_id": pending_id}
    finally:
        cur.close()
        conn.close()


@app.post("/api/register")
def register(user: UserRegisterAfterConfirm):
    role = (user.role or "").strip().lower()
    if role not in ("admin", "coach", "athlete"):
        raise HTTPException(status_code=400, detail="Неверная роль")
    if len(user.password) < 4:
        raise HTTPException(status_code=400, detail="Пароль минимум 4 символа")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        cur.execute(
            """
            SELECT id, is_used FROM pending_users
            WHERE email=%s AND code=%s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user.email, user.code),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Неверный код")
        pending_id, is_used = row
        if is_used:
            raise HTTPException(status_code=400, detail="Код уже использован")

        password_hash_ = hash_password(user.password)

        cur.execute(
            """
            INSERT INTO users (email, username, last_name, password_hash, role, sport, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,TRUE)
            RETURNING id
            """,
            (user.email, user.username, user.last_name, password_hash_, role, user.sport),
        )
        user_id = cur.fetchone()[0]
        cur.execute("UPDATE pending_users SET is_used=TRUE WHERE id=%s", (pending_id,))
        return {"message": "Аккаунт создан", "id": user_id, "email": user.email, "username": user.username, "role": role}
    finally:
        cur.close()
        conn.close()


@app.post("/api/login")
def login(data: UserLogin):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, username, last_name, password_hash, role, sport, is_active
            FROM users
            WHERE email=%s
            """,
            (data.email,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Неверный email или пароль")

        user_id, username, last_name, password_hash_, role, sport, is_active = row
        if not is_active:
            raise HTTPException(status_code=400, detail="Аккаунт выключен")
        if not verify_password(data.password, password_hash_):
            raise HTTPException(status_code=400, detail="Неверный email или пароль")

        return {"id": user_id, "email": data.email, "username": username, "last_name": last_name, "role": role, "sport": sport}
    finally:
        cur.close()
        conn.close()


@app.post("/api/password/reset-request")
def reset_request(data: PasswordResetRequest, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email=%s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Пользователь не найден")

        user_id = row[0]
        code = str(random.randint(100000, 999999))
        cur.execute("UPDATE password_reset_codes SET is_used=TRUE WHERE user_id=%s AND is_used=FALSE", (user_id,))
        cur.execute("INSERT INTO password_reset_codes (user_id, code) VALUES (%s,%s)", (user_id, code))
        bg.add_task(send_email, data.email, "SportTrack: сброс пароля", f"Код для сброса: {code}")
        return {"message": "Код отправлен"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/password/reset-confirm")
def reset_confirm(data: PasswordResetConfirm):
    if len(data.new_password) < 4:
        raise HTTPException(status_code=400, detail="Пароль минимум 4 символа")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email=%s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        user_id = row[0]

        cur.execute(
            """
            SELECT id, is_used FROM password_reset_codes
            WHERE user_id=%s AND code=%s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, data.code),
        )
        code_row = cur.fetchone()
        if not code_row:
            raise HTTPException(status_code=400, detail="Неверный код")
        code_id, is_used = code_row
        if is_used:
            raise HTTPException(status_code=400, detail="Код уже использован")

        cur.execute("UPDATE password_reset_codes SET is_used=TRUE WHERE id=%s", (code_id,))
        new_hash = hash_password(data.new_password)
        cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, user_id))
        return {"message": "Пароль обновлён"}
    finally:
        cur.close()
        conn.close()


@app.get("/api/notifications")
def get_notifications(user_id: int = Query(...), limit: int = 50, unread_only: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if unread_only:
            cur.execute(
                """
                SELECT id, title, message, created_at, is_read, kind, meta
                FROM notifications
                WHERE user_id=%s AND is_read=FALSE
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
        else:
            cur.execute(
                """
                SELECT id, title, message, created_at, is_read, kind, meta
                FROM notifications
                WHERE user_id=%s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )

        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "message": r[2],
                "created_at": r[3],
                "is_read": r[4],
                "kind": r[5],
                "meta": r[6],  # dict (если jsonb зарегистрирован) или строка
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    user_id: int = Query(...),
    body: Optional[Dict[str, Any]] = Body(default=None),
):

    if (not user_id) and body and "user_id" in body:
        user_id = int(body["user_id"])

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM notifications WHERE id=%s", (notif_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Уведомление не найдено")
        if row[0] != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")

        cur.execute("UPDATE notifications SET is_read=TRUE WHERE id=%s", (notif_id,))
        return {"ok": True}
    finally:
        cur.close()
        conn.close()


@app.get("/api/activity")
def user_activity_from_notifications(user_id: int = Query(...), limit: int = 6):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT title, message, created_at
            FROM notifications
            WHERE user_id=%s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
        return [{"title": r[0], "message": r[1], "created_at": r[2]} for r in rows]
    finally:
        cur.close()
        conn.close()


@app.get("/api/admin/stats")
def admin_stats():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users WHERE role='coach'")
        total_coaches = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users WHERE role='athlete'")
        total_athletes = cur.fetchone()[0] or 0
        return {"total_users": total_users, "total_coaches": total_coaches, "total_athletes": total_athletes}
    finally:
        cur.close()
        conn.close()


@app.get("/api/admin/users")
def admin_users(admin_id: int = Query(...), role: Optional[str] = None, q: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_admin(cur, admin_id)
        log_admin_action(cur, admin_id, "view_users", "Просмотр пользователей", f"role={role or 'all'}, q={q or '-'}")

        sql = """
        SELECT id, username, last_name, email, role, sport, is_active, created_at
        FROM users
        WHERE 1=1
        """
        params: List[Any] = []

        if role:
            sql += " AND role=%s"
            params.append(role.strip().lower())

        if q:
            qq = f"%{q.lower()}%"
            sql += " AND (LOWER(COALESCE(username,'')) LIKE %s OR LOWER(email) LIKE %s)"
            params.extend([qq, qq])

        sql += " ORDER BY id DESC"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        return [
            {"id": r[0], "username": r[1], "last_name": r[2], "email": r[3], "role": r[4], "sport": r[5], "is_active": r[6], "created_at": r[7]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.patch("/api/admin/users/{user_id}")
def admin_update_user(user_id: int, payload: AdminUserUpdate, admin_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_admin(cur, admin_id)

        cur.execute("SELECT email, role, is_active FROM users WHERE id=%s", (user_id,))
        target = cur.fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        email, old_role, old_active = target

        updates = []
        params = []
        changes = []

        if payload.role is not None:
            new_role = payload.role.strip().lower()
            if new_role not in ("admin", "coach", "athlete"):
                raise HTTPException(status_code=400, detail="Неверная роль")
            if new_role != (old_role or "").lower():
                updates.append("role=%s")
                params.append(new_role)
                changes.append(f"роль {old_role} → {new_role}")

        if payload.is_active is not None and payload.is_active != old_active:
            updates.append("is_active=%s")
            params.append(payload.is_active)
            changes.append(f"активность {old_active} → {payload.is_active}")

        if not updates:
            return {"ok": True, "message": "Без изменений"}

        params.append(user_id)
        cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=%s", tuple(params))

        create_notification(
            cur,
            user_id=user_id,
            title="Изменения от администратора",
            message=", ".join(changes),
            kind="admin_update",
            meta={"admin_id": admin_id, "changes": changes},
        )

        log_admin_action(
            cur,
            admin_id=admin_id,
            action="update_user",
            title="Изменён пользователь",
            message=f"{email}: {', '.join(changes)}",
            target_user_id=user_id,
        )

        return {"ok": True, "changes": changes}
    finally:
        cur.close()
        conn.close()


@app.get("/api/admin/activity")
def admin_activity(admin_id: int, limit: int = 10):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_admin(cur, admin_id)
        cur.execute(
            """
            SELECT title, message, created_at
            FROM admin_activity
            WHERE admin_id=%s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (admin_id, limit),
        )
        rows = cur.fetchall()
        return [{"title": r[0], "message": r[1], "created_at": r[2]} for r in rows]
    finally:
        cur.close()
        conn.close()


@app.get("/api/admin/activity-stats")
def admin_activity_stats(admin_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_admin(cur, admin_id)

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users WHERE role='athlete'")
        athletes = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users WHERE role='coach'")
        coaches = cur.fetchone()[0] or 0

        trainings = 0
        try:
            cur.execute("SELECT COUNT(*) FROM trainings")
            trainings = cur.fetchone()[0] or 0
        except Exception:
            trainings = 0

        cur.execute(
            """
            SELECT TO_CHAR(created_at, 'YYYY-MM') AS month, COUNT(*)
            FROM users
            GROUP BY month
            ORDER BY month
            """
        )
        registrations = [{"month": r[0], "count": r[1]} for r in cur.fetchall()]

        cur.execute(
            """
            SELECT DATE(created_at) AS day, COUNT(*)
            FROM admin_activity
            GROUP BY day
            ORDER BY day
            """
        )
        activity = [{"date": str(r[0]), "count": r[1]} for r in cur.fetchall()]

        return {
            "cards": {"total_users": total_users, "athletes": athletes, "coaches": coaches, "trainings": trainings},
            "registrations": registrations,
            "activity": activity,
        }
    finally:
        cur.close()
        conn.close()


@app.get("/api/users/search")
def users_search(q: str = Query(...), coach_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)

        q_str = (q or "").strip()
        params: List[Any] = [coach_id]

        sql = """
        SELECT u.id, u.username, u.last_name, u.email, u.role, u.sport,
               COALESCE(l.status, 'none') AS link_status
        FROM users u
        LEFT JOIN coach_athlete_links l
          ON l.coach_id = %s AND l.athlete_id = u.id
        WHERE 1=1
        """

        if q_str.isdigit():
            sql += " AND u.id = %s"
            params.append(int(q_str))
        else:
            like = f"%{q_str.lower()}%"
            sql += " AND (LOWER(u.email) LIKE %s OR LOWER(COALESCE(u.username,'')) LIKE %s OR LOWER(COALESCE(u.last_name,'')) LIKE %s)"
            params.extend([like, like, like])

        sql += " ORDER BY u.id DESC LIMIT 50"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        return [
            {"id": r[0], "username": r[1], "last_name": r[2], "email": r[3], "role": r[4], "sport": r[5], "link_status": r[6]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/coach/request")
def coach_request(payload: CoachRequestCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, payload.coach_id)
        assert_athlete(cur, payload.athlete_id)

        cur.execute(
            """
            INSERT INTO coach_athlete_links (coach_id, athlete_id, status)
            VALUES (%s,%s,'pending_from_coach')
            ON CONFLICT (coach_id, athlete_id)
            DO UPDATE SET status='pending_from_coach', updated_at=NOW()
            RETURNING id
            """,
            (payload.coach_id, payload.athlete_id),
        )
        link_id = cur.fetchone()[0]

        cur.execute("SELECT username, last_name FROM users WHERE id=%s", (payload.coach_id,))
        c = cur.fetchone()
        coach_name = (f"{c[0] or ''} {c[1] or ''}").strip() if c else f"Coach #{payload.coach_id}"

        create_notification(
            cur,
            user_id=payload.athlete_id,
            title="Запрос от тренера",
            message=f"Тренер {coach_name} хочет добавить вас.",
            kind="coach_request",
            meta={"coach_id": payload.coach_id, "athlete_id": payload.athlete_id, "link_id": link_id},
        )

        return {"ok": True, "link_id": link_id, "status": "pending_from_coach"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/athlete/coach-request/respond")
def athlete_respond(payload: AthleteRequestRespond):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, payload.athlete_id)
        assert_coach(cur, payload.coach_id)

        cur.execute(
            "SELECT id, status FROM coach_athlete_links WHERE coach_id=%s AND athlete_id=%s",
            (payload.coach_id, payload.athlete_id),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Запрос не найден")

        link_id, _old_status = row
        new_status = payload.decision

        cur.execute(
            "UPDATE coach_athlete_links SET status=%s, updated_at=NOW() WHERE id=%s",
            (new_status, link_id),
        )

        cur.execute("SELECT username, last_name FROM users WHERE id=%s", (payload.athlete_id,))
        a = cur.fetchone()
        athlete_name = (f"{a[0] or ''} {a[1] or ''}").strip() if a else f"Athlete #{payload.athlete_id}"

        if new_status == "accepted":
            title, msg = "Запрос принят", f"{athlete_name} принял ваш запрос."
        else:
            title, msg = "Запрос отклонён", f"{athlete_name} отклонил ваш запрос."

        create_notification(
            cur,
            user_id=payload.coach_id,
            title=title,
            message=msg,
            kind="coach_request_result",
            meta={"coach_id": payload.coach_id, "athlete_id": payload.athlete_id, "link_id": link_id, "status": new_status},
        )

        create_notification(
            cur,
            user_id=payload.athlete_id,
            title="Ответ отправлен",
            message=f"Вы: {new_status}",
            kind="info",
            meta={"coach_id": payload.coach_id, "link_id": link_id},
        )

        return {"ok": True, "status": new_status}
    finally:
        cur.close()
        conn.close()


@app.get("/api/coach/athletes")
def coach_athletes(coach_id: int = Query(...), status: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)

        sql = """
        SELECT u.id, u.username, u.last_name, u.email, u.role, u.sport, l.status
        FROM coach_athlete_links l
        JOIN users u ON u.id = l.athlete_id
        WHERE l.coach_id=%s
        """
        params: List[Any] = [coach_id]

        if status:
            sql += " AND l.status=%s"
            params.append(status.strip().lower())

        sql += " ORDER BY l.updated_at DESC"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

        return [
            {"id": r[0], "username": r[1], "last_name": r[2], "email": r[3], "role": r[4], "sport": r[5], "link_status": r[6]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/coach/athletes/remove")
def coach_remove_athlete(payload: CoachAthleteRemove):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, payload.coach_id)

        cur.execute(
            "DELETE FROM coach_athlete_links WHERE coach_id=%s AND athlete_id=%s",
            (payload.coach_id, payload.athlete_id),
        )

        create_notification(
            cur,
            user_id=payload.athlete_id,
            title="Связь с тренером удалена",
            message="Тренер удалил вас из своего списка.",
            kind="coach_unlink",
            meta={"coach_id": payload.coach_id, "athlete_id": payload.athlete_id},
        )

        return {"ok": True}
    finally:
        cur.close()
        conn.close()

@app.post("/api/coach/tasks")
def coach_create_task(payload: TaskCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, payload.coach_id)
        assert_athlete(cur, payload.athlete_id)

        cur.execute(
            """
            INSERT INTO tasks (coach_id, athlete_id, title, description, due_date, status, media_url)
            VALUES (%s,%s,%s,%s,%s,'sent',%s)
            RETURNING id, created_at
            """,
            (payload.coach_id, payload.athlete_id, payload.title, payload.description, payload.due_date, payload.media_url),
        )
        task_id, created_at = cur.fetchone()

        create_notification(
            cur,
            user_id=payload.athlete_id,
            title="Новое задание",
            message=payload.title,
            kind="task",
            meta={"task_id": task_id, "coach_id": payload.coach_id, "media_url": payload.media_url, "due_date": payload.due_date},
        )

        return {"ok": True, "task_id": task_id, "created_at": created_at}
    finally:
        cur.close()
        conn.close()


@app.get("/api/coach/tasks")
def coach_tasks(coach_id: int = Query(...), athlete_id: Optional[int] = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)
        sql = """
            SELECT id, coach_id, athlete_id, title, description, due_date, status, media_url, created_at
            FROM tasks
            WHERE coach_id=%s
        """
        params: List[Any] = [coach_id]
        if athlete_id:
            sql += " AND athlete_id=%s"
            params.append(athlete_id)
        sql += " ORDER BY created_at DESC"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        return [
            {
                "id": r[0], "coach_id": r[1], "athlete_id": r[2],
                "title": r[3], "description": r[4], "due_date": r[5],
                "status": r[6], "media_url": r[7], "created_at": r[8],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/api/athlete/tasks")
def athlete_tasks(athlete_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, athlete_id)
        cur.execute(
            """
            SELECT id, coach_id, athlete_id, title, description, due_date, status, media_url, created_at
            FROM tasks
            WHERE athlete_id=%s
            ORDER BY created_at DESC
            """,
            (athlete_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0], "coach_id": r[1], "athlete_id": r[2],
                "title": r[3], "description": r[4], "due_date": r[5],
                "status": r[6], "media_url": r[7], "created_at": r[8],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

@app.post("/api/coach/plans")
def coach_create_plan(payload: PlanCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, payload.coach_id)
        assert_athlete(cur, payload.athlete_id)

        cur.execute(
            """
            INSERT INTO plans (coach_id, athlete_id, name, body, media_url)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id, created_at
            """,
            (payload.coach_id, payload.athlete_id, payload.name, payload.body, payload.media_url),
        )
        plan_id, created_at = cur.fetchone()

        create_notification(
            cur,
            user_id=payload.athlete_id,
            title="Новый план тренировок",
            message=payload.name,
            kind="plan",
            meta={"plan_id": plan_id, "coach_id": payload.coach_id, "media_url": payload.media_url},
        )

        return {"ok": True, "plan_id": plan_id, "created_at": created_at}
    finally:
        cur.close()
        conn.close()


@app.get("/api/coach/plans")
def coach_plans(coach_id: int = Query(...), athlete_id: Optional[int] = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)
        sql = """
            SELECT id, coach_id, athlete_id, name, body, media_url, created_at
            FROM plans
            WHERE coach_id=%s
        """
        params: List[Any] = [coach_id]
        if athlete_id:
            sql += " AND athlete_id=%s"
            params.append(athlete_id)
        sql += " ORDER BY created_at DESC"

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        return [
            {"id": r[0], "coach_id": r[1], "athlete_id": r[2], "name": r[3], "body": r[4], "media_url": r[5], "created_at": r[6]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.get("/api/athlete/plans")
def athlete_plans(athlete_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, athlete_id)
        cur.execute(
            """
            SELECT id, coach_id, athlete_id, name, body, media_url, created_at
            FROM plans
            WHERE athlete_id=%s
            ORDER BY created_at DESC
            """,
            (athlete_id,),
        )
        rows = cur.fetchall()
        return [
            {"id": r[0], "coach_id": r[1], "athlete_id": r[2], "name": r[3], "body": r[4], "media_url": r[5], "created_at": r[6]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


@app.post("/api/upload")
def upload_file(file: UploadFile = File(...)):
    allowed = {"image/png", "image/jpeg", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Только картинки (png/jpg/webp/gif)")

    ext = Path(file.filename).suffix.lower() or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOADS_DIR / name

    with dest.open("wb") as f:
        f.write(file.file.read())

    return {"ok": True, "url": f"/uploads/{name}"}

@app.get("/api/users/{user_id}")
def get_user_profile(user_id: int):

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, username, last_name, email, role, sport
            FROM users
            WHERE id=%s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {
            "id": row[0],
            "username": row[1],
            "last_name": row[2],
            "email": row[3],
            "role": row[4],
            "sport": row[5],
        }
    finally:
        cur.close()
        conn.close()


@app.get("/api/athlete/summary")
def athlete_summary(athlete_id: int = Query(...)):

    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, athlete_id)


        cur.execute("SELECT COUNT(*) FROM plans WHERE athlete_id=%s", (athlete_id,))
        plans_cnt = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE athlete_id=%s
              AND COALESCE(status,'sent') NOT IN ('done', 'rated')
        """, (athlete_id,))
        active_tasks_cnt = cur.fetchone()[0] or 0

        workouts_cnt = 0
        try:
            cur.execute("SELECT COUNT(*) FROM trainings WHERE athlete_id=%s", (athlete_id,))
            workouts_cnt = cur.fetchone()[0] or 0
        except Exception:
            workouts_cnt = 0

        return {
            "plans": plans_cnt,
            "workouts": workouts_cnt,
            "active_tasks": active_tasks_cnt,
        }
    finally:
        cur.close()
        conn.close()

@app.post("/api/athlete/tasks/{task_id}/submit")
def athlete_submit_task(
    task_id: int,
    athlete_id: int = Form(...),
    text: str = Form(""),
    file: UploadFile | None = File(default=None),
):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, athlete_id)

        cur.execute("SELECT id, coach_id, athlete_id, status FROM tasks WHERE id=%s", (task_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задание не найдено")

        _id, coach_id, a_id, status = row
        if a_id != athlete_id:
            raise HTTPException(status_code=403, detail="Нет доступа")

        media_url = None
        if file is not None:
            up = save_upload(file)  # у тебя уже есть
            media_url = up

        cur.execute("""
          INSERT INTO task_submissions (task_id, athlete_id, coach_id, text, media_url)
          VALUES (%s,%s,%s,%s,%s)
          RETURNING id, created_at
        """, (task_id, athlete_id, coach_id, text.strip() or None, media_url))
        sub_id, created_at = cur.fetchone()

        cur.execute("UPDATE tasks SET status='submitted' WHERE id=%s", (task_id,))

        create_notification(
            cur,
            user_id=coach_id,
            title="Задание выполнено",
            message=f"Спортсмен #{athlete_id} отправил выполнение: {text[:80] if text else '(фото)'}",
            kind="task_submitted",
            meta={"task_id": task_id, "submission_id": sub_id, "athlete_id": athlete_id, "media_url": media_url},
        )

        create_notification(
            cur,
            user_id=athlete_id,
            title="Отправлено тренеру",
            message=f"Задание #{task_id} отправлено",
            kind="task_submitted_ack",
            meta={"task_id": task_id, "submission_id": sub_id},
        )

        return {"ok": True, "submission_id": sub_id, "created_at": created_at, "media_url": media_url}
    finally:
        cur.close()
        conn.close()

@app.get("/api/athlete/tasks")
def athlete_tasks(athlete_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_athlete(cur, athlete_id)

        cur.execute("""
            SELECT
                t.id, t.coach_id, t.athlete_id, t.title, t.description, t.due_date,
                t.status, t.media_url, t.created_at,
                s.text, s.media_url, s.created_at
            FROM tasks t
            LEFT JOIN LATERAL (
                SELECT text, media_url, created_at
                FROM task_submissions
                WHERE task_id = t.id AND athlete_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            ) s ON TRUE
            WHERE t.athlete_id = %s
            ORDER BY t.created_at DESC
        """, (athlete_id, athlete_id))

        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0],
                "coach_id": r[1],
                "athlete_id": r[2],
                "title": r[3],
                "description": r[4],
                "due_date": r[5],
                "status": r[6],
                "media_url": r[7],
                "created_at": r[8],
                "submission": None if (r[9] is None and r[10] is None and r[11] is None) else {
                    "text": r[9],
                    "media_url": r[10],
                    "created_at": r[11],
                }
            })
        return out
    finally:
        cur.close()
        conn.close()

class TaskRate(BaseModel):
    coach_id: int
    rating: int  # 0..10

@app.post("/api/coach/tasks/{task_id}/rate")
def coach_rate_task(task_id: int, payload: TaskRate):
    if payload.rating < 0 or payload.rating > 10:
        raise HTTPException(status_code=400, detail="rating должен быть 0..10")

    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, payload.coach_id)

        cur.execute(
            "SELECT id, coach_id, athlete_id, status FROM tasks WHERE id=%s",
            (task_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Задание не найдено")

        _id, coach_id, athlete_id, status = row
        if coach_id != payload.coach_id:
            raise HTTPException(status_code=403, detail="Нет доступа")

        cur.execute(
            "SELECT id FROM task_submissions WHERE task_id=%s ORDER BY created_at DESC LIMIT 1",
            (task_id,)
        )
        sub = cur.fetchone()
        if not sub:
            raise HTTPException(status_code=400, detail="Нет отправки от спортсмена")

        cur.execute(
            "UPDATE tasks SET rating=%s, status='rated', rated_at=NOW() WHERE id=%s",
            (payload.rating, task_id)
        )

        create_notification(
            cur,
            user_id=athlete_id,
            title="Задание оценено",
            message=f"Тренер поставил оценку {payload.rating}/10 за задание #{task_id}",
            kind="task_rated",
            meta={"task_id": task_id, "rating": payload.rating, "coach_id": payload.coach_id},
        )

        create_notification(
            cur,
            user_id=payload.coach_id,
            title="Оценка сохранена",
            message=f"Вы поставили {payload.rating}/10 за задание #{task_id}",
            kind="task_rated_ack",
            meta={"task_id": task_id, "rating": payload.rating, "athlete_id": athlete_id},
        )

        return {"ok": True, "task_id": task_id, "rating": payload.rating}
    finally:
        cur.close()
        conn.close()

@app.get("/api/coach/tasks")
def coach_tasks(coach_id: int = Query(...), athlete_id: Optional[int] = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)

        params: List[Any] = [coach_id]
        filt = ""
        if athlete_id:
            filt = " AND t.athlete_id=%s"
            params.append(athlete_id)

        cur.execute(f"""
            SELECT
              t.id, t.coach_id, t.athlete_id, t.title, t.description, t.due_date,
              t.status, t.media_url, t.created_at,
              t.rating, t.rated_at,
              s.id AS sub_id, s.text AS sub_text, s.media_url AS sub_media, s.created_at AS sub_created
            FROM tasks t
            LEFT JOIN LATERAL (
              SELECT id, text, media_url, created_at
              FROM task_submissions
              WHERE task_id = t.id
              ORDER BY created_at DESC
              LIMIT 1
            ) s ON TRUE
            WHERE t.coach_id=%s {filt}
            ORDER BY t.created_at DESC
        """, tuple(params))

        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0],
                "coach_id": r[1],
                "athlete_id": r[2],
                "title": r[3],
                "description": r[4],
                "due_date": r[5],
                "status": r[6],
                "media_url": r[7],
                "created_at": r[8],
                "rating": r[9],
                "rated_at": r[10],
                "submission": (None if r[11] is None else {
                    "id": r[11],
                    "text": r[12],
                    "media_url": r[13],
                    "created_at": r[14],
                })
            })
        return out
    finally:
        cur.close()
        conn.close()

@app.get("/api/coach/task-submissions/{submission_id}")
def coach_get_submission(submission_id: int, coach_id: int = Query(...)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        assert_coach(cur, coach_id)

        cur.execute("""
            SELECT s.id, s.task_id, s.athlete_id, s.coach_id, s.text, s.media_url, s.created_at
            FROM task_submissions s
            WHERE s.id=%s AND s.coach_id=%s
        """, (submission_id, coach_id))
        r = cur.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Submission not found")

        return {
            "id": r[0],
            "task_id": r[1],
            "athlete_id": r[2],
            "coach_id": r[3],
            "text": r[4],
            "media_url": r[5],
            "created_at": r[6],
        }
    finally:
        cur.close()
        conn.close()


@app.post("/api/profile/update")
def profile_update(
    user_id: int = Form(...),
    username: str = Form(...),
    last_name: str | None = Form(default=None),
    sport: str | None = Form(default=None),
    avatar: UploadFile | None = File(default=None),
):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, role FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        avatar_url = None
        if avatar is not None:
            avatar_url = save_upload(avatar)

        cur.execute(
            """
            UPDATE users
            SET username=%s,
                last_name=%s,
                sport=%s,
                avatar_url = COALESCE(%s, avatar_url)
            WHERE id=%s
            RETURNING id, username, last_name, email, role, sport, avatar_url
            """,
            (
                username.strip(),
                (last_name or None),
                (sport or None),
                avatar_url,
                user_id,
            )
        )
        u = cur.fetchone()

        return {
            "ok": True,
            "id": u[0],
            "username": u[1],
            "last_name": u[2],
            "email": u[3],
            "role": u[4],
            "sport": u[5],
            "avatar_url": u[6],
        }
    finally:
        cur.close()
        conn.close()
