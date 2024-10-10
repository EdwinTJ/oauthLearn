from .database import Base, engine
from .models import User, ChannelInfo

# Create all tables
Base.metadata.create_all(bind=engine)
