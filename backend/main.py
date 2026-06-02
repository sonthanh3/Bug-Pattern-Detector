from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base, Bug, BugHistory
from schemas import LearnRequest, LearnResponse, CheckRequest, PatchBugRequest
from embeddings import generate_embedding, get_vector, cosine_similarity, chunk_file, extract_context, score_to_confidence
from auth import verify_token
import datetime
import uuid
import json
import numpy as np

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

SIMILARITY_THRESHOLD = 0.62
# ─── Health Check ───
@app.get("/health")
def health():
    return {"status": "ok"}

# ─── GET /bugs — paginated + search ───
@app.get("/bugs")
def get_bugs(
    page: int = 1,
    limit: int = 20,
    language: str = None,
    severity: str = None,
    keyword: str = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    query = db.query(Bug).filter(Bug.approved == True)

    if language:
        query = query.filter(Bug.language == language)
    if severity:
        query = query.filter(Bug.severity == severity)
    if keyword:
        query = query.filter(
            Bug.title.ilike(f"%{keyword}%") |
            Bug.description.ilike(f"%{keyword}%")
        )

    total = query.count()
    offset = (page - 1) * limit
    bugs = query.offset(offset).limit(limit).all()

    return {
        "bugs": [
            {
                "id": str(bug.id),
                "title": bug.title,
                "description": bug.description,
                "severity": bug.severity,
                "resolved_by": bug.resolved_by,
                "resolved_at": str(bug.resolved_at.date()) if bug.resolved_at else "",
                "language": bug.language,
            }
            for bug in bugs
        ],
        "total": total,
        "page": page,
        "limit": limit
    }

# ─── GET /bugs/:id ───
@app.get("/bugs/{bug_id}")
def get_bug(
    bug_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    return {
        "id": str(bug.id),
        "title": bug.title,
        "description": bug.description,
        "root_cause": bug.root_cause,
        "fix_description": bug.fix_description,
        "severity": bug.severity,
        "resolved_by": bug.resolved_by,
        "resolved_at": str(bug.resolved_at.date()) if bug.resolved_at else "",
        "language": bug.language,
        "file_path": bug.file_path,
        "occurrence_count": bug.occurrence_count,
    }

# ─── PATCH /bugs/:id — edit with version history ───
@app.patch("/bugs/{bug_id}")
def patch_bug(
    bug_id: str,
    request: PatchBugRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    # Save previous snapshot to bug_history
    snapshot = {
        "title": bug.title,
        "description": bug.description,
        "root_cause": bug.root_cause,
        "fix_description": bug.fix_description,
        "severity": bug.severity,
        "approved": bug.approved,
    }

    history = BugHistory(
        id=uuid.uuid4(),
        bug_id=bug.id,
        changed_by=request.changedBy,
        changed_at=datetime.datetime.utcnow(),
        previous_snapshot=snapshot
    )
    db.add(history)

    # Apply updates
    if request.title is not None:
        bug.title = request.title
    if request.description is not None:
        bug.description = request.description
    if request.rootCause is not None:
        bug.root_cause = request.rootCause
    if request.fixDescription is not None:
        bug.fix_description = request.fixDescription
    if request.severity is not None:
        bug.severity = request.severity
    if request.approved is not None:
        bug.approved = request.approved

    bug.updated_at = datetime.datetime.utcnow()

    # Re-generate embedding if title or description changed
    if request.title or request.description:
        text_to_embed = f"{bug.title} {bug.description} {bug.root_cause or ''}"
        bug.embedding = generate_embedding(text_to_embed)

    db.commit()
    db.refresh(bug)

    return {"message": f"Bug updated successfully: {bug.title}"}

# ─── POST /learn ───
@app.post("/learn", response_model=LearnResponse)
def learn(
    request: LearnRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    # Use context extractor for richer embedding
    raw_text = f"{request.title} {request.description} {request.rootCause}"
    enriched_text = extract_context(raw_text, request.language)
    embedding = generate_embedding(enriched_text)

    bug = Bug(
        id=uuid.uuid4(),
        title=request.title,
        description=request.description,
        root_cause=request.rootCause,
        fix_description=request.fixDescription,
        severity=request.severity,
        resolved_by=request.fixedBy,
        resolved_at=datetime.datetime.utcnow(),
        language=request.language,
        file_path=request.filePath,
        embedding=embedding,
    )

    db.add(bug)
    db.commit()
    db.refresh(bug)

    return LearnResponse(
        bugId=str(bug.id),
        message=f"Bug learned successfully: {bug.title}"
    )

# ─── POST /check ───
@app.post("/check")
def check(
    request: CheckRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    print("CHECK ENDPOINT HIT")
    bugs = db.query(Bug).filter(Bug.approved == True, Bug.embedding != None).all()
    print(f"Total bugs in DB: {len(bugs)}")

    if not bugs:
        return {"matches": []}

    # Extract context from file content before chunking
    enriched_content = extract_context(request.content)
    chunks = chunk_file(enriched_content)

    matches = []
    seen_lines = set()

    for chunk in chunks:
        chunk_vector = get_vector(chunk['text'])

        for bug in bugs:
            stored_vector = json.loads(bug.embedding)
            stored_np = np.array(stored_vector)
            score = cosine_similarity(chunk_vector, stored_np)
            confidence = score_to_confidence(score)
            print(f"Bug: {bug.title} | Score: {score} | Confidence: {confidence}%")

            if score >= SIMILARITY_THRESHOLD:
                line = chunk['start_line']
                if line not in seen_lines:
                    seen_lines.add(line)
                    matches.append({
                        "line": line,
                        "bugId": str(bug.id),
                        "title": bug.title,
                        "description": bug.description,
                        "fixedBy": bug.resolved_by,
                        "date": str(bug.resolved_at.date()) if bug.resolved_at else "",
                        "score": round(score, 4),
                        "confidence": confidence
                    })

    matches.sort(key=lambda x: x['score'], reverse=True)
    return {"matches": matches}