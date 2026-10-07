from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from launchlens.constants import DEFAULT_MAX_FILE_CHARS, DEFAULT_MODEL, DEFAULT_TIMEOUT


class ProjectFile(BaseModel):
    path: str = Field(min_length=1)
    extension: str
    lines: int = Field(ge=0)
    size_bytes: int = Field(ge=0)
    content: str = Field(min_length=1)
    truncated: bool = False

class ProjectSnapshot(BaseModel):
    source: str
    project_name: str
    files: list[ProjectFile] = Field(min_length=1, max_length=400)
    languages: dict[str, int]
    total_lines: int = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda:
datetime.now(timezone.utc))
    
    @property
    def context(self) -> str:
        language_text = ", ".join(f"{key}: {value}" for key, value in self.languages.items())
        sections = [f"Project: {self.project_name}\nLanguages: {language_text}\nTotal lines: {self.total_lines}"]
        sections.extend(f"\n--- {item.path} ---\n{item.content}" for item in self.files)
        return "".join(sections)