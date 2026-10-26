"""Configuration loading.

Which keys live at which layer (later columns win over earlier ones):

| Key                     | Default     | Global file | Project file      | CLI flag |
| ----------------------- | ----------- | ----------- | ----------------- | -------- |
| `server.host`           | `127.0.0.1` | yes         | ignored, notice   | `--host` |
| `server.port`           | `7420`      | yes         | ignored, notice   | `--port` |
| `repos`                 | `[]`        | yes         | no                | no       |
| `branch.default_parent` | none        | no          | yes               | no       |

The global file is `$XDG_CONFIG_HOME/revuer/config.toml` (default
`~/.config/revuer/config.toml`). The project file is `<repo>/.revuer.toml`.
Relative `repos` entries resolve against the global file's directory.
Unknown keys are errors, except `[server]` in a project file.
"""

import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


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


def global_config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "revuer" / "config.toml"


def _read(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as error:
        raise ConfigError(f"{path}: cannot load config: {error}") from error


def _validate[T: BaseModel](model: type[T], data: dict[str, Any], path: Path) -> T:
    try:
        return model.model_validate(data)
    except ValidationError as error:
        problems = "\n".join(
            f"  {'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors()
        )
        raise ConfigError(f"{path}: invalid config\n{problems}") from error


def load_global_config() -> GlobalConfig:
    path = global_config_path()
    config = _validate(GlobalConfig, _read(path), path)
    repos = [(path.parent / repo.expanduser()).resolve() for repo in config.repos]
    return config.model_copy(update={"repos": repos})


class BranchConfig(Strict):
    default_parent: str | None = None


class ProjectConfig(Strict):
    branch: BranchConfig = BranchConfig()


def load_project_config(repo_root: Path) -> tuple[ProjectConfig, list[str]]:
    """Return the project config and notices about ignored keys."""
    path = repo_root / ".revuer.toml"
    data = _read(path)
    notices: list[str] = []
    if data.pop("server", None) is not None:
        notices.append(
            f"{path}: [server] is ignored in project files; set it in "
            f"{global_config_path()}"
        )
    return _validate(ProjectConfig, data, path), notices


def resolve_server(
    config: GlobalConfig, host: str | None = None, port: int | None = None
) -> ServerConfig:
    return ServerConfig(
        host=config.server.host if host is None else host,
        port=config.server.port if port is None else port,
    )
