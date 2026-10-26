from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from revuer import cli
from revuer.config import GlobalConfig, ServerConfig, resolve_server


def test_resolve_server_defaults() -> None:
    assert resolve_server(GlobalConfig()) == ServerConfig(host="127.0.0.1", port=7420)


def test_resolve_server_flags_win_over_file() -> None:
    config = GlobalConfig(server=ServerConfig(host="0.0.0.0", port=8000))
    assert resolve_server(config, port=9000) == ServerConfig(host="0.0.0.0", port=9000)
    assert resolve_server(config, host="::1") == ServerConfig(host="::1", port=8000)


@pytest.fixture
def served(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    calls: dict[str, Any] = {}

    def fake_run(app: object, host: str, port: int) -> None:
        calls.update(app=app, host=host, port=port)

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    return calls


def test_serve_uses_defaults(served: dict[str, Any]) -> None:
    result = CliRunner().invoke(cli.app, ["serve"])
    assert result.exit_code == 0, result.output
    assert (served["host"], served["port"]) == ("127.0.0.1", 7420)


def test_serve_flags_override_global_file(
    config_home: Path, served: dict[str, Any]
) -> None:
    path = config_home / "revuer" / "config.toml"
    path.parent.mkdir(parents=True)
    path.write_text('[server]\nhost = "0.0.0.0"\nport = 8000\n')
    result = CliRunner().invoke(cli.app, ["serve", "--port", "9000"])
    assert result.exit_code == 0, result.output
    assert (served["host"], served["port"]) == ("0.0.0.0", 9000)


def test_serve_reports_invalid_config(config_home: Path) -> None:
    path = config_home / "revuer" / "config.toml"
    path.parent.mkdir(parents=True)
    path.write_text('[server]\nport = "x"\n')
    result = CliRunner().invoke(cli.app, ["serve"])
    assert result.exit_code == 1
    assert str(path) in result.output
    assert "server.port" in result.output


def test_serve_reports_unreadable_config(config_home: Path) -> None:
    path = config_home / "revuer" / "config.toml"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"\xff")
    result = CliRunner().invoke(cli.app, ["serve"])
    assert result.exit_code == 1
    assert str(path) in result.output
