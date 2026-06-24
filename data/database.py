import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select

DB_FILE = "documents.db"


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    file_path: str = Field(index=True)
    file_name: str
    file_hash: str = Field(index=True)
    file_type: str
    raw_text: str = ""
    summary: str = ""
    keywords: str = ""
    processed_at: Optional[datetime] = None
    model_used: str = ""


class Database:
    _instance: Optional["Database"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        db_path = Path(__file__).parent.parent / DB_FILE
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def add_document(
        self,
        file_path: str,
        file_name: str,
        file_hash: str,
        file_type: str,
        raw_text: str,
        summary: str,
        keywords: str,
        model_used: str,
    ) -> Document:
        with Session(self.engine) as session:
            existing = session.exec(
                select(Document).where(Document.file_hash == file_hash)
            ).first()

            if existing:
                existing.raw_text = raw_text
                existing.summary = summary
                existing.keywords = keywords
                existing.processed_at = datetime.now()
                existing.model_used = model_used
                doc = existing
            else:
                doc = Document(
                    file_path=file_path,
                    file_name=file_name,
                    file_hash=file_hash,
                    file_type=file_type,
                    raw_text=raw_text,
                    summary=summary,
                    keywords=keywords,
                    processed_at=datetime.now(),
                    model_used=model_used,
                )
                session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc

    def get_by_hash(self, file_hash: str) -> Optional[Document]:
        with Session(self.engine) as session:
            return session.exec(
                select(Document).where(Document.file_hash == file_hash)
            ).first()

    def get_all(self) -> List[Document]:
        with Session(self.engine) as session:
            return list(session.exec(select(Document)))

    def search(self, keyword: str) -> List[Document]:
        with Session(self.engine) as session:
            return list(
                session.exec(
                    select(Document).where(
                        Document.keywords.contains(keyword)
                        | Document.summary.contains(keyword)
                        | Document.raw_text.contains(keyword)
                        | Document.file_name.contains(keyword)
                    )
                )
            )

    def delete(self, doc_id: int):
        with Session(self.engine) as session:
            doc = session.get(Document, doc_id)
            if doc:
                session.delete(doc)
                session.commit()


def compute_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
    except Exception:
        return ""
    return hasher.hexdigest()


db = Database()
