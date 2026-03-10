from fastapi import FastAPI

app = FastAPI(title="Email Service")

@app.post("/send")
def send_email(to: str, subject: str, body: str):
    # placeholder logic
    print(f"Sending Email to {to}: {subject} - {body}")
    return {"status": "sent"}