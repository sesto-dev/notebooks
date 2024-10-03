# models.py

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to positions
    positions = relationship("Position", back_populates="owner")


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, index=True)
    ticket = Column(Integer, unique=True, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    volume = Column(Float, nullable=False)
    position_type = Column(String, nullable=False)  # 'long' or 'short'
    price_open = Column(Float, nullable=False)
    price_current = Column(Float, nullable=True)
    sl = Column(Float, nullable=True)
    tp = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    leverage = Column(Integer, nullable=False, default=500)
    deviation = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Foreign key to User
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="positions")