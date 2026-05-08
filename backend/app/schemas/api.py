from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    document_id: int


class OpenTargetResponse(BaseModel):
    document_id: int
    page: int
    snippet: str
