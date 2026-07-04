import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse  # Adicionado HTMLResponse
from fastapi.templating import Jinja2Templates            # Adicionado para Templates
from fastapi.staticfiles import StaticFiles              # Mantido caso use a pasta static futuramente
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import users, posts, follows

logger = logging.getLogger("uvicorn.error")

# Configura o diretório onde os arquivos HTML estão salvos
templates = Jinja2Templates(directory="app/templates")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Social Network API",
        version="1.0.0",
        description="API RESTful para Rede Social"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- ROTA PARA RENDERIZAR O SEU NOVO HTML ---
    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    # Routers
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(posts.router, prefix="/posts", tags=["posts"])
    app.include_router(follows.router, prefix="/follows", tags=["follows"])

    # Handlers de exceção global
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error("HTTPException: %s %s", request.url.path, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception at %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )