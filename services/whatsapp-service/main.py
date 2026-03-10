from fastapi import FastAPI

app = FastAPI(title="WhatsApp Service")

@app.post("/send")
def send_whatsapp(to: str, message: str):
    # placeholder logic
    print(f"Sending WhatsApp to {to}: {message}")
    return {"status": "sent"}