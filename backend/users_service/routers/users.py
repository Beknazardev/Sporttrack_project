from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models

router = APIRouter(prefix="/api/users", tags=["users"])  # <-- ВОТ ОНА


@router.get("/search")
def search_users(q: str, db: Session = Depends(get_db)):
    query = db.query(models.User)

    if q.isdigit():
        query = query.filter(models.User.id == int(q))
    elif "@" in q:
        query = query.filter(models.User.email.ilike(f"%{q}%"))
    else:
        query = query.filter(models.User.username.ilike(f"%{q}%"))

    users = query.limit(50).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "sport": getattr(u, "sport", None),
            "role": getattr(u, "role", None),
        }
        for u in users
    ]
