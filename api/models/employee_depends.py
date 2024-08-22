from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class Dependents(Base):
    __tablename__ = "dependents"

    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id"))  
    dependent_name = Column(String(length=50))
    realtion = Column(String(length=50))
    date_of_birth = Column(Date)

    # Define many-to-one relationship with Emloyee
    Emloyee = relationship("Emloyee", back_populates="dependents")
