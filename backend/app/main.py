import hmac
import os
from pathlib import Path
from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .engine import clue_text, generate, validate_game
from .export import create_html, create_pdf
from .models import Export, Hint, Personalization, Project, Puzzle, PuzzleDependency, ValidationRun
from .schemas import ProjectCreate, ProjectUpdate, PuzzleUpdate

TOKEN = os.environ.get("PUZZLEMINT_TOKEN", "")
EXPORT_ROOT = Path(os.environ.get("PUZZLEMINT_EXPORT_DIR", Path(__file__).resolve().parents[1] / "exports")).resolve()


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


def puzzle_data(puzzle: Puzzle) -> dict:
    return {
        "id": puzzle.id,
        "project_id": puzzle.project_id,
        "type": puzzle.puzzle_type,
        "title": puzzle.title,
        "position": puzzle.position,
        "difficulty": puzzle.difficulty,
        "parameters": puzzle.parameters_json,
        "solution": puzzle.solution_json,
        "hints": [hint.content for hint in puzzle.hints],
        "dependencies": [item.requires_puzzle_id for item in puzzle.dependencies],
        "validation_status": puzzle.validation_status,
    }


def public_puzzle_data(puzzle: Puzzle) -> dict:
    data = puzzle_data(puzzle)
    data["parameters"] = {**data["parameters"]}
    if data["type"] == "logic_grid":
        data["parameters"]["clue_texts"] = [clue_text(clue) for clue in data["parameters"]["clues"]]
    return data


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


@app.post("/api/v1/projects/{project_id}/generate", dependencies=[Depends(authorize)])
def generate_adventure(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    config = project_data(project)
    specs = generate(config)
    project.puzzles.clear()
    db.flush()
    previous = None
    for spec in specs:
        puzzle = Puzzle(
            project=project,
            puzzle_type=spec["type"],
            title=spec["title"],
            position=spec["position"],
            difficulty=spec["difficulty"],
            parameters_json=spec["parameters"],
            solution_json=spec["solution"],
            hints=[Hint(hint_level=index + 1, content=value) for index, value in enumerate(spec["hints"])],
        )
        db.add(puzzle)
        db.flush()
        if previous:
            puzzle.dependencies.append(PuzzleDependency(requires_puzzle_id=previous.id))
        previous = puzzle
    project.status = "generated"
    db.commit()
    return {"project": project_data(project), "puzzles": [public_puzzle_data(p) for p in project.puzzles]}


@app.get("/api/v1/projects/{project_id}/puzzles", dependencies=[Depends(authorize)])
def list_puzzles(project_id: str, db: Session = Depends(get_db)):
    return [public_puzzle_data(puzzle) for puzzle in get_project(project_id, db).puzzles]


@app.post("/api/v1/projects/{project_id}/validate", dependencies=[Depends(authorize)])
def validate_adventure(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    start = perf_counter()
    errors = validate_game([puzzle_data(puzzle) for puzzle in project.puzzles])
    invalid_ids = {error.get("puzzle_id") for error in errors}
    for puzzle in project.puzzles:
        puzzle.validation_status = "invalid" if puzzle.id in invalid_ids else "valid"
    project.status = "validated" if not errors else "validation_failed"
    run = ValidationRun(project_id=project.id, passed=not errors, error_count=len(errors), errors_json=errors, execution_time_ms=round((perf_counter() - start) * 1000))
    db.add(run)
    db.commit()
    return {"passed": not errors, "errors": errors, "execution_time_ms": run.execution_time_ms, "status": project.status}


@app.get("/api/v1/projects/{project_id}/quality", dependencies=[Depends(authorize)])
def quality(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    latest = max(project.validation_runs, key=lambda run: run.created_at) if project.validation_runs else None
    return {"status": project.status, "latest_validation": None if latest is None else {"passed": latest.passed, "errors": latest.errors_json, "execution_time_ms": latest.execution_time_ms}}


@app.post("/api/v1/projects/{project_id}/preview", dependencies=[Depends(authorize)])
def preview(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    return {"project": project_data(project), "puzzles": [public_puzzle_data(p) for p in project.puzzles]}


@app.patch("/api/v1/puzzles/{puzzle_id}", dependencies=[Depends(authorize)])
def update_puzzle(puzzle_id: str, payload: PuzzleUpdate, db: Session = Depends(get_db)):
    puzzle = db.get(Puzzle, puzzle_id)
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    values = payload.model_dump(exclude_unset=True)
    if "title" in values:
        puzzle.title = values["title"]
    if "difficulty" in values:
        puzzle.difficulty = values["difficulty"]
    if "prompt" in values:
        puzzle.parameters_json = {**puzzle.parameters_json, "story": values["prompt"]}
    puzzle.project.status = "generated"
    puzzle.validation_status = "unchecked"
    db.commit()
    return public_puzzle_data(puzzle)


def export_ready(project: Project) -> list[dict]:
    puzzles = [public_puzzle_data(puzzle) for puzzle in project.puzzles]
    if project.status not in {"validated", "exported"} or validate_game(puzzles):
        raise HTTPException(status_code=409, detail="Validate this adventure before exporting")
    return puzzles


def save_export(db: Session, project: Project, name: str, contents: bytes) -> dict:
    directory = (EXPORT_ROOT / project.id).resolve()
    if not directory.is_relative_to(EXPORT_ROOT):
        raise HTTPException(status_code=400, detail="Invalid export path")
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / name
    destination.write_bytes(contents)
    record = Export(project_id=project.id, export_format=destination.suffix.lstrip("."), file_path=str(destination))
    db.add(record)
    db.flush()
    return {"id": record.id, "path": str(destination), "download_url": f"/api/v1/exports/{record.id}/download"}


@app.post("/api/v1/projects/{project_id}/export/html", dependencies=[Depends(authorize)])
def export_html(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    puzzles = export_ready(project)
    result = save_export(db, project, "adventure.html", create_html(project_data(project), puzzles).encode("utf-8"))
    project.status = "exported"
    db.commit()
    return result


@app.post("/api/v1/projects/{project_id}/export/pdf", dependencies=[Depends(authorize)])
def export_pdf(project_id: str, db: Session = Depends(get_db)):
    project = get_project(project_id, db)
    puzzles = export_ready(project)
    player, organizer = create_pdf(project_data(project), puzzles)
    handout = save_export(db, project, "player-handout.pdf", player)
    answer_key = save_export(db, project, "organizer-answer-key.pdf", organizer)
    project.status = "exported"
    db.commit()
    return {"handout": handout, "answer_key": answer_key}


@app.get("/api/v1/exports/{export_id}/download", dependencies=[Depends(authorize)])
def download_export(export_id: str, db: Session = Depends(get_db)):
    record = db.get(Export, export_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Export not found")
    path = Path(record.file_path).resolve()
    if not path.is_relative_to(EXPORT_ROOT) or not path.is_file():
        raise HTTPException(status_code=404, detail="Export file is unavailable")
    return FileResponse(path, filename=path.name)
