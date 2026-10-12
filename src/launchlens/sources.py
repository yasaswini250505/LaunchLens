from __future__ import annotations

from dbm import error
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from launchlens.errors import SourceError

GITHUB_URL = re.compile(r"^https://github\.com/([^/]+)/([^/#]+?)(?:\.git)?(?:#(.+))?/?$")


@dataclass
class ResolvedSource:
    root: Path
    display_name: str
    temporary: bool = False

    def cleanup(self) -> None:
        if self.temporary:
            shutil.rmtree(self.root, ignore_errors=True)

class SourceResolver:
    """Resolve a local directory or clone a public/private GitHub repository."""

    def __init__(self, github_token: str | None = None) -> None:
        self.github_token = github_token

    def resolve(self, source: str, ref: str | None = None) -> ResolvedSource:
        local = Path(source).expanduser()
        if local.exists():
            if not local.is_dir():
                raise SourceError("local source must be a directory")
            return ResolvedSource(local.resolve(), local.name, False)
        match = GITHUB_URL.match(source.strip())
        if not match:
            raise SourceError("source must be an existing folder or an https://github.com URL")
        owner, repository, url_ref = match.groups()
        selected_ref = ref or url_ref
        temporary = Path(tempfile.mkdtemp(prefix="launchlens-"))
        clone_url = f"https://github.com/{owner}/{repository}.git"
        if self.github_token:
            clone_url = f"https://x-access-token:{self.github_token}@github.com/{owner}/{repository}.git"
        command = ["git", "clone", "--depth", "1"]
        if selected_ref:
            command += ["--branch", selected_ref]
        command += [clone_url, str(temporary)]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            shutil.rmtree(temporary, ignore_errors=True)
            raise SourceError(f"git clone failed: {error}") from error
        if completed.returncode != 0:
            shutil.rmtree(temporary, ignore_errors=True)
            raise SourceError(completed.stderr.strip() or "git clone failed")
        return ResolvedSource(temporary, repository, True)