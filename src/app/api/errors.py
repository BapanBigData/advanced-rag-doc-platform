from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exc_handler(_, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exc_handler(_, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": f"Internal error: {exc}"})
