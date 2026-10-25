from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Theme = Literal["museum", "agent", "library"]
Difficulty = Literal["easy", "medium", "hard"]


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    theme: Theme = "museum"
    occasion: str = Field(default="Birthday", min_length=2, max_length=40)
    difficulty: Difficulty = "medium"
    duration_minutes: int = Field(default=30, ge=10, le=120)
    puzzle_count: int = Field(default=6, ge=4, le=8)
    random_seed: int = Field(default=42, ge=0, le=2147483647)
    player_alias: str = Field(default="Explorer", min_length=1, max_length=60)
    final_message: str = Field(default="What an adventure!", min_length=1, max_length=500)

    @field_validator("title", "occasion", "player_alias", "final_message")
    @classmethod
    def no_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    theme: Theme | None = None
    occasion: str | None = Field(default=None, min_length=2, max_length=40)
    difficulty: Difficulty | None = None
    duration_minutes: int | None = Field(default=None, ge=10, le=120)
    puzzle_count: int | None = Field(default=None, ge=4, le=8)
    random_seed: int | None = Field(default=None, ge=0, le=2147483647)
    player_alias: str | None = Field(default=None, min_length=1, max_length=60)
    final_message: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def no_null_or_blank(self):
        for name in self.model_fields_set:
            value = getattr(self, name)
            if value is None or isinstance(value, str) and not value.strip():
                raise ValueError(f"{name} must not be empty")
        return self


class PuzzleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    difficulty: Difficulty | None = None
    prompt: str | None = Field(default=None, min_length=5, max_length=1000)

    @model_validator(mode="after")
    def no_null_or_blank(self):
        for name in self.model_fields_set:
            value = getattr(self, name)
            if value is None or isinstance(value, str) and not value.strip():
                raise ValueError(f"{name} must not be empty")
        return self
