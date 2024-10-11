from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Trade
import os

# Database connection
DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}:5432/{os.environ['DATABASE_NAME']}"
print(f"Database URL is {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def store_trade(ticket, symbol, trade_type, volume, open_time, open_price):
    session = Session()
    new_trade = Trade(
        ticket=ticket,
        symbol=symbol,
        type=trade_type,
        volume=volume,
        open_time=open_time,
        open_price=open_price
    )
    session.add(new_trade)
    session.commit()
    session.close()

def update_trade(ticket, close_time, close_price, profit):
    session = Session()
    trade = session.query(Trade).filter_by(ticket=ticket).first()
    if trade:
        trade.close_time = close_time
        trade.close_price = close_price
        trade.profit = profit
        session.commit()
    session.close()

def get_trade(ticket):
    session = Session()
    trade = session.query(Trade).filter_by(ticket=ticket).first()
    session.close()
    return trade

def get_all_trades():
    session = Session()
    trades = session.query(Trade).all()
    session.close()
    return trades