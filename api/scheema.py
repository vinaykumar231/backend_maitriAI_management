from pydantic import BaseModel,  Field, EmailStr, validator
from typing import Optional, List
from fastapi import UploadFile, File
from datetime import date, datetime
from enum import Enum
from sqlalchemy import JSON
import re

################################## maitri user #############################

class LoginInput(BaseModel):
    email: str
    user_password: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    class Config:
        from_attributes = True


class UserType(str, Enum):
    superAdmin = "superadmin"
    admin = "admin"
    user = "user"
   
class UserCreate(BaseModel):
    user_name: str
    user_email: str
    user_password: str
    user_type: UserType = UserType.user
    phone_no: str

    class Config:
        from_attributes = True

class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    phone_no: Optional[int] = None
    user_type: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

################################### employee profile ############################

# Pydantic models for request body validation
class EmployeeContactCreate(BaseModel):
    primary_number: str
    secondary_number: Optional[str] = None
    primary_email_id: str
    secondary_email_id: Optional[str] = None
    current_address: str
    permanent_address: str

class EducationCreate(BaseModel):
    education_level: str
    institution: str
    specialization: str
    field_of_study: str
    year_of_passing: int
    percentage: float

class EmergencyContactCreate(BaseModel):
    emergency_contact_name: str
    relation: str
    emergency_contact_number: int

class DependentsCreate(BaseModel):
    dependent_name: str
    realtion: str
    date_of_birth: date

class SkillCreate(BaseModel):
    skill: str
    certification: str

class LanguagesSpokenCreate(BaseModel):
    languages: str

class EmployeeProfileCreate(BaseModel):
    name: str
    email: str
    department: str
    position_name: str
    contact_info: EmployeeContactCreate
    education: List[EducationCreate]
    emergency_contacts: List[EmergencyContactCreate]
    dependents: List[DependentsCreate]
    skills: List[SkillCreate]
    languages: List[LanguagesSpokenCreate]
