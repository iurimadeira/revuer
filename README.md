# revuer

A local daemon with a CLI and a web UI for reviewing and understanding code per
git worktree and branch.

Status: early development. See [TODO.md](TODO.md) for the plan.

## Development

Requires [uv](https://docs.astral.sh/uv/), Node.js 24 and pnpm.

```sh
uv sync
pnpm --dir frontend install
pnpm --dir frontend build
uv run revuer serve
```

The daemon listens on `http://127.0.0.1:7420` by default. Use
`revuer serve --host <host> --port <port>` to change it.

## Configuration

Global config at `$XDG_CONFIG_HOME/revuer/config.toml` (default
`~/.config/revuer/config.toml`):

```toml
repos = ["~/code/my-app"]

[server]
host = "127.0.0.1"
port = 7420
```

Project config at `<repo>/.revuer.toml`:

```toml
[branch]
default_parent = "main"
```

Command-line flags win over config files. `[server]` in a project file is
ignored with a warning.

## License

MIT. See [LICENSE](LICENSE).
