from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..database import Base, engine
from ..models import User, ChannelInfo

DATABASE_URL = "postgresql://admin:admin@localhost/projectyt"

# Create engine
engine = create_engine(DATABASE_URL)

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Recreate all tables
Base.metadata.create_all(bind=engine)

print("All tables have been reset.")