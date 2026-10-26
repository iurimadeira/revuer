from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.types import Receive, Scope, Send

STATIC_DIR = Path(__file__).parent / "static"
UI_NOT_BUILT = "revuer UI not built. Run `pnpm --dir frontend build` and restart."


def _static_file(root: Path, path: str) -> Path | None:
    try:
        file = (root / path.lstrip("/")).resolve()
        if file.is_file() and file.is_relative_to(root):
            return file
    except (OSError, ValueError):
        pass
    return None


def create_app(static_dir: Path = STATIC_DIR) -> FastAPI:
    app = FastAPI(title="revuer")
    root = static_dir.resolve()
    not_found = app.router.default

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    async def ui(scope: Scope, receive: Receive, send: Send) -> None:
        path: str = scope["path"]
        if (
            scope["type"] != "http"
            or scope["method"] not in ("GET", "HEAD")
            or path == "/api"
            or path.startswith("/api/")
        ):
            return await not_found(scope, receive, send)
        file = _static_file(root, path) or root / "index.html"
        response = (
            FileResponse(file)
            if file.is_file()
            else PlainTextResponse(UI_NOT_BUILT, status_code=503)
        )
        await response(scope, receive, send)

    app.router.default = ui
    return app
