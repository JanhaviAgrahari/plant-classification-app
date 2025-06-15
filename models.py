from sqlalchemy import Column, Integer, String, Text
from database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    scientific_name = Column(String, unique=True, nullable=False)
    family = Column(String)
    origin = Column(String)
    description = Column(Text)
    uses = Column(Text)
    image_url = Column(Text)