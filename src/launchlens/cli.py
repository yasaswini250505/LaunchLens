from __future__ import annotations

from pathlib import Path
from xml.parsers.expat import model

import typer
from typer import models

from launchlens.errors import LaunchLensError
from launchlens.service import LaunchLensService
from launchlens.ui import console, emit_json, show_artifact, show_benchmark

app = typer.Typer(
    name = "launchlens", 
    help = "Turn a project into a portfolio story.", 
    no_args_is_help = True)


@app.callback()
def root(
    ctx: typer.Context, json_output: bool = typer.Option(False, "-- json", help="Emit one JSON document.")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def is_json(ctx: typer.Context) -> bool:
    return bool(ctx.obj and ctx.obj.get("json"))


def handle_error(ctx: typer.Context, error: Exception) -> None:
    if is_json(ctx):
        emit_json({"error": str(error), "type": type(error).__name__})
    else:
        console.print(f"[bold red]Error:[/bold red] {error}")
    raise typer.Exit(code=1) from error


@app.command()
def inspect(ctx: typer.Context, source: str = typer.Argument(...), ref: str
| None = typer.Option(None, "--ref")) -> None:
    """Inspect a local folder or GitHub repository without calling Groq."""
    try:
        resolved, snapshot = LaunchLensService().resolve_and_scan(source, ref)
        try:
            payload = {"source": source, 
                       "project_name" : snapshot.project_name, 
                       "files" : len(snapshot.files), 
                       "lines" : snapshot.total_lines, 
                       "languages" : snapshot.languages, 
                       "file_paths" : [item.path for item in snapshot.files], 
                       "truncated_files" : [item.path for item in snapshot.files if item.truncated]}
            emit_json(payload) if is_json(ctx) else console.print(payload)
        finally:
            resolved.cleanup()
    except LaunchLensError as error:
        handle_error(ctx, error)


@app.command()
def generate(
    ctx: typer.Context,
    kind: str = typer.Argument(..., help="readme, pitch, resume, interview, roadmap, or architecture"),
    source: str = typer.Argument(...),
    ref: str | None = typer.Option(None, "--ref"),
    model: str | None = typer.Option(None, "--model", "-m"),
    stream: bool = typer.Option(False, "--stream/--no-stream"),
) -> None:
    """Generate a portfolio artifact from a local folder or GitHub URL."""
    if kind not in {"readme", "pitch", "resume", "interview", "roadmap", "architecture"}:
        raise typer.BadParameter("unsupported artifact kind")
    try:
        service = LaunchLensService()
        if stream:
            if is_json(ctx):
                artifact = service.stream_generate(source, kind, model=model, ref=ref)
            else:
                console.print(f"[bold cyan]Streaming {kind} for {source} [/bold cyan]\n")
                print("LaunchLens: ", end="", flush=True)
                artifact = service.stream_generate(source, kind,
                on_token=lambda token: print(token, end="", flush=True), model=model, ref=ref)

                print("\n")
        else:
            artifact = service.generate(source, kind, model=model, ref=ref)
        emit_json(artifact) if is_json(ctx) else (None if stream else show_artifact(artifact))
    except LaunchLensError as error:
        handle_error(ctx, error)

@app.command()
def benchmark(
    ctx: typer.Context,
    source: str = typer.Argument(...),
    kind: str = typer.Option("pitch", "--kind"),
    models: list[str] = typer.Option(..., "--model", "-m"),
    rounds: int = typer.Option(3, "--rounds", min=1, max=20),
) -> None:
    """Compare model latency for the same project artifact prompt."""
    try:
        results = LaunchLensService().benchmark(source, kind, models,
        rounds)
        emit_json(results) if is_json(ctx) else show_benchmark(results)
    except (LaunchLensError, ValueError) as error:
        handle_error(ctx, error)


@app.command("set-key")
def set_key(api_key: str | None = typer.Option(None, prompt=True,
hide_input=True)) -> None:
    if not api_key:
        raise typer.BadParameter("API key is required")
    service = LaunchLensService()
    service.config.api_key = api_key.strip()
    service.config_store.save(service.config)
    console.print("[green]Groq key saved locally.[/green]")


@app.command("set-model")
def set_model(model: str = typer.Argument(...)) -> None:
    service = LaunchLensService()
    service.config.model = model.strip()
    service.config_store.save(service.config)
    console.print(f"[green]Default model set to {model}.[/green]")

def main() -> None:
    app()


if __name__ == "__main__":
    main()