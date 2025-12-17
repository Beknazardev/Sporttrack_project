import os
from typing import Optional

import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="SportTrack Users Service")

DB_NAME = os.getenv("DB_NAME", "sporttrack")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Postgres123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

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


@app.get("/api/ping")
def ping():
    return {"status": "users-service ok"}


@app.get("/api/users/search")
def search_users(q: str = Query(...), coach_id: Optional[int] = None):
    q = (q or "").strip()
    if not q:
        raise HTTPException(422, "q is required")

    conn = get_conn()
    cur = conn.cursor()
    try:
        if q.isdigit():
            cur.execute(
                "SELECT id, email, username, sport, role FROM users WHERE id=%s",
                (int(q),),
            )
        else:
            cur.execute(
                """
                SELECT id, email, username, sport, role
                FROM users
                WHERE email ILIKE %s OR username ILIKE %s
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (f"%{q}%", f"%{q}%"),
            )

        rows = cur.fetchall()

        result = []
        for r in rows:
            user_id, email, username, sport, role = r
            link_status = None

            # если ищем спортсменов и передали coach_id — покажем статус связи
            if coach_id is not None and role == "athlete":
                cur.execute(
                    """
                    SELECT status
                    FROM trainer_athletes
                    WHERE coach_id=%s AND athlete_id=%s
                    """,
                    (coach_id, user_id),
                )
                s = cur.fetchone()
                if s:
                    link_status = s[0]

            result.append(
                {
                    "id": user_id,
                    "email": email,
                    "username": username,
                    "sport": sport,
                    "role": role,
                    "link_status": link_status,
                }
            )

        return result
    finally:
        cur.close()
        conn.close()
