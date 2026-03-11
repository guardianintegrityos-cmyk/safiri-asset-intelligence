from fastapi import FastAPI
import requests
import os

app = FastAPI()

@app.post("/send_whatsapp")
def send_whatsapp(phone: str, message: str):
    api_key = os.getenv("WHATSAPP_API_KEY")
    # Example: send request to WhatsApp API
    response = requests.post("https://api.whatsapp.com/send", data={"phone": phone, "text": message, "key": api_key})
    return {"status": response.status_code}
