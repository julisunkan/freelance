import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_FOLDER = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_FOLDER, exist_ok=True)

DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_FOLDER, 'app.db')}"

engine = create_engine(DATABASE_URI, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class IDRecord(Base):
    __tablename__ = 'id_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename_front = Column(String(255))
    filename_back = Column(String(255))
    filename_selfie = Column(String(255))
    extracted_text = Column(Text)
    structured_data = Column(Text)
    risk_level = Column(String(20), default='UNKNOWN')
    file_hash = Column(String(64))
    is_duplicate = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    groq_api_key = Column(String(255), default='')


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Settings).first():
        db.add(Settings(groq_api_key=''))
        db.commit()
    db.close()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def get_settings(db):
    return db.query(Settings).first()
