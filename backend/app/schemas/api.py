from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    document_id: int


class OpenTargetResponse(BaseModel):
    document_id: int
    page: int
    snippet: str


class AnalysisRunResponse(BaseModel):
    document_id: int
    pages: int
    chunks: int
    items_created: int
    evidences_created: int
