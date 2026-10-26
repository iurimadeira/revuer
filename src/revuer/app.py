from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response

STATIC_DIR = Path(__file__).parent / "static"
UI_NOT_BUILT = "revuer UI not built. Run `pnpm --dir frontend build` and restart."


def create_app(static_dir: Path = STATIC_DIR) -> FastAPI:
    app = FastAPI(title="revuer")
    root = static_dir.resolve()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/{path:path}", include_in_schema=False)
    def ui(path: str) -> Response:
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (root / path).resolve()
        if file.is_file() and file.is_relative_to(root):
            return FileResponse(file)
        index = root / "index.html"
        if not index.is_file():
            return PlainTextResponse(UI_NOT_BUILT, status_code=503)
        return FileResponse(index)

    return app
