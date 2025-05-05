from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from database import Base
from datetime import datetime

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, nullable=True)
    file_size = Column(Integer)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)  # Armazena os dados brutos recebidos 