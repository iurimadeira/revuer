"""Pure configuration rules: parsing, validation, path anchoring and precedence.

Functions here take data and return data, raising `ConfigError` for invalid
input. `Path` is used as a value type only: never call filesystem methods
(`resolve`, `exists`, `open`, `expanduser`, `home`) here.
"""

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

__all__ = [
    "BranchConfig",
    "ConfigError",
    "GlobalConfig",
    "ProjectConfig",
    "ServerConfig",
    "anchor_repos",
    "parse_global_config",
    "parse_project_config",
    "resolve_server",
]


class ConfigError(Exception):
    pass


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ServerConfig(Strict):
    host: str = "127.0.0.1"
    port: int = Field(default=7420, strict=True, ge=1, le=65535)


class GlobalConfig(Strict):
    server: ServerConfig = ServerConfig()
    repos: list[Path] = []


class BranchConfig(Strict):
    default_parent: str | None = None


class ProjectConfig(Strict):
    branch: BranchConfig = BranchConfig()


def _parse_toml(text: str, path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"{path}: cannot load config: {error}") from error


def _validate[T: BaseModel](model: type[T], data: dict[str, Any], path: Path) -> T:
    try:
        return model.model_validate(data)
    except ValidationError as error:
        problems = "\n".join(
            f"  {'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()
        )
        raise ConfigError(f"{path}: invalid config\n{problems}") from error


def _expand_home(path: Path, home: Path) -> Path:
    if path.parts[:1] == ("~",):
        return home.joinpath(*path.parts[1:])
    return path


def anchor_repos(repos: list[Path], base_dir: Path, home: Path) -> list[Path]:
    """Expand a leading `~` to `home` and anchor relative paths on `base_dir`."""
    return [base_dir / _expand_home(repo, home) for repo in repos]


def parse_global_config(text: str, path: Path, home: Path) -> GlobalConfig:
    """Parse the global file at `path`, anchoring `repos` on its directory."""
    config = _validate(GlobalConfig, _parse_toml(text, path), path)
    repos = anchor_repos(config.repos, path.parent, home)
    return config.model_copy(update={"repos": repos})


def parse_project_config(
    text: str, path: Path, global_path: Path
) -> tuple[ProjectConfig, list[str]]:
    """Parse the project file at `path` and return notices about ignored keys."""
    data = _parse_toml(text, path)
    notices: list[str] = []
    if "server" in data:
        notices.append(
            f"{path}: [server] is ignored in project files; set it in {global_path}"
        )
    project = {key: value for key, value in data.items() if key != "server"}
    return _validate(ProjectConfig, project, path), notices


def resolve_server(
    config: GlobalConfig, host: str | None = None, port: int | None = None
) -> ServerConfig:
    """Apply CLI values over the global file, which is already over defaults."""
    return ServerConfig(
        host=config.server.host if host is None else host,
        port=config.server.port if port is None else port,
    )
