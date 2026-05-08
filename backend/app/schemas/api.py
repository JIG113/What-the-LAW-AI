from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    document_id: int


class OpenTargetResponse(BaseModel):
    document_id: int
    page: int
    snippet: str


class AnalysisRunResponse(BaseModel):
    run_id: int
    document_id: int
    status: str
    pages: int
    chunks: int
    items_created: int
    evidences_created: int
    error_message: str
