"""ArgosArt API Routes — Endpoint matching e portfolio."""

from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from embeddings.matching import JobRequirements, MatchingEngine
from embeddings.vector_store import VectorStore
from ingestion.art_cv_parser import ArtistCVParser
from storage.database import get_db
from storage.repository import DocumentRepository

router = APIRouter(tags=["Matching & Portfolio"])

# ── Services ──────────────────────────────────────────────────
cv_parser = ArtistCVParser()
vector_store = VectorStore()
matching_engine = MatchingEngine(vector_store)


# ── Schemas ───────────────────────────────────────────────────

class JobSearchRequest(BaseModel):
    """Richiesta di matching artista per un ruolo."""
    title: str = Field(..., description="Titolo del ruolo/bando")
    description: str = Field(..., description="Descrizione completa del ruolo")
    voice_types: list[str] = Field(default_factory=list, description="Tipi voce richiesti (es. ['Soprano'])")
    voice_range: str = Field("", description="Range vocale (es. 'G2-B4')")
    min_height_cm: Optional[int] = Field(None, description="Altezza minima in cm")
    max_height_cm: Optional[int] = Field(None, description="Altezza massima in cm")
    max_age: Optional[int] = Field(None, description="Età massima")
    required_skills: list[str] = Field(default_factory=list, description="Skills obbligatorie")
    required_languages: list[str] = Field(default_factory=list, description="Lingue richieste")
    required_dance: list[str] = Field(default_factory=list, description="Stili danza richiesti")
    gender: str = Field("any", description="Genere: female, male, any")
    top_k: int = Field(20, ge=1, le=100, description="Numero massimo risultati")


class MatchResponse(BaseModel):
    """Risultati matching."""
    job_title: str
    query: str
    total_matches: int
    took_ms: float
    matches: list[dict]


class CVProfileResponse(BaseModel):
    """Profilo artista strutturato."""
    document_id: str
    full_name: str
    height_cm: str
    voice_type: str
    voice_range: str
    dance_styles: list[str]
    languages: list[dict]
    searchable_text: str
    tags: list[str]


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/match", response_model=MatchResponse)
async def match_artists(
    body: JobSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """🔍 Match semantico: dato un ruolo, trova i migliori artisti.

    Esempio:
    ```json
    {
      "title": "Soprano Drammatico per Musical",
      "description": "Cerchiamo soprano drammatico under 35 per produzione
                      teatrale. Richiesta danza moderna e contemporanea.",
      "voice_types": ["Soprano"],
      "required_dance": ["moderno", "contemporaneo"],
      "max_age": 35,
      "top_k": 10
    }
    ```

    Returns artists ranked by semantic relevance.
    """
    start = time.time()

    requirements = JobRequirements(
        title=body.title,
        description=body.description,
        voice_types=body.voice_types,
        voice_range=body.voice_range,
        min_height_cm=body.min_height_cm,
        max_height_cm=body.max_height_cm,
        max_age=body.max_age,
        required_skills=body.required_skills,
        required_languages=body.required_languages,
        required_dance=body.required_dance,
        gender=body.gender,
    )

    match_results = await matching_engine.match_artists(
        requirements, top_k=body.top_k
    )

    elapsed = (time.time() - start) * 1000

    return MatchResponse(
        job_title=body.title,
        query=requirements.to_search_query(),
        total_matches=len(match_results),
        took_ms=round(elapsed, 2),
        matches=[m.to_dict() for m in match_results],
    )


@router.get("/profile/{doc_id}", response_model=CVProfileResponse)
async def get_artist_profile(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """📋 Estrai profilo strutturato da un CV artista."""
    doc = await DocumentRepository.get_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from pathlib import Path

    file_path = Path(doc.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found in storage")

    text = doc.parsed_text or ""
    profile = await cv_parser.parse(file_path, raw_text=text)

    return CVProfileResponse(
        document_id=doc_id,
        full_name=profile.full_name,
        height_cm=profile.height_cm,
        voice_type=f"{profile.voice_type} {profile.vocal_subtype}".strip(),
        voice_range=profile.voice_range,
        dance_styles=profile.dance_styles,
        languages=profile.languages,
        searchable_text=profile.to_searchable_text(),
        tags=profile.to_tags(),
    )


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """📊 Statistiche dashboard producer."""
    from storage.repository import SourceRepository

    sources = await SourceRepository.list_all(db)
    total_sources = len(sources)

    from sqlalchemy import select, func
    from storage.models import DocumentModel

    result = await db.execute(
        select(
            func.count(DocumentModel.id).label("total"),
            func.sum(DocumentModel.file_size_bytes).label("total_bytes"),
            DocumentModel.document_type,
        ).group_by(DocumentModel.document_type)
    )
    type_counts = {}
    total_docs = 0
    for r in result.all():
        type_counts[r.document_type] = r.total
        total_docs += r.total

    return {
        "total_documents": total_docs,
        "total_sources": total_sources,
        "documents_by_type": type_counts,
    }
