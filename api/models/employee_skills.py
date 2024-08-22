from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id"))  
    skill = Column(String(length=50))
    certification = Column(String(length=50))
    

    # Define many-to-one relationship with Emloyee
    Emloyee = relationship("Emloyee", back_populates="skills")
    
