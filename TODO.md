# revuer TODO

revuer is a local daemon with a CLI and a web UI for reviewing and understanding
code per worktree and branch.

This file is the project plan. Work is split into big tasks. Each task lists
what to build, acceptance criteria and subtasks.

Status: `todo`, `doing`, `done`, `dropped`.

---

## Phase 1: MVP

Goal: review a branch's changes in the browser. Diff only. No comments, no live
updates, no graph.

### M1. Project skeleton and config

Status: doing

**What to build.** A Python package with a Typer CLI and a FastAPI server that
serves a React shell, plus global and per-project config files.

**Acceptance criteria**
- [ ] `revuer serve` starts the daemon on `127.0.0.1:7420` by default.
- [ ] Global config at `$XDG_CONFIG_HOME/revuer/config.toml` (default
      `~/.config/revuer/config.toml`) with `[server] host, port` and `repos = [...]`.
- [ ] Project config loader for `<repo>/.revuer.toml` with
      `[branch] default_parent`, with tests. `serve` reads it from M2.
- [ ] Precedence per key, where layers overlap: CLI flag, then project file,
      then global file, then defaults. Today only `server.*` overlaps (CLI and
      global). The project-over-global test arrives with the first shared key.
- [ ] Server keys in a project file are ignored, with a notice returned as data.
- [ ] Invalid config fails with a clear message naming the file and key.
- [ ] CI runs ruff, pyright, pytest, frontend typecheck and frontend build.

**Subtasks**
- [ ] uv project, hatchling build, MIT license, Python 3.12+.
- [ ] Config loading and validation.
- [ ] FastAPI app serving the built React app.
- [ ] React + Vite + TypeScript shell.
- [ ] GitHub Actions workflow.

### M2. Repositories and sessions

Status: todo · Blocked by: M1

**What to build.** The daemon finds every worktree of each configured
repository. Each worktree is a session with its own URL.

**Acceptance criteria**
- [ ] Sessions come from `git worktree list --porcelain` for each configured repo.
- [ ] Each session lives at `/<repo>/<worktree>`.
- [ ] `GET /api/sessions` returns repo, worktree, path, branch and URL.
- [ ] The home page lists all sessions grouped by repo.
- [ ] `revuer sessions` prints sessions as JSON.
- [ ] `revuer url` prints the URL of the session for the current directory, or
      fails with a hint if the directory is not in a configured repo.
- [ ] A missing or broken repo path shows an error for that repo only.
- [ ] `serve` reads each repo's `.revuer.toml` and prints its notices.

**Subtasks**
- [ ] Worktree discovery with tests against real temporary repos.
- [ ] Sessions API and home page.
- [ ] CLI talks to the running daemon and fails with a start hint if it is down.

### M3. Branch diff

Status: todo · Blocked by: M2

**What to build.** For a session, show everything that changed since the branch
forked from its parent: commits plus uncommitted and untracked files.

**Acceptance criteria**
- [ ] Parent resolution order: `git config branch.<b>.revuerParent`, then
      `default_parent` from `.revuer.toml`, then the remote default branch
      (`origin/HEAD`), else an error with the command to set it.
- [ ] Fork point: `git merge-base --fork-point <parent> HEAD`, falling back to
      `git merge-base`.
- [ ] Diff from the fork point to the working tree, including untracked files,
      without touching the index (`GIT_OPTIONAL_LOCKS=0`, no `git add`).
- [ ] Detached HEAD and a parent equal to the branch fail with clear messages.
- [ ] The UI shows a file tree, split and unified views and syntax highlighting.
- [ ] Binary and very large files show a placeholder.
- [ ] Reloading the page fetches a fresh diff.

**Subtasks**
- [ ] Git runner: argument lists, timeouts, `LC_ALL=C`, `-z` output.
- [ ] Parent and fork-point resolution with edge-case tests.
- [ ] Diff API: files, status, hunks, line numbers.
- [ ] Diff page with `@pierre/diffs`.

### M4. Install, docs and smoke test

Status: todo · Blocked by: M3

**Acceptance criteria**
- [ ] `uv tool install .` from a clone installs `revuer` with the built UI.
- [ ] README covers install, config, `serve`, `sessions` and `url`.
- [ ] One Playwright smoke test opens a session and sees a changed file.

---

## Roadmap

Big tasks, roughly in priority order. Each one becomes a phase when we pick it up.

### R1. Live updates

Status: todo

The diff updates while you look at it.

- [ ] watchfiles on worktrees with an open tab, plus gitdir watching for commits
      and branch switches.
- [ ] SSE stream per session with small invalidate events.
- [ ] Light polling for sessions without an open tab.
- [ ] Stay inside inotify limits with many worktrees.

### R2. Persistent comments

Status: todo

Line comments shared by people and agents that survive restarts.

- [ ] SQLite store in WAL mode, with the daemon as the single writer.
- [ ] Threads with replies, authors and timestamps.
- [ ] Resolved is a state, not a delete.
- [ ] Comments belong to the branch and show as outdated when the line changes.
- [ ] CLI: `revuer comment add|list|reply|resolve`, with JSON output.
- [ ] Idempotent import of comment batches.
- [ ] UI: write, reply to and resolve comments, plus a resolved filter.

### R3. Agent skill

Status: todo · Blocked by: R2

- [ ] `skills/revuer/SKILL.md` teaches any coding agent to open sessions, read
      comments, reply to them and resolve them through the CLI.

### R4. More diff modes

Status: todo

- [ ] Working tree only (uncommitted changes).
- [ ] Per-commit review with a commit list.
- [ ] Arbitrary commit ranges.
- [ ] Ignore whitespace and context-line options.

### R5. Smarter parent discovery

Status: todo

Find the parent branch without config in more cases.

- [ ] Branch creation entry in the reflog.
- [ ] Upstream when it differs from the branch itself.
- [ ] Anonymous creation commit when it is still an ancestor.
- [ ] Parent changes and rewritten parents covered by tests.

### R6. Code graph: files and modules

Status: todo

Navigate changes through the files they touch.

- [ ] tree-sitter import extraction for Elixir, TypeScript/JavaScript and Python.
- [ ] Resolve imports to files: Elixir module index, tsconfig paths, Python packages.
- [ ] Neighborhood graph of changed files, one or two hops.
- [ ] React Flow + elkjs view. Clicking a node opens that file's diff.
- [ ] Cache per blob SHA.

### R7. Review experience

Status: todo

- [ ] Mark files as viewed.
- [ ] Keyboard navigation for files, hunks and comments.
- [ ] File filter and search.
- [ ] Markdown and image previews.

### R8. Daemon operations

Status: todo

- [ ] Background start and stop commands.
- [ ] Example systemd user unit.
- [ ] Base path support for reverse proxies.
- [ ] Structured logging.

### R9. Distribution

Status: todo

- [ ] PyPI release with trusted publishing from GitHub Actions.
- [ ] Versioning and changelog.

### R10. Code graph: symbols and calls

Status: todo · Blocked by: R6

- [ ] Changed functions and their callers and callees.
- [ ] Jump from a symbol to its definition diff.

### R11. GitHub pull request review

Status: todo

- [ ] Open a pull request diff through `gh`.
- [ ] Import pull request review comments.
