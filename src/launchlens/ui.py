from __future__ import annotations

import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from launchlens.schemas import GeneratedArtifact

console = Console()


def emit_json(value: object) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    elif isinstance(value, list):
        value = [item.to_dict() if hasattr(item, "to_dict") else item for item in value]
    print(json.dumps(value, indent=2, default=str))


def show_artifact(artifact: GeneratedArtifact) -> None:
    console.print(
        Panel(
            artifact.content, 
            title=f"{artifact.artifact_type.upper()} — {artifact.source}",
            border_style="cyan"))
    console.print(
        f"[dim]Files: {artifact.files_analyzed} | "
        f"Lines: {artifact.lines_analyzed} | "
        f"Time: {artifact.elapsed_ms:.2f} ms[/dim]")


def show_benchmark(results) -> None:
    table = Table(title="LaunchLens model benchmark")
    for column in ("Model", "Success", "Average", "Median", "P95"):
        table.add_column(column)
    for item in results:
        table.add_row(
            item.model, 
            f"{item.successful}/{item.rounds}", 
            f" {item.average_ms:.2f} ms", 
            f"{item.median_ms:.2f} ms", 
            f"{item.p95_ms:.2f} ms")
        
    console.print(table)