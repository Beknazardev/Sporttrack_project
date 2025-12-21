import os
import random
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
from pathlib import Path

import psycopg2
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr


# ===================== Paths / Static =====================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="SportTrack")

# Статика НЕ на "/", чтобы /api/* не ломалось
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.get("/")
def root():
    fp = STATIC_DIR / "register.html"
    if not fp.exists():
        return {"detail": "Put register.html into backend/static/register.html"}
    return FileResponse(str(fp))


# Если фронт открываешь с 8000 — CORS не нужен, но оставим (не мешает)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Config =====================
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


# ===================== Helpers =====================
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
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    data = (password + PEPPER + salt).encode("utf-8")
    pwd_hash = hashlib.sha256(data).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, stored_value: str) -> bool:
    try:
        salt, stored_hash = stored_value.split("$", 1)
    except ValueError:
        return False
    data = (plain_password + PEPPER + salt).encode("utf-8")
    check_hash = hashlib.sha256(data).hexdigest()
    return check_hash == stored_hash


def send_email(to_email: str, subject: str, text: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(text)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


# ===================== Schemas =====================
class EmailSendCode(BaseModel):
    email: EmailStr


class EmailCheckCode(BaseModel):
    email: EmailStr
    code: str


class UserRegisterAfterConfirm(BaseModel):
    email: EmailStr
    code: str               # код пользователь ввёл на шаге 2, фронт сохранит и отправит тут
    username: str
    last_name: str | None = None
    password: str
    role: str
    sport: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


# ===================== Routes =====================
@app.get("/api/ping")
def ping():
    return {"ok": True, "service": "sporttrack"}


# Шаг 1: отправить код на почту
@app.post("/api/email/send-code")
def email_send_code(data: EmailSendCode, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        email = data.email
        code = str(random.randint(100000, 999999))

        # закрываем старые pending
        cur.execute(
            "UPDATE pending_users SET is_used=TRUE WHERE email=%s AND is_used=FALSE",
            (email,),
        )

        # создаём новый pending
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


# Шаг 2: проверить код (аккаунт НЕ создаём)
@app.post("/api/email/check-code")
def email_check_code(data: EmailCheckCode):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, is_used
            FROM pending_users
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


# Шаг 3: регистрация (только после подтверждения кода)
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
        # email уже есть?
        cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        # проверяем что код верный и pending ещё не использован
        cur.execute(
            """
            SELECT id, is_used
            FROM pending_users
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

        password_hash = hash_password(user.password)

        cur.execute(
            """
            INSERT INTO users (email, username, last_name, password_hash, role, sport, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,TRUE)
            RETURNING id
            """,
            (user.email, user.username, user.last_name, password_hash, role, user.sport),
        )
        user_id = cur.fetchone()[0]

        # помечаем pending использованным
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

        user_id, username, last_name, password_hash, role, sport, is_active = row
        if not is_active:
            raise HTTPException(status_code=400, detail="Аккаунт выключен")

        if not verify_password(data.password, password_hash):
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
        cur.execute(
            "UPDATE password_reset_codes SET is_used=TRUE WHERE user_id=%s AND is_used=FALSE",
            (user_id,),
        )
        cur.execute(
            "INSERT INTO password_reset_codes (user_id, code) VALUES (%s,%s)",
            (user_id, code),
        )

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
            SELECT id, is_used
            FROM password_reset_codes
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
