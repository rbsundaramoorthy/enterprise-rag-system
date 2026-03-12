from _pytest.monkeypatch import MonkeyPatch
from enterprise_rag_core.settings import Settings


def test_settings_reads_environment_values(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ENTERPRISE_RAG_APP_NAME", "test-api")
    monkeypatch.setenv("ENTERPRISE_RAG_API_PORT", "9000")

    settings = Settings()

    assert settings.app_name == "test-api"
    assert settings.api_port == 9000
