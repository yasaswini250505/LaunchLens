from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from os import error, path
from pathlib import Path

from launchlens.constants import IGNORED_PARTS, IMPORTANT_FILENAMES, SENSITIVE_BASENAMES, SUPPORTED_EXTENSIONS
from launchlens.errors import SourceError
from launchlens.schemas import ProjectFile, ProjectSnapshot


class ProjectScanner:
    """Read useful project files while excluding generated and sensitive material."""

    def __init__(self, max_file_chars: int = 25_000) -> None:
        self.max_file_chars = max_file_chars

    @staticmethod
    def _is_sensitive(path: Path) -> bool:
        name = path.name.lower()
        if name in {item.lower() for item in SENSITIVE_BASENAMES}:
            return True
        return name.startswith(".env") and name != ".env.example"
    
    @staticmethod
    def _is_candidate(path: Path) -> bool:
        return path.name in IMPORTANT_FILENAMES or path.suffix.lower() in SUPPORTED_EXTENSIONS

    def _read(self, path: Path, root: Path) -> ProjectFile:
        try:
            original = path.read_text(encoding="utf-8", errors="replace")
            size_bytes = path.stat().st_size
        except OSError as error:
            raise SourceError(f"cannot read {path}: {error}") from error
        content = original[: self.max_file_chars] or " "
        return ProjectFile(
            path=path.relative_to(root).as_posix(),
            extension=path.suffix.lower() or "[no extension]",
            lines=original.count("\n") + (1 if original else 0),
            size_bytes=size_bytes,
            content=content,
            truncated=len(content) < len(original),
        )

    def scan(self, root: Path) -> ProjectSnapshot:
        if not root.exists() or not root.is_dir():
            raise SourceError(f"not a directory: {root}")
        paths = [
            path for path in root.rglob("*")
            if path.is_file()
            and self._is_candidate(path)
            and not self._is_sensitive(path)
            and not any(part in IGNORED_PARTS for part in path.parts)
        ]
        if not paths:
            raise SourceError("no supported project files found")
        files: list[ProjectFile] = []
        with ThreadPoolExecutor(max_workers=min(8, len(paths)),
                                thread_name_prefix="lens-scan") as pool:
            futures = {pool.submit(self._read, path, root): path for path in paths}
            for future in as_completed(futures):
                files.append(future.result())
        files.sort(key=lambda item: item.path)
        languages: dict[str, int] = {}
        for item in files:
            languages[item.extension] = languages.get(item.extension, 0) + 1
        return ProjectSnapshot(
            source=str(root),
            project_name=root.name,
            files=files,
            languages=languages,
            total_lines=sum(item.lines for item in files),
        )