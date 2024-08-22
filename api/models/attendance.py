from sqlalchemy import Column, Integer, String, JSON, DateTime, func,Date, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    emloyee_id = Column(JSON)
    date = Column(DateTime, default=func.now())
    status = Column(JSON) 


   
    


    