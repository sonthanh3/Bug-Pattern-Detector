from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

TEAM_TOKEN = os.getenv("TEAM_TOKEN", "youseeit-dev-token")

def verify_token(authorization: str = Header(...)):
    """
    Validate team token from Authorization header.
    Expected format: Bearer YOUR_TOKEN
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    if token != TEAM_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid team token")
    
    return token