from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    document_id: int


class OpenTargetResponse(BaseModel):
    document_id: int
    page: int
    snippet: str


class AnalysisRunResponse(BaseModel):
    id: int
    document_id: int
    status: str
    pages: int
    chunks: int
    items_created: int
    evidences_created: int
    error_message: str


class ItemEditRequest(BaseModel):
    category: str
    item_value: str
    editor: str = "reviewer"
    reason: str = "manual update"


class SearchResponse(BaseModel):
    chunk_id: int
    document_id: int
    page_start: int
    keyword_score: int
    vector_score: float
    hybrid_score: float
    snippet: str


class RunListResponse(BaseModel):
    total: int
    items: list[AnalysisRunResponse]


class AnalysisEventResponse(BaseModel):
    id: int
    run_id: int
    level: str
    step: str
    message: str


class RunEventListResponse(BaseModel):
    total: int
    items: list[AnalysisEventResponse]


class ValidationIssueResponse(BaseModel):
    id: int
    run_id: int
    item_id: int
    rule_code: str
    severity: str
    message: str


class ValidationIssueListResponse(BaseModel):
    total: int
    items: list[ValidationIssueResponse]
