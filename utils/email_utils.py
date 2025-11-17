import smtplib
from email.message import EmailMessage
import os

def send_email(to, subject, message):
    try:
        email = EmailMessage()
        email["From"] = os.getenv("MAIL_USERNAME")
        email["To"] = to
        email["Subject"] = subject
        email.set_content(message)

        # Send email
        with smtplib.SMTP(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT"))) as smtp:
            smtp.starttls()
            smtp.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
            smtp.send_message(email)

        return True

    except Exception as e:
        print("EMAIL ERROR:", e)
        return False
