from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from database import get_db
from ..models import (Emloyee,EmloyeeContact, LanguagesSpoken, Dependents, Education, EmergencyContact,LanguagesSpoken, Skill,MaitriUser,Attendance)
from ..scheema import EmployeeProfileCreate
from auth.auth_bearer import JWTBearer, get_current_user, get_admin
from typing import Optional
from pydantic import BaseModel,  Field
from datetime import date
from typing import List, Optional
from datetime import datetime
from pytz import timezone
from sqlalchemy import func

import socket

router = APIRouter()

class AttendanceBase(BaseModel):
    employee_id: int
    date: datetime
    status: List[str]

@router.post("/attendance/", response_model=List[AttendanceBase])
def create_attendance(
    employee_ids: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    employee_ids_list = employee_ids.split(',')
    employee_status_list = status.split(',')
    
    ist_now = datetime.now(timezone('Asia/Kolkata'))
    
    attendance_records = []
    
    for i, employee_id in enumerate(employee_ids_list):
        employee = db.query(Emloyee).filter(Emloyee.emloyee_id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail=f"Student with id {employee_id} not found")
        
        existing_attendance = db.query(Attendance).filter(
            Attendance.emloyee_id == employee_id,
            func.date(Attendance.date) == func.date(ist_now)  
        ).first()
        
        if existing_attendance:
            existing_attendance.status = [employee_status_list[i]]
        else:
            db_attendance = Attendance(
                emloyee_id=employee_id,
                status=[employee_status_list[i]], 
                date=ist_now
            )
            db.add(db_attendance)
        
        db.commit()
        attendance_records.append(AttendanceBase(
            employee_id=employee_id,
            date=ist_now,
            status=[employee_status_list[i]]
        ))
    
    return attendance_records

@router.get("/attendance/", response_model=None)
def get_attendance(
    employee_ids: str,
    db: Session = Depends(get_db)
):
    employee_ids_list = employee_ids.split(',')
    all_records = db.query(Attendance).all()
    attendance_records = [record for record in all_records if record.emloyee_id in employee_ids_list]

    if not attendance_records:
        raise HTTPException(status_code=404, detail="No attendance records found for the provided student IDs")
    return attendance_records

@router.get("/employee/only_id_name/", response_model=None)
def get_all_students(db: Session = Depends(get_db)):
    employee = db.query(Emloyee).all()
    return employee


###################################################
# # Define the biometric device connection settings
# device_ip = '192.168.1.100'
# device_port = 8080
# #API_URL = 'http://ebioservernew.esslsecurity.com:99/webservice.asmx?op=GetEmployeeDetails'

# class Attendance(BaseModel):
#     user_id: int
#     date: str
#     time: str
#     status: str

# # Initialize the biometric device connection
# essl = ESSL(device_ip, device_port)

# @router.get("/attendances/biometrics")
# async def get_attendance(start_date: date, end_date: date):
#     try:
#         # Fetch attendance data from the biometric device
#         attendance_data = essl.get_attendance(start_date, end_date)
        
#         # Process the raw data into Attendance objects
#         attendance_records = []
#         for record in attendance_data:
#             attendance_record = Attendance(
#                 user_id=record['user_id'],
#                 date=record['date'],
#                 time=record['time'],
#                 status=record['status']
#             )
#             attendance_records.append(attendance_record)
        
#         return attendance_records
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

####################################
DEVICE_IP = '192.168.1.201'
DEVICE_PORT = 4370

class Attendance(BaseModel):
    user_id: int
    date: str
    time: str
    status: str

class BiometricRecord(BaseModel):
    user_id: int
    timestamp: str
    biometric_data: str

# Function to get all attendance data from the biometric device
def get_all_attendance_data():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((DEVICE_IP, DEVICE_PORT))
            # Send a request to fetch all attendance data
            sock.sendall(b"GET_ALL_ATTENDANCE_DATA\n")

            # Receive the data from the biometric device
            data = sock.recv(4096).decode()

            # Process the raw data into attendance records
            attendance_records = []
            for line in data.split('\n'):
                if line.strip():
                    user_id, date, time, status = line.split(',')
                    attendance_record = Attendance(
                        user_id=int(user_id),
                        date=date,
                        time=time,
                        status=status
                    )
                    attendance_records.append(attendance_record)

            return attendance_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve attendance data: {str(e)}")

@router.get("/attendances/biometrics/all")
async def get_all_attendance():
    try:
        # Fetch all attendance data from the biometric device
        attendance_records = get_all_attendance_data()
        return attendance_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to get all biometric data from the device
def get_all_biometric_data():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((DEVICE_IP, DEVICE_PORT))
            # Send a request to fetch all biometric data
            sock.sendall(b"GET_ALL_BIOMETRIC_DATA\n")

            data = sock.recv(4096).decode()

            biometric_records = []
            for line in data.split('\n'):
                if line.strip():
                    user_id, timestamp, biometric_data = line.split(',')
                    record = BiometricRecord(
                        user_id=int(user_id),
                        timestamp=timestamp,
                        biometric_data=biometric_data
                    )
                    biometric_records.append(record)

            return biometric_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve biometric data: {str(e)}")

@router.get("/biometrics/all")
async def get_all_biometrics():
    try:
        biometric_records = get_all_biometric_data()
        return biometric_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

############################
    

DEVICE_IP = "192.168.168.100"
DEVICE_PORT = 5005

class BiometricRecord(BaseModel):
    user_id: int
    timestamp: str
    biometric_data: str

def get_biometric_data():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(b"GET_BIOMETRIC_DATA\n")
            
            data = sock.recv(4096).decode()
            
            biometric_records = []
            for line in data.split('\n'):
                if line.strip():
                    user_id, timestamp, biometric_data = line.split(',')
                    record = BiometricRecord(
                        user_id=int(user_id),
                        timestamp=timestamp,
                        biometric_data=biometric_data
                    )
                    biometric_records.append(record)
            
            return biometric_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve biometric data: {str(e)}")

@router.get("/biometrics/all")
async def get_biometrics():
    return get_biometric_data()
