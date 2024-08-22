from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException
from database import Base



class EmloyeeContact(Base):
    __tablename__ = "emloyee_contact_info"

    # Define columns
    id = Column(Integer, primary_key=True, index=True)
    Emloyee_id = Column(Integer, ForeignKey("Emloyees.emloyee_id")) 
    primary_number = Column(String(length=50))
    secondary_number = Column(String(length=50), nullable=True)
    primary_email_id = Column(String(length=50))
    secondary_email_id = Column(String(length=50), nullable=True)
    current_address = Column(String(length=255))
    permanent_address = Column(String(length=255))

    # Define one-to-one relationship with Emloyee
    Emloyee = relationship("Emloyee", back_populates="contact_information")