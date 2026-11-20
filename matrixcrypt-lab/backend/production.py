"""Serve the built React application and unchanged Python API at one origin."""
from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from backend.api.main import app as api_app


def create_app(frontend_directory: Path | None = None) -> Starlette:
    directory = frontend_directory or Path(__file__).resolve().parents[1] / "frontend" / "dist"
    if not (directory / "index.html").is_file():
        raise RuntimeError("Frontend build is missing. Run npm ci and npm run build in frontend first.")

    async def index(request):
        # Revalidate the entry point so a deployment cannot leave stale asset links.
        return FileResponse(directory / "index.html", headers={"Cache-Control": "no-cache"})

    # The frontend uses hash routes. Unknown server URLs must remain real 404s,
    # especially /api URLs, instead of returning the application's HTML.
    return Starlette(routes=[
        Route("/", index),
        Route("/index.html", index),
        Mount("/assets", StaticFiles(directory=directory / "assets")),
        Mount("/", api_app),
    ])
