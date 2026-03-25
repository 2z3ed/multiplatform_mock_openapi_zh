import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/kb", tags=["knowledge"])

DOCUMENTS: dict[str, dict] = {}
CHUNKS: dict[str, list[dict]] = {}


class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    doc_type: str = "faq"


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    doc_type: str
    chunk_count: int
    created_at: str


class ChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    index: int


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    query: str
    results: list[dict]


@router.post("/documents", response_model=DocumentResponse)
def upload_document(req: DocumentUploadRequest) -> DocumentResponse:
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat() + "Z"
    
    DOCUMENTS[doc_id] = {
        "document_id": doc_id,
        "title": req.title,
        "content": req.content,
        "doc_type": req.doc_type,
        "created_at": now
    }
    
    chunks = _chunk_document(doc_id, req.content)
    CHUNKS[doc_id] = chunks
    
    return DocumentResponse(
        document_id=doc_id,
        title=req.title,
        doc_type=req.doc_type,
        chunk_count=len(chunks),
        created_at=now
    )


def _chunk_document(doc_id: str, content: str) -> list[dict]:
    sentences = content.replace("\n", " ").split(". ")
    chunks = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            chunks.append({
                "chunk_id": f"{doc_id}_chunk_{i}",
                "document_id": doc_id,
                "content": sentence.strip(),
                "index": i,
                "embedding": [0.0] * 1536
            })
    return chunks


@router.post("/reindex")
def reindex_documents() -> dict:
    total_chunks = sum(len(chunks) for chunks in CHUNKS.values())
    return {
        "status": "ok",
        "total_documents": len(DOCUMENTS),
        "total_chunks": total_chunks,
        "reindexed_at": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/documents/{document_id}/chunks")
def get_document_chunks(document_id: str) -> dict:
    if document_id not in CHUNKS:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": document_id,
        "chunks": CHUNKS[document_id]
    }


@router.post("/search", response_model=SearchResponse)
def search_knowledge(req: SearchRequest) -> SearchResponse:
    all_chunks = []
    for doc_id, chunks in CHUNKS.items():
        for chunk in chunks:
            all_chunks.append(chunk)
    
    query_lower = req.query.lower()
    results = []
    for chunk in all_chunks:
        if query_lower in chunk["content"].lower():
            results.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "content": chunk["content"],
                "score": 0.9
            })
            if len(results) >= req.top_k:
                break
    
    return SearchResponse(query=req.query, results=results)