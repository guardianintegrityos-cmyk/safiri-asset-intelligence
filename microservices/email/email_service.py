from fastapi import FastAPI
import smtplib
import os

app = FastAPI()

@app.post("/send_email")
def send_email(to_email: str, subject: str, body: str):
    server = smtplib.SMTP(os.getenv("EMAIL_HOST"), 587)
    server.starttls()
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    server.sendmail(os.getenv("EMAIL_USER"), to_email, f"Subject:{subject}\n\n{body}")
    return {"status": "sent"}
