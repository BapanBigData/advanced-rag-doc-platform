from typing import Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.document_ingestion.data_ingestion import DocumentComparator
from src.core.document_compare.document_comparator import DocumentComparatorLLM
from src.common.utils.document_ops import FastAPIFileAdapter

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("")
async def compare_documents(
    reference: UploadFile = File(...),
    actual: UploadFile = File(...),
) -> Any:
    try:
        dc = DocumentComparator()
        
        ref_path, act_path = dc.save_uploaded_files(
            FastAPIFileAdapter(reference), FastAPIFileAdapter(actual)
        )
        # kept for clarity; combine uses internal state
        _ = (ref_path, act_path)
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_text)
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")
