"""Configuration IO: locate, read and resolve config files around the pure core."""

import os
from pathlib import Path

from revuer.config.core import (
    ConfigError,
    GlobalConfig,
    ProjectConfig,
    parse_global_config,
    parse_project_config,
)

__all__ = ["global_config_path", "load_global_config", "load_project_config"]

PROJECT_FILE = ".revuer.toml"


def global_config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "revuer" / "config.toml"


def _read_text(path: Path) -> str:
    """Return the file's text, or an empty string when it does not exist."""
    try:
        return path.read_bytes().decode()
    except FileNotFoundError:
        return ""
    except (OSError, ValueError) as error:
        raise ConfigError(f"{path}: cannot load config: {error}") from error


def load_global_config() -> GlobalConfig:
    path = global_config_path()
    config = parse_global_config(_read_text(path), path, Path.home())
    repos = [repo.resolve() for repo in config.repos]
    return config.model_copy(update={"repos": repos})


def load_project_config(repo_root: Path) -> tuple[ProjectConfig, list[str]]:
    """Return the project config and notices about ignored keys."""
    path = repo_root / PROJECT_FILE
    return parse_project_config(_read_text(path), path, global_config_path())
