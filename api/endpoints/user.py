from fastapi import FastAPI, HTTPException, Request,APIRouter
from pydantic import BaseModel
import requests
import folium
import datetime
from geopy.distance import geodesic
from typing import Tuple
from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer, get_user_id_from_token,get_admin, get_current_user
from database import get_db, api_response
from ..scheema import LoginInput, UserCreate,UpdateUser,UserType
from ..models import MaitriUser
import bcrypt
from .Email_config import send_email
import random
import pytz
import bcrypt
from auth.auth_handler import signJWT
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse


router = APIRouter()


ALLOWED_LOGIN_LOCATION = (19.2316, 72.8532) 
MAX_DISTANCE = 500  

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    distance_meters = geodesic((lat1, lon1), (lat2, lon2)).meters
    return distance_meters

@router.post('/maitri_user_login/')
async def maitri_login(credential: LoginInput, request: Request, db: Session = Depends(get_db)):
    try:
        # Get user's location from request body
        request_body = await request.json()
        user_lat = request_body['location']['latitude']
        user_lon = request_body['location']['longitude']
        
        # Calculate distance from allowed location
        distance = calculate_distance(ALLOWED_LOGIN_LOCATION[0], ALLOWED_LOGIN_LOCATION[1], user_lat, user_lon)
        
        if distance > MAX_DISTANCE:
            raise HTTPException(
                status_code=401,
                detail=f"Login not allowed from this location. You are {distance:.2f} meters away from the allowed location."
            )
        
        user = db.query(MaitriUser).filter(MaitriUser.user_email == credential.email).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"Record with Email: {credential.email} not found")

        if not bcrypt.checkpw(credential.user_password.encode('utf-8'), user.user_password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate JWT token
        token, exp = signJWT(user.user_id, user.user_type)
        
        response = {
            "message": "Login successful",
            "token": token,
            "exp": exp,
            "user_id": user.user_id,
            "user_name": user.user_name,
            "email_id": user.user_email,
            "user_type": user.user_type,
            "created_on": user.created_on.isoformat(),
            "phone_no": user.phone_no,
            "distance": f"{distance:.2f} meters"
        }

        return JSONResponse(content=response)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Login failed: {str(e)}"})
    
    
@router.post("/insert/maitri_user/")
async def maitri_register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Call the method to handle user registration
        result = MaitriUser.maitri_register(data.dict(), db)
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_my_profile")
def get_current_user_details(current_user: MaitriUser = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_details = {
            "user_id": current_user.user_id,
            "username": current_user.user_name,
            "email": current_user.user_email,
            "user_type": current_user.user_type,
            "created_on": current_user.created_on,

        }
        return api_response(data=user_details, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


############################################################################################

@router.get("/read/maitri_user")
async def searchall(user_id: int = None, user_type: UserType = None, page_num: int = 1, page_size: int = 20,
                    db: Session = Depends(get_db)):
    return MaitriUser.searchall(user_id, user_type, page_num, page_size, db)


@router.put("/update/maitri_user/{user_id}", dependencies=[Depends(JWTBearer())])
async def lms_user_update(user_data: UpdateUser, user_id: int,
                          current_user: MaitriUser = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    try:
        if user_data.user_type and user_data.user_type not in {"user", "admin", "superadmin"}:
            raise HTTPException(status_code=403, detail="Invalid user type. Allowed values: user, admin, superadmin, student, parent")

        if current_user.user_type == "admin" or current_user.user_id == user_id:
            db_user = db.query(MaitriUser).filter(MaitriUser.user_id == user_id, MaitriUser.is_deleted == False).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail="Record not found")

            if user_data.user_email:
                existing_user = db.query(MaitriUser).filter(
                    MaitriUser.user_email == user_data.user_email,
                    MaitriUser.user_id != user_id
                ).first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="Email already exists for another user")

            hero_data = user_data.dict(exclude_unset=True)
            for key, value in hero_data.items():
                setattr(db_user, key, value)

            is_administrator: bool = current_user.user_type == "admin"

            if (is_administrator and user_data.new_password) or (
                    not is_administrator and user_data.current_password and user_data.new_password):
                if not MaitriUser.validate_password(user_data.new_password):
                    raise HTTPException(status_code=400, detail="Invalid new password")

                current_password = None if is_administrator else user_data.current_password
                MaitriUser.change_password(current_password, user_data.new_password, user_id, is_administrator, db)

            db.commit()
            response = api_response(200, message="User Data updated successfully")
            return response
        else:
            raise HTTPException(status_code=403, detail="Forbidden: You are not authorized to update this user's data.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

#######################################################################################

# @staticmethod
# def validate_password(password):
#         return len(password) >= 8


# @router.put("/change_password/{user_id}")
# async def change_password(current_password: str, new_password: str, confirm_new_password: str, current_user: MaitriUser = Depends(get_current_user), db: Session = Depends(get_db)):
#     try:
#         if new_password != confirm_new_password:
#             raise HTTPException(status_code=400, detail="New passwords do not match")

#         user = db.query(MaitriUser).filter(MaitriUser.user_id == current_user.user_id, MaitriUser.is_deleted == False).first()
#         if not user:
#             raise HTTPException(status_code=404, detail=f"User with ID {current_user.user_id} not found")

#         if not bcrypt.checkpw(current_password.encode('utf-8'), user.user_password.encode('utf-8')):
#             raise HTTPException(status_code=400, detail="Wrong current password")

#         if not MaitriUser.validate_password(new_password):
#             raise HTTPException(status_code=400, detail="Invalid new password")
        
#         hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
#         user.user_password = hashed_new_password

#         db.commit()
#         contact = "900-417-3181"
#         email_contact = "vinay@example.com"

#         reset_email_body = f"""
#         <p>Dear User,</p>
#         <p>Your password has been successfully changed.</p>
#         <p>If you did not request this change, please contact support at {contact} or email us at {email_contact}.</p>
#         <p>Thank you!</p>
#         <br><br>
#         <p>Best regards,</p>
#         <p>Vinay Kumar</p>
#         <p>MaitriAI</p>
#         <p>900417181</p>
#         """
#         await send_email(
#             subject="Password Change Confirmation",
#             email_to=user.user_email,
#             body=reset_email_body
#         )
#         return {"message": "Password changed successfully"}

#     except HTTPException as e:
#         raise e

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# def generate_otp():
#     return random.randint(100000, 999999)

# # Function to send OTP email
# async def send_otp_email(email: str, otp: int):
#     otp_email_body = f"""
#     <p>Dear User,</p>
#     <p>Your OTP for password reset is: <strong>{otp}</strong></p>
#     <p>Please use this OTP to reset your password.</p>
#     <br><br>
#     <p>Best regards,</p>
#     <p>Vinay Kumar</p>
#     <p>MaitriAI</p>
#     <p>900417181</p>
#     """
#     await send_email(
#         subject="Password Reset OTP",
#         email_to=email,
#         body=otp_email_body
#     )

# @router.post("/send_otp")
# async def send_otp(email: str, db: Session = Depends(get_db)):
#     user = db.query(MaitriUser).filter(MaitriUser.user_email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail=f"User with email {email} not found")

#     otp = generate_otp()
#     utc_now = pytz.utc.localize(datetime.utcnow())
#     ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
#     # Update the existing user record
#     user.reset_otp = otp
#     user.otp_generated_at = ist_now
    
#     db.commit()

#     await send_otp_email(email, otp)
#     return {"message": "OTP sent successfully"}

# @router.put("/reset_password")
# async def reset_password(email: str, otp: int, new_password: str, confirm_new_password: str, db: Session = Depends(get_db)):
#     try:
#         user = db.query(MaitriUser).filter(MaitriUser.user_email == email).first()
#         if not user:
#             raise HTTPException(status_code=404, detail=f"User with email {email} not found")

#         # Verify OTP
#         if user.reset_otp != otp:
#             raise HTTPException(status_code=400, detail="Invalid OTP")

#         # Check OTP expiration
#         ist_tz = pytz.timezone('Asia/Kolkata')
#         current_time = datetime.now(ist_tz)
        
#         # Ensure otp_generated_at is timezone-aware
#         otp_generated_at = user.otp_generated_at.replace(tzinfo=pytz.UTC).astimezone(ist_tz)
        
#         otp_age = current_time - otp_generated_at
#         if otp_age > timedelta(minutes=10):
#             raise HTTPException(status_code=400, detail="OTP has expired")

#         if new_password != confirm_new_password:
#             raise HTTPException(status_code=400, detail="Passwords do not match")

#         hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
#         user.user_password = hashed_new_password
        
#         # Clear the OTP after successful password reset
#         user.reset_otp = None
#         user.otp_generated_at = None

#         db.commit()

#         # Send email for password reset
#         contact = "900-417-3181"
#         email_contact = "vinay@example.com"

#         reset_email_body = f"""
#         <p>Dear User,</p>
#         <p>Your password has been successfully changed.</p>
#         <p>If you did not request this change, please contact support at {contact} or email us at {email_contact}.</p>
#         <p>Thank you!</p>
#         <br><br>
#         <p>Best regards,</p>
#         <p>Vinay Kumar</p>
#         <p>MaitriAI</p>
#         <p>900417181</p>
#         """
#         await send_email(
#             subject="Password Reset Confirmation",
#             email_to=email,
#             body=reset_email_body
#         )

#         return {"message": "Password reset successfully"}

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")