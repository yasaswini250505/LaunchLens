from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean, median
from time import perf_counter
from typing import Callable

from launchlens.client import GroqClient


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    model: str
    rounds: int
    successful: int
    failed: int
    average_ms: float
    median_ms: float
    p95_ms: float
    samples: tuple[float, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
    
class BenchmarkRunner:
    def __init__(self, factory: Callable[[str], GroqClient]) -> None:
        self.factory = factory

    def run(self, models: list[str], prompt: str, rounds: int) -> list[BenchmarkResult]:
        if not models or rounds < 1:
            raise ValueError("models and positive rounds are required")
        results: list[BenchmarkResult] = []
        for model in models:
            samples: list[float] = []
            failures = 0
            for _ in range(rounds):
                started = perf_counter()
                try:
                    with self.factory(model) as client:
                        client.complete(prompt)
                    samples.append((perf_counter() - started) * 1000)
                except Exception:
                    failures += 1
            ordered = sorted(samples)
            p95 = ordered[min(len(ordered) - 1, max(0, int(len(ordered) *
                        0.95) - 1))] if ordered else 0.0
            results.append(BenchmarkResult(model, rounds, len(samples),
                            failures, round(mean(samples), 2) if samples else 0.0,
                            round(median(samples), 2) if samples else 0.0, round(p95, 2),
                            tuple(round(item, 2) for item in samples)))
        return results