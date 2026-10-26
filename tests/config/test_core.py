from pathlib import Path

import pytest

from revuer.config.core import (
    ConfigError,
    GlobalConfig,
    ServerConfig,
    anchor_repos,
    parse_global_config,
    parse_project_config,
    resolve_server,
)

GLOBAL = Path("/etc/xdg/revuer/config.toml")
PROJECT = Path("/repo/.revuer.toml")
HOME = Path("/home/user")


def test_empty_text_gives_defaults() -> None:
    assert parse_global_config("", GLOBAL, HOME) == GlobalConfig()


def test_parses_global_text() -> None:
    config = parse_global_config(
        '[server]\nhost = "0.0.0.0"\nport = 8000\n', GLOBAL, HOME
    )
    assert config.server == ServerConfig(host="0.0.0.0", port=8000)


def test_malformed_toml_names_file() -> None:
    with pytest.raises(ConfigError, match="cannot load config") as error:
        parse_global_config("[server\n", GLOBAL, HOME)
    assert str(error.value).startswith(f"{GLOBAL}: ")


def test_invalid_value_names_file_and_key() -> None:
    with pytest.raises(ConfigError) as error:
        parse_global_config('[server]\nport = "x"\n', GLOBAL, HOME)
    assert str(error.value).startswith(f"{GLOBAL}: invalid config\n  server.port: ")


def test_relative_repos_anchor_on_base_dir() -> None:
    assert anchor_repos([Path("projects/app")], Path("/cfg"), HOME) == [
        Path("/cfg/projects/app")
    ]


def test_absolute_repos_ignore_base_dir() -> None:
    assert anchor_repos([Path("/srv/app")], Path("/cfg"), HOME) == [Path("/srv/app")]


@pytest.mark.parametrize(
    ("repo", "expected"),
    [("~", HOME), ("~/code/app", HOME / "code" / "app")],
)
def test_tilde_repos_expand_to_home(repo: str, expected: Path) -> None:
    assert anchor_repos([Path(repo)], Path("/cfg"), HOME) == [expected]


def test_global_repos_anchor_on_config_dir() -> None:
    config = parse_global_config('repos = ["app", "~/x"]\n', GLOBAL, HOME)
    assert config.repos == [GLOBAL.parent / "app", HOME / "x"]


def test_project_server_table_is_split_off_with_notice() -> None:
    config, notices = parse_project_config(
        '[server]\nport = 1\n[branch]\ndefault_parent = "main"\n', PROJECT, GLOBAL
    )
    assert config.branch.default_parent == "main"
    assert notices == [
        f"{PROJECT}: [server] is ignored in project files; set it in {GLOBAL}"
    ]


def test_project_without_server_has_no_notice() -> None:
    _, notices = parse_project_config("", PROJECT, GLOBAL)
    assert notices == []


def test_invalid_project_names_file_and_key() -> None:
    with pytest.raises(ConfigError) as error:
        parse_project_config('[branch]\nparent = "main"\n', PROJECT, GLOBAL)
    assert str(error.value).startswith(f"{PROJECT}: invalid config\n")
    assert "branch.parent" in str(error.value)


def test_resolve_server_defaults() -> None:
    assert resolve_server(GlobalConfig()) == ServerConfig(host="127.0.0.1", port=7420)


def test_resolve_server_flags_win_over_file() -> None:
    config = GlobalConfig(server=ServerConfig(host="0.0.0.0", port=8000))
    assert resolve_server(config, port=9000) == ServerConfig(host="0.0.0.0", port=9000)
    assert resolve_server(config, host="::1") == ServerConfig(host="::1", port=8000)
