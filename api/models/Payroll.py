from sqlalchemy import Column, String, Integer, ForeignKey, Float,TIMESTAMP,DateTime
from database import Base
from sqlalchemy.orm import relationship
from fastapi import HTTPException, Depends
from sqlalchemy.sql import func
from datetime import datetime


class Payroll(Base):
    __tablename__ = 'payrolls'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'))
    salary = Column(Float)
    benefits = Column(String)  
    pay_date = Column(DateTime, default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    employee = relationship("Employee", back_populates="payrolls")