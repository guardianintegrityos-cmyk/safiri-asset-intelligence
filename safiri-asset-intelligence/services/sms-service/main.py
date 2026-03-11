from fastapi import FastAPI

app = FastAPI(title="SMS Service")

@app.post("/send")
def send_sms(to: str, message: str):
    # placeholder logic
    print(f"Sending SMS to {to}: {message}")
    return {"status": "sent"}