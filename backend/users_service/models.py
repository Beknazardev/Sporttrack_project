from .database import Base
from sqlalchemy import Column, Integer, String



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True)
    password = Column(String)
    sport = Column(String, nullable=True)
    role = Column(String)
