from fastapi import FastAPI
from routes import claims, users

app = FastAPI(title="Safiri Asset Intelligence API")

# Include routes
app.include_router(claims.router, prefix="/claims", tags=["Claims"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Welcome to Safiri Asset Intelligence API"}
