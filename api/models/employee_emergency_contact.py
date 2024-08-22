from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



class EmergencyContact(Base):
    __tablename__ = "emergency_contact"

    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id"))
    emergency_contact_name = Column(String(length=50))
    relation = Column(String(length=50))
    emergency_contact_number = Column(Integer)

    # Define many-to-one relationship with Employee
    Emloyee = relationship("Emloyee", back_populates="emergency_contact")

    
