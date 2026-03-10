from fastapi import FastAPI
from twilio.rest import Client
import os

app = FastAPI()

@app.post("/send_sms")
def send_sms(phone: str, message: str):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    client.messages.create(body=message, from_="+254XXX", to=phone)
    return {"status": "sent"}
