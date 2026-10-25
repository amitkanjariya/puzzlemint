import hmac
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import Personalization, Project
from .schemas import ProjectCreate, ProjectUpdate

TOKEN = os.environ.get("PUZZLEMINT_TOKEN", "")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not TOKEN or len(TOKEN) < 32:
        raise RuntimeError("Set PUZZLEMINT_TOKEN to a random token of at least 32 characters")
    yield


app = FastAPI(title="PuzzleMint Local API", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None)


@app.middleware("http")
async def limit_body(request: Request, call_next):
    if request.method in {"POST", "PATCH", "PUT"}:
        size = request.headers.get("content-length")
        if size and (not size.isdigit() or int(size) > 65536):
            return JSONResponse(status_code=413, content={"detail": "Request is too large"})
        body = await request.body()
        if len(body) > 65536:
            return JSONResponse(status_code=413, content={"detail": "Request is too large"})
    return await call_next(request)


def authorize(authorization: str | None = Header(default=None)):
    supplied = authorization[7:] if authorization and authorization.startswith("Bearer ") else ""
    if not TOKEN or not hmac.compare_digest(supplied, TOKEN):
        raise HTTPException(status_code=401, detail="Invalid local session token")


def get_project(project_id: str, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Adventure not found")
    return project


def project_data(project: Project) -> dict:
    return {
        "id": project.id,
        "title": project.title,
        "theme": project.theme,
        "occasion": project.occasion,
        "difficulty": project.difficulty,
        "duration_minutes": project.duration_minutes,
        "puzzle_count": project.puzzle_count,
        "random_seed": project.random_seed,
        "status": project.status,
        "player_alias": project.personalization.player_alias,
        "final_message": project.personalization.final_message,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/projects", status_code=201, dependencies=[Depends(authorize)])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump(exclude={"player_alias", "final_message"}))
    project.personalization = Personalization(player_alias=payload.player_alias, final_message=payload.final_message)
    db.add(project)
    db.commit()
    return project_data(project)


@app.get("/api/v1/projects", dependencies=[Depends(authorize)])
def list_projects(db: Session = Depends(get_db)):
    projects = db.scalars(select(Project).order_by(Project.updated_at.desc())).all()
    return [project_data(project) for project in projects]


@app.get("/api/v1/projects/{project_id}", dependencies=[Depends(authorize)])
def read_project(project_id: str, db: Session = Depends(get_db)):
    return project_data(get_project(project_id, db))


@app.patch("/api/v1/projects/{project_id}", dependencies=[Depends(authorize)])
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    values = payload.model_dump(exclude_unset=True)
    if project.puzzles and any(key in values for key in {"theme", "difficulty", "puzzle_count", "random_seed"}):
        project.puzzles.clear()
        project.status = "draft"
    for key, value in values.items():
        if key in {"player_alias", "final_message"}:
            setattr(project.personalization, key, value)
        else:
            setattr(project, key, value)
    db.commit()
    return project_data(project)


@app.delete("/api/v1/projects/{project_id}", status_code=204, dependencies=[Depends(authorize)])
def delete_project(project_id: str, db: Session = Depends(get_db)):
    db.delete(get_project(project_id, db))
    db.commit()
