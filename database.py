import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, DateTime, BigInteger, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from datetime import datetime

load_dotenv()

Base = declarative_base()
password = quote_plus(os.getenv("PASSWORD"))
user = os.getenv("USER")
host = os.getenv("HOST")
database = os.getenv("DATABASE")


class Message(Base):
        __tablename__ = "messages"
        id = Column(BigInteger, primary_key=True, autoincrement=False)
        author_name = Column(String(255))
        author_id = Column(BigInteger, nullable=False)
        message = Column(String(4000))
        message_send_timestamp = Column(DateTime)
        created_at = Column(TIMESTAMP)
        updated_at = Column(TIMESTAMP)

class Log(Base):
        __tablename__ = "log"
        id = Column(BigInteger, primary_key=True, autoincrement=True)
        author_name = Column(String(255), default="System")
        author_id = Column(String(32), default="System")
        message = Column(String(4000))
        level = Column(Enum("INFO", "WARNING", "ERROR", "DEBUG"), nullable=False)
        date = Column(DateTime, default=datetime.utcnow)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Database_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
engine = create_engine(Database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    try:
        Base.metadata.create_all(engine)
        print("Database connected successfully")
    except Exception as e:
        print(f"Error connecting to database: {e}")
