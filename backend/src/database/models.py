from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(255), unique=True, nullable=False)  # Store Google ID for OAuth
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    channel_id = Column(String(255), unique=True, nullable=False)  # Unique channel ID for the user
    access_token = Column(Text, nullable=False)  # Access token
    refresh_token = Column(Text, nullable=False)  # Refresh token
    token_expiry = Column(TIMESTAMP, nullable=False)  # Expiry of access token
    created_at = Column(TIMESTAMP, default=datetime.utcnow)  # Default timestamp for creation
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto update timestamp

    videos = relationship("Video", back_populates="owner")  # Relationship with videos
