from fastapi import Depends
from sqlalchemy.orm import Session
from .database import SessionLocal

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
