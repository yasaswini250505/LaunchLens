from __future__ import annotations

from pathlib import Path
from time import perf_counter
from urllib import response
from urllib import response
from weakref import ref
from xml.parsers.expat import model
from xmlrpc import client

from launchlens.benchmark import BenchmarkResult, BenchmarkRunner
from launchlens.client import GroqClient
from launchlens.config import ConfigStore
from launchlens.errors import ConfigurationError
from launchlens.prompts import ArtifactKind, build_prompt
from launchlens.schemas import GeneratedArtifact
from launchlens.scanner import ProjectScanner
from launchlens.sources import SourceResolver


class LaunchLensService:
    def __init__(self, config_store: ConfigStore | None = None) -> None:
        self.config_store = config_store or ConfigStore()
        self.config = self.config_store.load()

    def resolve_and_scan(self, source: str, ref: str | None = None):
        resolved = SourceResolver(self.config_store.github_token()).resolve(source, ref)
        try:
            return resolved, ProjectScanner(self.config.max_file_chars).scan(resolved.root)
        except Exception:
            resolved.cleanup()
            raise

    def _client(self, model: str | None = None) -> GroqClient:
        key = self.config_store.api_key()
        if not key:
            raise ConfigurationError("Set GROQ_API_KEY or run launchlens set-key.")

        return GroqClient(key, model or self.config.model, self.config.timeout_seconds)

    def generate(self, source: str, kind: ArtifactKind, model: str | None =
None, ref: str | None = None) -> GeneratedArtifact:
        resolved, snapshot = self.resolve_and_scan(source, ref)
        started = perf_counter()
        try:
            with self._client(model) as client:
                response = client.complete(build_prompt(kind, snapshot.context))
            return GeneratedArtifact(kind, source, response.model,
response.text, len(snapshot.files), snapshot.total_lines, (perf_counter() -
started) * 1000)
        finally:
            resolved.cleanup()

    def stream_generate(self, source: str, kind: ArtifactKind,
on_token=None, model: str | None = None, ref: str | None = None) -> GeneratedArtifact:
        resolved, snapshot = self.resolve_and_scan(source, ref)
        started = perf_counter()
        try:
            with self._client(model) as client:
                text = client.stream(build_prompt(kind, snapshot.context), on_token=on_token)
            return GeneratedArtifact(kind, source, model or 
self.config.model, text, len(snapshot.files), snapshot.total_lines,
(perf_counter() - started) * 1000)
        finally:
            resolved.cleanup()

    def benchmark(self, source: str, kind: ArtifactKind, models: list[str],
    rounds: int, ref: str | None = None) -> list[BenchmarkResult]:
        resolved, snapshot = self.resolve_and_scan(source, ref)
        try:
            key = self.config_store.api_key()
            if not key:
                raise ConfigurationError("Set GROQ_API_KEY before benchmarking.")
            prompt = build_prompt(kind, snapshot.context)
            return BenchmarkRunner(lambda model: GroqClient(key, model,
    self.config.timeout_seconds)).run(models, prompt, rounds)
        finally:
            resolved.cleanup()