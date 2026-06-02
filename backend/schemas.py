from pydantic import BaseModel
from typing import Optional

class LearnRequest(BaseModel):
    title: str
    description: str
    rootCause: str
    fixDescription: str
    severity: str = "medium"
    fixedBy: str
    filePath: Optional[str] = None
    language: Optional[str] = None

class LearnResponse(BaseModel):
    bugId: str
    message: str

class CheckRequest(BaseModel):
    content: str

class BugMatch(BaseModel):
    line: int
    bugId: str
    title: str
    description: str
    fixedBy: str
    date: str
    score: float

class PatchBugRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    rootCause: Optional[str] = None
    fixDescription: Optional[str] = None
    severity: Optional[str] = None
    approved: Optional[bool] = None
    changedBy: str 