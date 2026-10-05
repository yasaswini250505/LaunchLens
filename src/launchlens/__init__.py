from typing import Final

GROQ_BASE_URL: Final[str] = "https://api.groq.com/openai/v1"
DEFAULT_MODEL: Final[str] = "llama-3.1-8b-instant"
DEFAULT_TIMEOUT: Final[float] = 60.0
DEFAULT_MAX_FILE_CHARS: Final[int] = 25_000
SUPPORTED_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go",
".rs",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".rb", ".swift", ".scala",
    ".md", ".markdown", ".rst", ".txt", ".csv", ".json", ".jsonl",
".ndjson",
    ".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".properties",
".env.example",
    ".sql", ".graphql", ".gql", ".proto", ".sh", ".bash", ".ps1", ".bat",
".cmd",
    ".lock", ".xml", ".html", ".css", ".scss", ".vue", ".svelte",
})
IMPORTANT_FILENAMES: Final[frozenset[str]] = frozenset({
    "Dockerfile", "dockerfile", ".dockerignore", "Makefile", "makefile",
"Procfile",
    "requirements.txt", "requirements-dev.txt", "package.json", 
"package-lock.json",
    "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock", "Pipfile",
"Pipfile.lock",
    "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "pom.xml",
"build.gradle",
    "compose.yaml", "compose.yml", "docker-compose.yml",
"docker-compose.yaml",
    ".gitignore", "LICENSE", "CHANGELOG.md", "README", "README.md",
})
SENSITIVE_BASENAMES: Final[frozenset[str]] = frozenset({
    ".env", ".env.local", ".env.production", "credentials.json",
"secrets.json",
    "id_rsa", "id_ed25519", "server.key", "server.pem",
})
IGNORED_PARTS: Final[frozenset[str]] = frozenset({".git", ".venv", "venv",
"node_modules", "__pycache__", "dist", "build", ".pytest_cache",
"coverage", ".mypy_cache"})

class LaunchLensError(Exception):
    """Expected error displayed without a traceback."""

class SourceError(LaunchLensError):
    pass

class ConfigurationError(LaunchLensError):
    pass

class APIError(LaunchLensError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code

class ResponseError(LaunchLensError):
    pass