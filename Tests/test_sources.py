from launchlens.sources import SourceResolver


def test_local_folder_is_resolved(project) -> None:
    resolved = SourceResolver().resolve(str(project))
    assert resolved.root == project.resolve()
    assert resolved.temporary is False
    resolved.cleanup()