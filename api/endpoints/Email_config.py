import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import bcrypt
from pydantic import EmailStr, BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form


######################################################################################################################
                # For sending Email
#######################################################################################################################

async def send_email(subject, email_to, body):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'  # Corrected SMTP server address for Gmail
    smtp_port = 587  # Corrected SMTP port for TLS encryption
    smtp_username = 'vinaykumar900417@gmail.com'  # Update with your email
    smtp_password = 'fgyc cjhy lfmb fddk'  # Update with your email password

    try:
        # Create a connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(smtp_username, smtp_password)  # Login to the SMTP server

        # Construct the email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Send the email
        server.sendmail(smtp_username, email_to, msg.as_string())

        # Close the connection to the SMTP server
        server.quit()

    except Exception as e:
        # Handle any exceptions, such as authentication failure
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")