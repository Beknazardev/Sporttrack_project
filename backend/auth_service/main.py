import os
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import psycopg
import random
import smtplib
from email.message import EmailMessage
import hashlib
import secrets

app = FastAPI(title="SportTrack Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "sporttrack"
DB_USER = "postgres"
DB_PASSWORD = "Postgres123"
DB_HOST = "localhost"
DB_PORT = 5432

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "sporttrack.project@gmail.com"
SMTP_PASSWORD = "cfng hixo xptz kmfm"

PEPPER = "super_secret_pepper_123"


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


def get_connection():
    try:
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
        print("DB CONNECT ERROR:", e)
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str


class EmailConfirmRequest(BaseModel):
    email: EmailStr


class EmailConfirmCheck(BaseModel):
    email: EmailStr
    code: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class LogoutRequest(BaseModel):
    email: EmailStr


class AccountDelete(BaseModel):
    email: EmailStr


def send_reset_email(to_email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Код для сброса пароля"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(f"Ваш код для сброса пароля: {code}")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def send_confirm_email(to_email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Код подтверждения email"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(f"Ваш код: {code}")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


@app.get("/api/ping")
def ping():
    return {"status": "auth-service ok"}


@app.get("/api/db-check")
def db_check():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1")
        row = cur.fetchone()
        return {"db_ok": True, "result": row[0]}
    finally:
        cur.close()
        conn.close()


@app.post("/api/register")
def register(user: UserRegister, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        if len(user.password) < 4:
            raise HTTPException(status_code=400, detail="Пароль слишком короткий")

        password_hash = hash_password(user.password)
        code = str(random.randint(100000, 999999))

        cur.execute(
            """
            UPDATE pending_users
            SET is_used = TRUE
            WHERE email = %s AND is_used = FALSE
            """,
            (user.email,),
        )

        cur.execute(
            """
            INSERT INTO pending_users (email, username, password_hash, role, code)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (user.email, user.username, password_hash, user.role, code),
        )
        pending_id = cur.fetchone()[0]

        bg.add_task(send_confirm_email, user.email, code)

        return {
            "pending_id": pending_id,
            "message": "Регистрация начата. Код отправлен на email. Введите код для завершения регистрации."
        }
    except HTTPException:
        raise
    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=f"REGISTER ERROR: {e}")
    finally:
        cur.close()
        conn.close()


@app.post("/api/email/send-code")
def email_send_code(data: EmailConfirmRequest, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id FROM pending_users WHERE email = %s AND is_used = FALSE",
            (data.email,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=400,
                detail="Незавершённая регистрация не найдена. Попробуйте зарегистрироваться заново.",
            )

        pending_id = row[0]
        code = str(random.randint(100000, 999999))

        cur.execute(
            "UPDATE pending_users SET code = %s WHERE id = %s",
            (code, pending_id),
        )

        bg.add_task(send_confirm_email, data.email, code)

        return {"message": "Код повторно отправлен на email"}
    except HTTPException:
        raise
    except Exception as e:
        print("EMAIL SEND CODE ERROR:", e)
        raise HTTPException(status_code=500, detail="Ошибка отправки кода")
    finally:
        cur.close()
        conn.close()


@app.post("/api/email/confirm")
def email_confirm(data: EmailConfirmCheck):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, username, password_hash, role, is_used
            FROM pending_users
            WHERE email = %s AND code = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (data.email, data.code),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=400,
                detail="Неверный код или регистрация не найдена"
            )

        pending_id, username, password_hash, role, is_used = row
        if is_used:
            raise HTTPException(
                status_code=400,
                detail="Код уже использован. Начните регистрацию заново."
            )

        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        cur.execute(
            """
            INSERT INTO users (email, username, password, role, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
            RETURNING id
            """,
            (data.email, username, password_hash, role),
        )
        user_id = cur.fetchone()[0]

        cur.execute(
            "UPDATE pending_users SET is_used = TRUE WHERE id = %s",
            (pending_id,),
        )

        return {
            "message": "Email подтверждён, аккаунт создан",
            "id": user_id,
            "email": data.email,
            "username": username,
            "role": role,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("EMAIL CONFIRM ERROR:", e)
        raise HTTPException(status_code=500, detail="Ошибка подтверждения email")
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
            SELECT id, username, password, role, is_active
            FROM users
            WHERE email = %s
            """,
            (data.email,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Неверный email или пароль")

        user_id, username, db_password, role, is_active = row

        if not is_active:
            raise HTTPException(400, "Аккаунт удалён")

        ok = verify_password(data.password, db_password)
        if not ok:
            raise HTTPException(400, "Неверный email или пароль")

        return {
            "id": user_id,
            "email": data.email,
            "username": username,
            "role": role,
            "is_active": is_active,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Ошибка авторизации")
    finally:
        cur.close()
        conn.close()


@app.post("/api/password/reset-request")
def reset_req(data: PasswordResetRequest, bg: BackgroundTasks):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Пользователь не найден")

        user_id = row[0]
        code = str(random.randint(100000, 999999))

        cur.execute(
            """
            UPDATE password_reset_codes
            SET is_used = TRUE
            WHERE user_id = %s AND is_used = FALSE
            """,
            (user_id,),
        )

        cur.execute(
            "INSERT INTO password_reset_codes (user_id, code) VALUES (%s, %s)",
            (user_id, code),
        )

        bg.add_task(send_reset_email, data.email, code)

        return {"message": "Код отправлен"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/password/reset-confirm")
def reset_confirm(data: PasswordResetConfirm):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Пользователь не найден")

        user_id = row[0]

        cur.execute(
            """
            SELECT id, is_used
            FROM password_reset_codes
            WHERE user_id = %s AND code = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, data.code),
        )
        code_row = cur.fetchone()
        if not code_row:
            raise HTTPException(400, "Неверный код")

        code_id, is_used = code_row
        if is_used:
            raise HTTPException(400, "Код уже использован")

        cur.execute(
            "UPDATE password_reset_codes SET is_used = TRUE WHERE id = %s",
            (code_id,),
        )

        new_hashed = hash_password(data.new_password)
        cur.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_hashed, user_id),
        )

        return {"message": "Пароль обновлён"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/account/delete")
def delete_account(data: AccountDelete):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Пользователь не найден")

        user_id = row[0]

        cur.execute(
            "DELETE FROM password_reset_codes WHERE user_id = %s",
            (user_id,),
        )
        cur.execute(
            "DELETE FROM email_confirm_codes WHERE user_id = %s",
            (user_id,),
        )
        cur.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,),
        )

        return {"message": "Аккаунт удалён"}
    finally:
        cur.close()
        conn.close()
