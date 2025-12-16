from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import psycopg2
import random
import smtplib
from email.message import EmailMessage
import hashlib
import secrets  # для генерации соли


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
DB_PORT = "5432"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "sporttrack.project@gmail.com"
SMTP_PASSWORD = "cfng hixo xptz kmfm"

# ====== ХЭШИРОВАНИЕ ПАРОЛЯ (SHA256 + salt + pepper) ======

PEPPER = "super_secret_pepper_123"  # для учебного проекта можно так, в реале в .env


def hash_password(password: str) -> str:
    # соль 16 байт => 32 hex-символа
    salt = secrets.token_hex(16)
    data = (password + PEPPER + salt).encode("utf-8")
    pwd_hash = hashlib.sha256(data).hexdigest()
    # в БД храним "salt$hash"
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, stored_value: str) -> bool:
    try:
        salt, stored_hash = stored_value.split("$", 1)
    except ValueError:
        return False

    data = (plain_password + PEPPER + salt).encode("utf-8")
    check_hash = hashlib.sha256(data).hexdigest()
    return check_hash == stored_hash


# ====== БАЗА ДАННЫХ ======

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
        print("DB CONNECT ERROR:", e)
        raise HTTPException(status_code=500, detail=f"DB CONNECT ERROR: {e}")


# ====== Pydantic-модели ======

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


# ====== Email-отправка ======

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


# ====== Эндпоинты ======

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
    finally:
        cur.close()
        conn.close()
    return {"db_ok": True, "result": row[0]}


@app.post("/api/register")
def register(user: UserRegister):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1) Проверка email
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

        # 2) Простейшая проверка пароля
        if len(user.password) < 4:
            raise HTTPException(status_code=400, detail="Пароль слишком короткий")

        # 3) Хэшируем пароль
        hashed = hash_password(user.password)

        # 4) Вставляем пользователя
        cur.execute(
            """
            INSERT INTO users (email, username, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id, is_active, is_email_confirmed
            """,
            (user.email, user.username, hashed, user.role),
        )
        user_id, is_active, is_email_confirmed = cur.fetchone()

        return {
            "id": user_id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": is_active,
            "is_email_confirmed": is_email_confirmed,
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
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Пользователь не найден")
        user_id = row[0]

        code = str(random.randint(100000, 999999))

        cur.execute(
            """
            UPDATE email_confirm_codes
            SET is_used = TRUE
            WHERE user_id = %s AND is_used = FALSE
            """,
            (user_id,),
        )
        cur.execute(
            "INSERT INTO email_confirm_codes (user_id, code) VALUES (%s, %s)",
            (user_id, code),
        )

        bg.add_task(send_confirm_email, data.email, code)
        return {"message": "Код отправлен"}
    finally:
        cur.close()
        conn.close()


@app.post("/api/email/confirm")
def email_confirm(data: EmailConfirmCheck):
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
            FROM email_confirm_codes
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
            "UPDATE email_confirm_codes SET is_used = TRUE WHERE id = %s",
            (code_id,),
        )
        cur.execute(
            "UPDATE users SET is_email_confirmed = TRUE WHERE id = %s",
            (user_id,),
        )

        return {"message": "Email подтверждён"}
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
            SELECT id, username, password, role, is_active, is_email_confirmed
            FROM users
            WHERE email = %s
            """,
            (data.email,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(400, "Неверный email или пароль")

        user_id, username, db_password, role, is_active, is_email_confirmed = row

        if not is_active:
            raise HTTPException(400, "Аккаунт удалён")

        if not is_email_confirmed:
            raise HTTPException(400, "Подтвердите email перед входом")

        ok = verify_password(data.password, db_password)
        if not ok:
            raise HTTPException(400, "Неверный пароль")

        return {
            "id": user_id,
            "email": data.email,
            "username": username,
            "role": role,
            "is_active": is_active,
            "is_email_confirmed": is_email_confirmed,
        }
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

        cur.execute("DELETE FROM password_reset_codes WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM email_confirm_codes WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        return {"message": "Аккаунт удалён"}
    finally:
        cur.close()
        conn.close()
