from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .errors import register_error_handlers
from .routes import (
    health_router,
    ui_router,
    analyze_router,
    compare_router,
    chat_router,
)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

    # static mount (same as before)
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(ui_router)
    app.include_router(health_router)
    app.include_router(analyze_router)
    app.include_router(compare_router)
    app.include_router(chat_router)

    # Errors
    register_error_handlers(app)

    return app

app = create_app()

# Run:
# uvicorn src.app.api.main:app --reload
# uvicorn src.app.api.main:app --host 127.0.0.0 --port 8080 --reload
