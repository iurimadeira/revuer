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

Code layout and import rules are in [CONTEXT.md](CONTEXT.md).

## Configuration

Global config at `$XDG_CONFIG_HOME/revuer/config.toml` (default
`~/.config/revuer/config.toml`):

```toml
repos = ["~/code/my-app"]

[server]
host = "127.0.0.1"
port = 7420
```

Relative `repos` entries resolve against the config file's directory.
Command-line flags win over the global file.

Project config at `<repo>/.revuer.toml` (read once repo discovery lands):

```toml
[branch]
default_parent = "main"
```

`[server]` in a project file is ignored with a notice.

## License

MIT. See [LICENSE](LICENSE).
