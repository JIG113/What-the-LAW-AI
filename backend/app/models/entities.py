from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(index=True)
    file_name: str
    file_type: str
    storage_path: str
    parse_status: str = "queued"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractedItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(index=True)
    category: str = Field(index=True)
    item_key: str
    item_value: str
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
