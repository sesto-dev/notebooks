from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    ticket = Column(Integer, unique=True)
    symbol = Column(String)
    type = Column(String)
    volume = Column(Float)
    open_time = Column(DateTime)
    open_price = Column(Float)
    close_time = Column(DateTime)
    close_price = Column(Float)
    profit = Column(Float)