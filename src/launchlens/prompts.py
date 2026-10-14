from typing import Literal

ArtifactKind = Literal["readme", "pitch", "resume", "interview", "roadmap", "architecture"]

INSTRUCTIONS: dict[ArtifactKind, str] = {
    "readme": "Write a polished README with value proposition, features, architecture, setup, usage, and roadmap. Do not invent dependencies.",
    "pitch": "Write a compelling 60-second spoken project pitch for an internship interview. Explain problem, solution, technical decisions, and impact.",
    "resume": "Write four concise resume bullets using strong engineering verbs. Mention concrete technologies only when visible in the snapshot.",
    "interview": "Create ten likely technical interview questions and model answers based only on the visible project.",
    "roadmap": "Create a prioritized roadmap with quick wins, reliability work, security work, and ambitious next features.",
    "architecture": "Explain the architecture, data flow, important modules, concurrency choices, and trade-offs in an interview-friendly format.",
}


def build_prompt(kind: ArtifactKind, context: str) -> str:
    return (
        "You are LaunchLens, a senior engineer and technical storyteller.\n"
        "Never claim that a file, dependency, metric, or feature exists unless it appears in the project snapshot.\n"
        f"Task: {INSTRUCTIONS[kind]}\n\nProject snapshot:\n{context}"
)