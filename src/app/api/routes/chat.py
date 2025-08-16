from typing import Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..config import settings
from ..deps import resolve_index_dir

from src.core.document_ingestion.data_ingestion import ChatIngestor
from src.core.document_chat.retrieval import ConversationalRAG
from src.common.utils.document_ops import FastAPIFileAdapter

router = APIRouter(prefix="/chat", tags=["chat"])

# ---------- BUILD INDEX ----------
@router.post("/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=settings.UPLOAD_BASE,
            faiss_base=settings.FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        # NOTE: your method name was "built_retriver" in the snippet.
        # If your class actually exposes "build_retriever", update it there.
        ci.built_retriver(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

# ---------- QUERY ----------
@router.post("/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        index_dir = resolve_index_dir(session_id, use_session_dirs)
        # existence check kept in loader (raises 404 if missing)
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=settings.FAISS_INDEX_NAME)
        response = rag.invoke(question, chat_history=[])
        return {"answer": response, "session_id": session_id, "k": k, "engine": "LCEL-RAG"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
