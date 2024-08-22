from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base
from sqlalchemy.orm import relationship



class LanguagesSpoken(Base):
    __tablename__ = "languages_spoken"

    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id"))
    languages = Column(String(length=50))

    # Define many-to-one relationship with Employee
    Emloyee = relationship("Emloyee", back_populates="languages_spoken")
    