from typing import Annotated

import typer
import uvicorn

from revuer.app import create_app
from revuer.config import ConfigError, load_global_config, resolve_server

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Review code per git worktree and branch."""


@app.command()
def serve(
    host: Annotated[str | None, typer.Option(help="Address to bind.")] = None,
    port: Annotated[
        int | None, typer.Option(min=1, max=65535, help="Port to bind.")
    ] = None,
) -> None:
    """Start the revuer daemon."""
    try:
        server = resolve_server(load_global_config(), host=host, port=port)
    except ConfigError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1) from error
    uvicorn.run(create_app(), host=server.host, port=server.port)
