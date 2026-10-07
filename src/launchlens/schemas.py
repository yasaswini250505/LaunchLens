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

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=100_000)

    @field_validator("content")
    @classmethod
    def clean_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("content cannot be blank")
        return value
    
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(default=DEFAULT_MODEL, min_length=2)
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_completion_tokens: int = Field(default=1200, gt=0, le=8192)
    stream: bool = False

class ChoiceMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    role: str
    content: str

class Choice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    index: int = 0
    message: ChoiceMessage
    finish_reason: str | None = None

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    model: str
    choices: list[Choice] = Field(min_length=1)
    @property
    def text(self) -> str:
        return self.choices[0].message.content.strip()
    
class AppConfig(BaseModel):
    api_key: str | None = None
    github_token: str | None = None
    model: str = DEFAULT_MODEL
    timeout_seconds: float = Field(default=DEFAULT_TIMEOUT, gt=0, le=300)
    max_file_chars: int = Field(default=25_000, ge=500, le=100_000)

class GeneratedArtifact(BaseModel):
    artifact_type: str
    source: str
    model: str
    content: str
    files_analyzed: int = Field(ge=0)
    lines_analyzed: int = Field(ge=0)
    elapsed_ms: float = Field(ge=0)
    created_at: datetime = Field(default_factory=lambda:
datetime.now(timezone.utc))