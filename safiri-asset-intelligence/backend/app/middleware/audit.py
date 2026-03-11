from fastapi import Request
from db import get_db
import json

async def audit_log(request: Request, user: str = "system", details: dict = None):
    db = get_db()
    query = """
    INSERT INTO audit_logs (action, user, details)
    VALUES (%s, %s, %s)
    """
    db.execute(query, (request.url.path, user, json.dumps(details or {})))
    db.commit()
