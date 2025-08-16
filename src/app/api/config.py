import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Document Portal API"
    APP_VERSION: str = "0.1"

    # keep consistent with your classes
    FAISS_BASE: str = os.getenv("FAISS_BASE", "faiss_index")
    UPLOAD_BASE: str = os.getenv("UPLOAD_BASE", "data")
    FAISS_INDEX_NAME: str = os.getenv("FAISS_INDEX_NAME", "index")

    # paths for static/UI
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

settings = Settings()
