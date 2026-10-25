# PuzzleMint

PuzzleMint is a local-first creator for personalized puzzle adventures. The Flutter creator and Python API are developed in runnable increments. The backend persists projects, generates four puzzle families, independently validates them, and exports printable and offline games. Creator integration is being built next.

## Requirements

- Flutter 3.41.2 or newer compatible stable version
- Python 3.12 or newer
- Windows for the primary desktop target

All dependencies are free. The core product does not require a cloud account or paid API.

## Run locally

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python -m alembic -c backend\alembic.ini upgrade head
.\.venv\Scripts\python backend\run.py
```

The backend prints a new session token on startup and binds to `127.0.0.1:8765`. Send the token in `Authorization: Bearer <token>` for all project endpoints. It has no CORS origins enabled. The token is held in memory and is never committed to source control. Keep the API terminal open while using the creator.

In another terminal:

```powershell
flutter pub get
flutter run -d windows
```

The API uses `backend/puzzlemint.db` by default. Set `PUZZLEMINT_DATABASE_URL` to another SQLite URL when needed. Run Alembic migrations before starting a new database.

## Verify

```powershell
python -m pytest backend\tests -q
flutter test
flutter analyze
```

## Current architecture

- Flutter desktop creator, with Android and web project scaffolds for later adaptation.
- FastAPI versioned local API with Pydantic input validation and a per-run bearer token.
- SQLAlchemy relational models, SQLite foreign keys, and Alembic migration.
- Separate project and personalization records; puzzle, dependency, hint, validation, and export tables are ready for the next increments.
- Deterministic Caesar ciphers, three-digit locks, small logic grids, and exact-order timelines. Lock combinations, logic assignments, and timeline orders are enumerated independently to check uniqueness. A chain of dependencies connects the stages.
- PDF player handout and separate organizer answer key; self-contained HTML player with hints, answer checks, stage unlocks, and browser-local progress where available. Export text is encoded into JSON and rendered through safe DOM text APIs. Offline answers can be inspected by a technically skilled player.

Project data stays on the local machine. There is no telemetry. A local user with access to the computer can inspect the database, so this is not a security boundary against that user.
