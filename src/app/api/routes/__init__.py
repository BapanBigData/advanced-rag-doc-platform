from .health import router as health_router
from .ui import router as ui_router
from .analyze import router as analyze_router
from .compare import router as compare_router
from .chat import router as chat_router

__all__ = [
    "health_router",
    "ui_router",
    "analyze_router",
    "compare_router",
    "chat_router",
]
