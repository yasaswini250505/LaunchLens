from launchlens.scanner import ProjectScanner


def test_scanner_counts_files_and_languages(project) -> None:
    snapshot = ProjectScanner().scan(project)
    assert snapshot.project_name == project.name
    assert len(snapshot.files) == 2
    assert snapshot.languages[".py"] == 1
    assert all(not item.path.startswith("/") for item in snapshot.files)