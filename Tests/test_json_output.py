import json

from launchlens.schemas import GeneratedArtifact

from launchlens.ui import emit_json


def test_json_output_is_parseable(capsys) -> None:
    emit_json(GeneratedArtifact(artifact_type = "pitch", 
                                source = "demo",
                                model = "test", 
                                content = "hello", 
                                files_analyzed = 1, 
                                lines_analyzed = 2, 
                                elapsed_ms = 4))
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact_type"] == "pitch"
    assert payload["files_analyzed"] == 1