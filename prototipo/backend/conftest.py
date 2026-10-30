import pytest

from integrations.ports import reset_ports


@pytest.fixture(autouse=True)
def _stub_generation(settings, tmp_path, monkeypatch):
    """Every test runs offline against the stub adapter, with its own MEDIA_ROOT."""
    settings.GENERATION_ADAPTER = "integrations.adapters.runware_stub.StubGenerationAdapter"
    settings.MEDIA_ROOT = tmp_path / "media"
    monkeypatch.setattr("integrations.adapters.runware_stub.time.sleep", lambda _: None)
    reset_ports()
    yield
    reset_ports()
