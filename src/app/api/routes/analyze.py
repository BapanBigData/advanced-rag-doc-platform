from typing import Any, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from src.core.document_ingestion.data_ingestion import DocHandler
from src.core.document_analyzer.data_analysis import DocumentAnalyzer
from src.common.utils.document_ops import FastAPIFileAdapter, read_pdf_via_handler

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("", response_model=None)
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf_via_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result: Dict = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
