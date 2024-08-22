from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id"))
    education_level = Column(String(length=50))
    institution = Column(String(length=50))
    specialization = Column(String(length=50))
    field_of_study = Column(String(length=50))
    year_of_passing = Column(Integer)
    percentage = Column(Float)


    # Define many-to-one relationship with Employee
    Emloyee = relationship("Emloyee", back_populates="educations")
    
   

