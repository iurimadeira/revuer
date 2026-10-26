# revuer context

How the code is organized and the domain terms it uses. Rejected alternatives
are in [docs/DECISIONS.md](docs/DECISIONS.md).

## Architecture

The package is split into contexts and interface layers.

```text
src/revuer/
  cli.py            interface: Typer CLI
  web/              interface: FastAPI app
  config/           context
    __init__.py     public API (re-exports only)
    core.py         pure rules
    loader.py       orchestration and IO
  static/           built frontend (generated)
```

- **Context**: a package under `revuer/` that owns one area of the domain, such
  as `config`. Its `__init__.py` is the public API: re-exports listed in
  `__all__`, no logic.
- **Core** (`<context>/core.py`): pure functions and models. They take data and
  return data, and raise the context's domain error (for example
  `ConfigError`) for invalid input. No file, environment, process, network,
  clock or logging access. `pathlib.Path` is allowed as a value type, but core
  must not call filesystem methods such as `resolve`, `exists`, `open`,
  `expanduser` or `home`. Pass what IO would provide (file text, home
  directory, other paths) in as arguments.
- **Orchestration** (`<context>/loader.py` or a similarly named module): does
  the IO, converts IO failures into the domain error and calls core.
- **Interface layers** (`revuer.cli`, `revuer.web`): translate between the
  outside world and contexts. They import only a context's public package,
  never its `core` or orchestration modules.

### Import rules

Enforced by import-linter (`uv run lint-imports`, contracts in
`pyproject.toml`):

| Module                 | May import                                         |
| ---------------------- | -------------------------------------------------- |
| `revuer.cli`           | `revuer.web`, public context packages              |
| `revuer.web`           | public context packages                            |
| `<context>`            | its own modules, other public context packages     |
| `<context>.core`       | pure stdlib modules and pydantic                   |

Contexts never import `revuer.web` or `revuer.cli`.

### Tests

Tests mirror the package layout. Core tests use plain data: no temporary
files, no environment. Orchestration and interface tests cover IO with
`tmp_path` and the autouse `XDG_CONFIG_HOME` fixture in `tests/conftest.py`.

```text
tests/
  config/test_core.py     pure rules
  config/test_loader.py   files and environment
  web/test_app.py         HTTP behavior
  test_cli.py             CLI behavior
```

### Adding a context

1. Create `src/revuer/<name>/` with `core.py`, an orchestration module and an
   `__init__.py` that re-exports the public API.
2. Add `revuer.<name>.core` to the purity contract's `source_modules`, and the
   new private modules to the public-API contract's `forbidden_modules`.
3. Add the context to the bottom layer of the layers contract as a sibling
   that may import other contexts, e.g. `"revuer.config : revuer.<name>"`.
4. Add `tests/<name>/` with core and orchestration tests.

## Glossary

- **Global config**: the user's file at `$XDG_CONFIG_HOME/revuer/config.toml`
  (default `~/.config/revuer/config.toml`). Holds server settings and repos.
- **Project config**: a repository's `.revuer.toml`. Holds branch settings.
- **Repo**: a git repository listed in the global config's `repos`. Relative
  entries resolve against the global config's directory; `~` means the home
  directory.
- **Server settings**: `server.host` and `server.port`. CLI flags win over the
  global config, which wins over defaults.
- **Notice**: a message returned as data about a config key that was ignored,
  such as `[server]` in a project config. Not an error.
- **Worktree**: a git working tree of a repo, as listed by
  `git worktree list`.
- **Branch**: the branch checked out in a worktree. Its changes are reviewed
  against its parent branch from the fork point.
- **Session**: one worktree as revuer presents it, with its own URL.
