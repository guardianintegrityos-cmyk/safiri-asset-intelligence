# outreach.py
from twilio.rest import Client
import smtplib

def send_sms(phone, message):
    client = Client("TWILIO_SID", "TWILIO_AUTH")
    client.messages.create(body=message, from_="+254XXX", to=phone)

def send_email(to_email, subject, body):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email', 'password')
    server.sendmail('your_email', to_email, f"Subject:{subject}\n\n{body}")
