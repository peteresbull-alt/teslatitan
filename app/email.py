import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.conf import settings
import os
from decouple import config


ADMIN_EMAIL = settings.ADMIN_EMAIL
FROM_EMAIL = settings.FROM_EMAIL
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_SMTP_SERVER = settings.EMAIL_SMTP_SERVER
EMAIL_SMTP_PORT=465
MAIN_ADMIN = ADMIN_EMAIL

def send_password_reset_email(to_email, reset_link):
    # Email content
    subject = "Password Reset Request Halal Wealth Builder"
    html_content = f"""
    <html>
    <body>
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="https://res.cloudinary.com/daf9tr3lf/image/upload/v1741706174/halal_logo_dark_zcktcw.png" alt="Logo" style="width: 150px;"/>
            </div>
            <h2>Password Reset</h2>
            <p>You requested a password reset. Click the link below to set a new password:</p>
            <a href="{reset_link}" style="display:inline-block; padding:10px; background- color:white; text-decoration:none;">
                Reset Password
            </a>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Thank you.</p>
            <p style="text-align: center; font-size: 14px; color: #777; margin-top: 30px;">
                © 2025 Halal Wealth Builder. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = f"Halal Wealth Builder <{FROM_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    
    
    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(ADMIN_EMAIL,EMAIL_PASSWORD)
            server.sendmail(ADMIN_EMAIL, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")