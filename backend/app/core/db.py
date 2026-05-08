from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings

engine = create_engine(settings.sqlite_url, echo=False)


def init_db() -> None:
    from app.models.entities import Document, ExtractedItem  # noqa: F401

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
