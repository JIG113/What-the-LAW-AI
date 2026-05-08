from datetime import datetime, UTC
from typing import Optional

from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True)
    file_name: str
    file_type: str
    storage_path: str
    file_hash: str = Field(index=True)
    parse_status: str = "queued"
    ocr_status: str = "pending"
    indexed_status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AnalysisRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(index=True)
    status: str = Field(default="queued", index=True)
    pages: int = 0
    chunks: int = 0
    items_created: int = 0
    evidences_created: int = 0
    error_message: str = ""
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: Optional[datetime] = None


class DocumentPage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(index=True)
    page_no: int
    merged_text: str
    ocr_confidence: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Chunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(index=True)
    page_start: int
    page_end: int
    chunk_text: str
    section_title: str = "본문"
    embedding_json: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExtractedItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(index=True)
    category: str = Field(index=True)
    item_key: str
    item_value: str
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ItemEvidence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    extracted_item_id: int = Field(index=True)
    document_id: int = Field(index=True)
    page_no: int
    snippet_text: str
    char_start: int = 0
    char_end: int = 0
    bbox_json: str = ""
    retrieval_method: str = "heuristic"
    evidence_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserEdit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(index=True)
    editor: str = "system"
    old_category: str
    new_category: str
    old_value: str
    new_value: str
    reason: str = ""
    edited_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
