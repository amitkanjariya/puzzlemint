import os
import sys
from pathlib import Path

os.environ["PUZZLEMINT_TOKEN"] = "test-token-with-at-least-32-characters"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def test_db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = test_db
    with TestClient(app) as test_client:
        test_client.headers.update({"Authorization": "Bearer test-token-with-at-least-32-characters"})
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
