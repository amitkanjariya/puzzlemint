from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def now():
    return datetime.now(timezone.utc)


def uid():
    return str(uuid4())


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(120))
    theme: Mapped[str] = mapped_column(String(40))
    occasion: Mapped[str] = mapped_column(String(40))
    difficulty: Mapped[str] = mapped_column(String(10))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    puzzle_count: Mapped[int] = mapped_column(Integer)
    random_seed: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    personalization: Mapped["Personalization"] = relationship(back_populates="project", cascade="all, delete-orphan", uselist=False)
    puzzles: Mapped[list["Puzzle"]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="Puzzle.position")
    validation_runs: Mapped[list["ValidationRun"]] = relationship(cascade="all, delete-orphan")
    exports: Mapped[list["Export"]] = relationship(cascade="all, delete-orphan")


Index("ix_projects_updated", Project.updated_at)
Index("ix_projects_theme_status", Project.theme, Project.status)


class Personalization(Base):
    __tablename__ = "personalizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True)
    player_alias: Mapped[str] = mapped_column(String(60), default="Explorer")
    custom_facts_json: Mapped[dict] = mapped_column(JSON, default=dict)
    final_message: Mapped[str] = mapped_column(String(500), default="What an adventure!")
    project: Mapped[Project] = relationship(back_populates="personalization")


class Puzzle(Base):
    __tablename__ = "puzzles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    puzzle_type: Mapped[str] = mapped_column(String(24))
    title: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(10))
    parameters_json: Mapped[dict] = mapped_column(JSON)
    solution_json: Mapped[dict] = mapped_column(JSON)
    validation_status: Mapped[str] = mapped_column(String(24), default="unchecked")
    project: Mapped[Project] = relationship(back_populates="puzzles")
    dependencies: Mapped[list["PuzzleDependency"]] = relationship(foreign_keys="PuzzleDependency.puzzle_id", cascade="all, delete-orphan")
    hints: Mapped[list["Hint"]] = relationship(cascade="all, delete-orphan", order_by="Hint.hint_level")
    __table_args__ = (UniqueConstraint("project_id", "position"),)


class PuzzleDependency(Base):
    __tablename__ = "puzzle_dependencies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    puzzle_id: Mapped[str] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"), index=True)
    requires_puzzle_id: Mapped[str] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"))
    __table_args__ = (UniqueConstraint("puzzle_id", "requires_puzzle_id"),)


class Hint(Base):
    __tablename__ = "hints"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    puzzle_id: Mapped[str] = mapped_column(ForeignKey("puzzles.id", ondelete="CASCADE"), index=True)
    hint_level: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(String(500))
    __table_args__ = (UniqueConstraint("puzzle_id", "hint_level"),)


class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    passed: Mapped[bool] = mapped_column(Boolean)
    error_count: Mapped[int] = mapped_column(Integer)
    errors_json: Mapped[list] = mapped_column(JSON)
    execution_time_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Export(Base):
    __tablename__ = "exports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    export_format: Mapped[str] = mapped_column(String(12))
    file_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
