from sqlalchemy import Column, Integer, String

from db import Base


class URL(Base):
    __tablename__ = 'URLs'
    id = Column(Integer, primary_key=True, unique=True, index=True)
    url = Column(String(256))
