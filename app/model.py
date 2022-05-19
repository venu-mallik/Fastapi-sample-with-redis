import random
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, conlist, Field, confloat
from sqlalchemy import Column, Integer, String, create_engine, CHAR, JSON, DateTime, Float
from sqlalchemy.orm import Session

from .database import Base


class AsteroidTable(Base):
    __tablename__ = "asteroids"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    type = Column(CHAR)
    size = Column(Integer)
    distance = Column(Integer)
    collision = Column(Float)
    location = Column(JSON)
    observed_time = Column(DateTime)


class AsteroidSchema(BaseModel):
    name: str = Field(
        default_factory=f"Asteroid_{random.randint(0,99999999)}", description="Name of asteroid")
    type: Literal['S', 'C', 'M'] = Field(..., description="one of: S, C, M")
    size: int = Field(..., description="Size of asteroid in meters")
    distance: int = Field(..., description="distance from earth in AU")
    location: conlist(int, min_items=3, max_items=3) = Field(...,
                                                             description="coordinates in x,y,z")
    observed_time: datetime = Field(..., description="time of observation")
    collision: confloat(ge=0, le=1) = Field(...,
                                            description="Collision probability 0 to 1 .")

    class Config:
        orm_mode = True

    @classmethod
    def get_one(cls, db: Session, id: int):
        return db.query(AsteroidTable).filter(AsteroidTable.id == id).first()

    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100):
        return db.query(AsteroidTable).offset(skip).limit(limit).all()

    @classmethod
    def delete_one(cls, db, id):
        db.query(AsteroidTable).filter(
            AsteroidTable.id == id).delete()
        db.commit()
        return {'success': True}

    def save(self, db, id=None):
        item = AsteroidTable(**{k: v for k, v in self.__dict__.items()})
        if id:
            item.id = id
            db.query(AsteroidTable).filter(
                AsteroidTable.id == id).update({**item})
            db.commit()
            db.refresh(item)
            return {'update': True}
        else:
            db.add(item)
            db.commit()
            db.refresh(item)
            return {k: v for k, v in item.__dict__.items()}
