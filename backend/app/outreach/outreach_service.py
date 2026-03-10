from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Twilio config
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
client = Client(TWILIO_SID, TWILIO_AUTH)

# SendGrid config
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
sg = SendGridAPIClient(SENDGRID_API_KEY)

def send_sms(to_number, message):
    """Send SMS via Twilio"""
    return client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=to_number
    )

def send_whatsapp(to_number, message):
    """Send WhatsApp message via Twilio"""
    return client.messages.create(
        body=message,
        from_="whatsapp:" + TWILIO_PHONE,
        to="whatsapp:" + to_number
    )

def send_email(to_email, subject, message):
    """Send Email via SendGrid"""
    mail = Mail(
        from_email='noreply@safiri.africa',
        to_emails=to_email,
        subject=subject,
        html_content=message
    )
    response = sg.send(mail)
    return response.status_code
