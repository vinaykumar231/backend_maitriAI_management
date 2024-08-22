from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from .user import MaitriUser


class Emloyee(Base):
    __tablename__ = 'Emloyees'

    emloyee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    name = Column(String(255))
    email = Column(String(255))
    department = Column(String(255))
    position_name= Column(String(255))
    profile_pic=Column(String(255))
    documents=Column(String(255))
    

    # Define one-to-one relationship with EmloyeeContact
    contact_information = relationship("EmloyeeContact", back_populates="Emloyee")
    
    educations = relationship("Education", back_populates="Emloyee")

    dependents = relationship("Dependents", back_populates="Emloyee")

    emergency_contact = relationship("EmergencyContact", back_populates="Emloyee")

    skills = relationship("Skill", back_populates="Emloyee")

    languages_spoken = relationship("LanguagesSpoken", back_populates="Emloyee")

    user = relationship("MaitriUser", back_populates="Emloyee")

    

    
    