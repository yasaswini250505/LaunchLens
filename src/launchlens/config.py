from __future__ import annotations

import json
import os
import platform
from pathlib import Path

from dotenv import load_dotenv

from launchlens.constants import DEFAULT_MAX_FILE_CHARS, DEFAULT_MODEL, DEFAULT_TIMEOUT
from launchlens.errors import ConfigurationError
from launchlens.schemas import AppConfig

class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        load_dotenv()
        self.path = path or self.default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def default_path() -> Path:
        system = platform.system()
        if system == "Windows":
            root = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif system == "Darwin":
            root = Path.home() / "Library" / "Application Support"
        else:
            root = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        return root / "launchlens" / "config.json"
    
    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig(
                model=os.getenv("LAUNCHLENS_MODEL", DEFAULT_MODEL),

timeout_seconds=float(os.getenv("LAUNCHLENS_TIMEOUT_SECONDS", DEFAULT_TIMEOUT)),
                max_file_chars=int(os.getenv("LAUNCHLENS_MAX_FILE_CHARS",
DEFAULT_MAX_FILE_CHARS)),
            )
        try:
            return AppConfig.model_validate_json(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise ConfigurationError(f"cannot read config: {error}") from error

    def save(self, config: AppConfig) -> None:
        try:
            self.path.write_text(config.model_dump_json(indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            raise ConfigurationError(f"cannot save config: {error}") from error
        
    def api_key(self) -> str | None:
        return self.load().api_key or os.getenv("GROQ_API_KEY")

    def github_token(self) -> str | None:
        return self.load().github_token or os.getenv("GITHUB_TOKEN")