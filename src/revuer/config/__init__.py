"""Configuration context: the public API for global and project config.

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

from revuer.config.core import (
    BranchConfig,
    ConfigError,
    GlobalConfig,
    ProjectConfig,
    ServerConfig,
    resolve_server,
)
from revuer.config.loader import (
    global_config_path,
    load_global_config,
    load_project_config,
)

__all__ = [
    "BranchConfig",
    "ConfigError",
    "GlobalConfig",
    "ProjectConfig",
    "ServerConfig",
    "global_config_path",
    "load_global_config",
    "load_project_config",
    "resolve_server",
]
