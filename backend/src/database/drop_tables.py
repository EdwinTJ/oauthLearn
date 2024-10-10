from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .database import Base, engine
from .models import User, ChannelInfo

DATABASE_URL = "postgresql://admin:admin@localhost/projectyt"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def drop_all_tables():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("All tables have been dropped.")

if __name__ == "__main__":
    drop_all_tables()
