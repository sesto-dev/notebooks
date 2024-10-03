# crud.py

from sqlalchemy.orm import Session
from models import User, Position
import datetime

# Existing CRUD functions for User
def create_user(db: Session, username: str, email: str):
    db_user = User(username=username, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# New CRUD functions for Position

def create_position(db: Session, user_id: int, ticket: int, symbol: str, volume: float, position_type: str,
                   price_open: float, sl: float = None, tp: float = None, leverage: int = 500,
                   deviation: int = 20):
    db_position = Position(
        ticket=ticket,
        symbol=symbol,
        volume=volume,
        position_type=position_type,
        price_open=price_open,
        sl=sl,
        tp=tp,
        leverage=leverage,
        deviation=deviation,
        user_id=user_id
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def get_position_by_ticket(db: Session, ticket: int):
    return db.query(Position).filter(Position.ticket == ticket).first()

def get_positions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Position).filter(Position.user_id == user_id).offset(skip).limit(limit).all()

def update_position(db: Session, ticket: int, **kwargs):
    db_position = db.query(Position).filter(Position.ticket == ticket).first()
    if db_position:
        for key, value in kwargs.items():
            setattr(db_position, key, value)
        db_position.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_position)
    return db_position

def delete_position(db: Session, ticket: int):
    db_position = db.query(Position).filter(Position.ticket == ticket).first()
    if db_position:
        db.delete(db_position)
        db.commit()
    return db_position