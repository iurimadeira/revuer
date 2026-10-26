from pathlib import Path

import pytest

from revuer.config import (
    ConfigError,
    global_config_path,
    load_global_config,
    load_project_config,
)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_defaults_without_config_file() -> None:
    config = load_global_config()
    assert config.server.host == "127.0.0.1"
    assert config.server.port == 7420
    assert config.repos == []


def test_global_path_uses_xdg_config_home(config_home: Path) -> None:
    assert global_config_path() == config_home / "revuer" / "config.toml"


def test_global_path_falls_back_to_home_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert global_config_path() == tmp_path / ".config" / "revuer" / "config.toml"


def test_loads_global_file(config_home: Path, tmp_path: Path) -> None:
    write(
        config_home / "revuer" / "config.toml",
        f'repos = ["{tmp_path}/a"]\n[server]\nhost = "0.0.0.0"\nport = 8000\n',
    )
    config = load_global_config()
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 8000
    assert config.repos == [tmp_path / "a"]


def test_repos_expand_home_and_resolve(
    config_home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    write(config_home / "revuer" / "config.toml", 'repos = ["~/code/../app"]\n')
    assert load_global_config().repos == [tmp_path / "app"]


@pytest.mark.parametrize(
    ("text", "key"),
    [
        ('[server]\nport = "x"\n', "server.port"),
        ("[server]\nport = 70000\n", "server.port"),
        ("[server]\ncolour = 1\n", "server.colour"),
        ("unknown = 1\n", "unknown"),
        ("repos = [1]\n", "repos.0"),
    ],
)
def test_invalid_global_file_names_file_and_key(
    config_home: Path, text: str, key: str
) -> None:
    path = write(config_home / "revuer" / "config.toml", text)
    with pytest.raises(ConfigError) as error:
        load_global_config()
    assert str(path) in str(error.value)
    assert key in str(error.value)


def test_malformed_toml_names_file(config_home: Path) -> None:
    path = write(config_home / "revuer" / "config.toml", "[server\n")
    with pytest.raises(ConfigError, match="invalid TOML") as error:
        load_global_config()
    assert str(path) in str(error.value)


def test_project_defaults_without_file(tmp_path: Path) -> None:
    assert load_project_config(tmp_path).branch.default_parent is None


def test_project_default_parent(tmp_path: Path) -> None:
    write(tmp_path / ".revuer.toml", '[branch]\ndefault_parent = "develop"\n')
    assert load_project_config(tmp_path).branch.default_parent == "develop"


def test_project_server_table_is_ignored_with_warning(tmp_path: Path) -> None:
    path = write(
        tmp_path / ".revuer.toml",
        '[server]\nport = 1\n[branch]\ndefault_parent = "main"\n',
    )
    with pytest.warns(UserWarning, match=r"\[server\]") as record:
        config = load_project_config(tmp_path)
    assert str(path) in str(record[0].message)
    assert config.branch.default_parent == "main"


@pytest.mark.parametrize(
    ("text", "key"),
    [
        ("[branch]\ndefault_parent = 1\n", "branch.default_parent"),
        ('[branch]\nparent = "main"\n', "branch.parent"),
        ('repos = ["a"]\n', "repos"),
    ],
)
def test_invalid_project_file_names_file_and_key(
    tmp_path: Path, text: str, key: str
) -> None:
    path = write(tmp_path / ".revuer.toml", text)
    with pytest.raises(ConfigError) as error:
        load_project_config(tmp_path)
    assert str(path) in str(error.value)
    assert key in str(error.value)
