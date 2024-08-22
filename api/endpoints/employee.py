from fastapi import APIRouter, Form, Depends, HTTPException, UploadFile,File
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from database import get_db
from ..models import (Emloyee,EmloyeeContact, LanguagesSpoken, Dependents, Education, EmergencyContact,LanguagesSpoken, Skill,MaitriUser)
from ..scheema import EmployeeProfileCreate
from auth.auth_bearer import JWTBearer, get_current_user, get_admin
from typing import Optional
from pydantic import BaseModel,  Field
from datetime import date
from typing import List, Optional
from datetime import date
from typing import Optional
import os
import uuid
import shutil

router = APIRouter()

def save_upload_file(upload_file: Optional[UploadFile]) -> Optional[str]:
    if not upload_file:
        return None
    
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "uploads", unique_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Convert backslashes to forward slashes
        file_path = file_path.replace("\\", "/")
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
@router.post("/employee/add_employee")
async def create_employee_profile(
    name: str = Form(...),
    email: str = Form(...),
    department: str = Form(...),
    position_name: str = Form(...),
    primary_number: str = Form(...),
    primary_email_id: str = Form(...),
    current_address: str = Form(...),
    permanent_address: str = Form(None),
    education_level: str = Form(...),
    institution: str = Form(...),
    specialization: str = Form(...),
    field_of_study: str = Form(...),
    year_of_passing: int = Form(...),
    percentage: float = Form(...),
    emergency_contact_name: str = Form(...),
    emergency_relation: str = Form(...),
    emergency_contact_number: str = Form(...),
    dependent_name: str = Form(...),
    dependent_relation: str = Form(...),
    dependent_date_of_birth: date = Form(None),
    skill: str = Form(...),
    certification: str = Form(...),
    profile_pic:UploadFile=File(None),
    documents:UploadFile=File(None),
    languages: str = Form(...),
    db: Session = Depends(get_db),
    current_user: MaitriUser = Depends(get_current_user)
):
    profile_pic_path = save_upload_file(profile_pic)
    addocuments_path = save_upload_file(documents)
    try:
        # Create employee
        db_employee = Emloyee(
            user_id=current_user.user_id,
            name=name,
            email=email,
            department=department,
            position_name=position_name,
            profile_pic=profile_pic_path,
            documents=addocuments_path
        )
        db.add(db_employee)
        db.flush()

        # Create employee contact
        db_contact = EmloyeeContact(
            Emloyee_id=db_employee.emloyee_id,
            primary_number=primary_number,
            primary_email_id=primary_email_id,
            current_address=current_address,
            permanent_address=permanent_address
        )
        db.add(db_contact)

        # Create education record
        db_education = Education(
            Emloyee_id=db_employee.emloyee_id,
            education_level=education_level,
            institution=institution,
            specialization=specialization,
            field_of_study=field_of_study,
            year_of_passing=year_of_passing,
            percentage=percentage
        )
        db.add(db_education)

        # Create emergency contact
        db_emergency = EmergencyContact(
            Emloyee_id=db_employee.emloyee_id,
            emergency_contact_name=emergency_contact_name,
            relation=emergency_relation,
            emergency_contact_number=emergency_contact_number
        )
        db.add(db_emergency)

        # Create dependent
        db_dependent = Dependents(
            Emloyee_id=db_employee.emloyee_id,
            dependent_name=dependent_name,
            realtion=dependent_relation,
            date_of_birth=dependent_date_of_birth
        )
        db.add(db_dependent)

        # Create skill
        db_skill = Skill(
            Emloyee_id=db_employee.emloyee_id,
            skill=skill,
            certification=certification
        )
        db.add(db_skill)

        # Create language spoken
        db_language = LanguagesSpoken(
            Emloyee_id=db_employee.emloyee_id,
            languages=languages
        )
        db.add(db_language)

        # Commit all changes
        db.commit()

        return {"message": "Employee profile created successfully", "employee_id": db_employee.emloyee_id}

    except Exception as e:
        db.rollback()
    raise HTTPException(status_code=400, detail=f"Error creating employee profile: {str(e)}")
    

@router.get("/employee-profile/{employee_id}/")
async def get_employee_profile(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Emloyee).filter(Emloyee.emloyee_id == employee_id).first()
    
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db_contact = db.query(EmergencyContact).filter(EmergencyContact.Emloyee_id == employee_id).first()
    db_education = db.query(Education).filter(Education.Emloyee_id == employee_id).first()
    db_emergency = db.query(EmergencyContact).filter(EmergencyContact.Emloyee_id == employee_id).first()
    db_dependent = db.query(Dependents).filter(Dependents.Emloyee_id == employee_id).first()
    db_skill = db.query(Skill).filter(Skill.Emloyee_id == employee_id).first()
    db_language = db.query(LanguagesSpoken).filter(LanguagesSpoken.Emloyee_id == employee_id).first()

    return {
        "employee": db_employee,
        "contact": db_contact,
        "education": db_education,
        "emergency_contact": db_emergency,
        "dependent": db_dependent,
        "skill": db_skill,
        "languages": db_language
    }

@router.get("/employee-profiles/")
async def get_all_employee_profiles(db: Session = Depends(get_db)):
    employees = db.query(Emloyee).all()
    result = []
    
    for employee in employees:
        employee_id = employee.emloyee_id
        
        contact = db.query(EmergencyContact).filter(EmergencyContact.Emloyee_id == employee_id).first()
        education = db.query(Education).filter(Education.Emloyee_id == employee_id).first()
        emergency = db.query(EmergencyContact).filter(EmergencyContact.Emloyee_id == employee_id).first()
        dependent = db.query(Dependents).filter(Dependents.Emloyee_id == employee_id).first()
        skill = db.query(Skill).filter(Skill.Emloyee_id == employee_id).first()
        languages = db.query(LanguagesSpoken).filter(LanguagesSpoken.Emloyee_id == employee_id).first()
        
        result.append({
            "employee": employee,
            "contact": contact,
            "education": education,
            "emergency_contact": emergency,
            "dependent": dependent,
            "skill": skill,
            "languages": languages
        })
    
    return result

