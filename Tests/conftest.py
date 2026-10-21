from pathlib import Path

import pytest

from launchlens.config import ConfigStore
from launchlens.schemas import AppConfig
from launchlens.service import LaunchLensService


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "main.py").write_text("def main():\n return 'hello'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    return tmp_path

@pytest.fixture
def config_store(tmp_path: Path) -> ConfigStore:
    store = ConfigStore(tmp_path / "config.json")
    store.save(AppConfig(api_key="test-key", model="test-model"))
    return store

@pytest.fixture
def service(config_store: ConfigStore) -> LaunchLensService:
    return LaunchLensService(config_store)