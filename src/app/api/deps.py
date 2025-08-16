import os
from fastapi import HTTPException
from .config import settings

def resolve_index_dir(session_id: str | None, use_session_dirs: bool) -> str:
    """
    Returns the faiss index directory, validating existence when needed.
    """
    if use_session_dirs and not session_id:
        raise HTTPException(status_code=400,
                            detail="session_id is required when use_session_dirs=True")
    index_dir = os.path.join(settings.FAISS_BASE, session_id) if use_session_dirs else settings.FAISS_BASE  # type: ignore
    return index_dir
