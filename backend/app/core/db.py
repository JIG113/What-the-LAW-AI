from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings

engine = create_engine(settings.sqlite_url, echo=False)


def _apply_sqlite_migrations(session: Session) -> None:
    session.exec(text(
        """
        CREATE TABLE IF NOT EXISTS analysisrun (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            pages INTEGER NOT NULL DEFAULT 0,
            chunks INTEGER NOT NULL DEFAULT 0,
            items_created INTEGER NOT NULL DEFAULT 0,
            evidences_created INTEGER NOT NULL DEFAULT 0,
            error_message TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            finished_at TEXT,
            cancel_requested BOOLEAN NOT NULL DEFAULT 0,
            cancelled_at TEXT
        )
        """
    ))
    session.commit()

    existing = session.exec(text("PRAGMA table_info('analysisrun')")).all()
    col_names = {row[1] for row in existing}
    if "cancel_requested" not in col_names:
        session.exec(text("ALTER TABLE analysisrun ADD COLUMN cancel_requested BOOLEAN NOT NULL DEFAULT 0"))
    if "cancelled_at" not in col_names:
        session.exec(text("ALTER TABLE analysisrun ADD COLUMN cancelled_at TEXT"))
    session.commit()

    doc_cols = session.exec(text("PRAGMA table_info('document')")).all()
    doc_col_names = {row[1] for row in doc_cols}
    if "rule_profile" not in doc_col_names:
        session.exec(text("ALTER TABLE document ADD COLUMN rule_profile TEXT NOT NULL DEFAULT 'default'"))
        session.commit()


def init_db() -> None:
    from app.models import entities  # noqa: F401

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _apply_sqlite_migrations(session)


def get_session():
    with Session(engine) as session:
        yield session
