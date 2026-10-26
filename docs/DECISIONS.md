# Decisions

## Contexts with a pure core, enforced by import-linter

Each context is a package with a pure `core`, an orchestration module and a
public `__init__`. import-linter contracts in `pyproject.toml` enforce core
purity, public-API-only access from interfaces, and layering. See
[CONTEXT.md](../CONTEXT.md).

Rejected alternatives:

- **Single-module contexts with private functions.** Underscore names separate
  pure and IO code only by convention. A module boundary is something a tool
  can check.
- **An ast-based pytest import check.** Custom code to maintain, and it misses
  indirect imports. import-linter already builds the import graph and reports
  the full chain.
- **Documentation-only enforcement.** Rules that nothing checks drift as soon
  as the code grows.
- **Result tuples instead of domain exceptions.** `(value, error)` pairs are
  not idiomatic Python and push checks onto every caller. Core raises the
  context's domain error, such as `ConfigError`.
- **An architecture section in README.** README is for users installing and
  running revuer. Contributor rules live in `CONTEXT.md`, linked from README.
