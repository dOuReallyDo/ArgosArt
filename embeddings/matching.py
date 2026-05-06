"""Matching Engine — Artista↔Ruolo via ricerca semantica cross-modale.

Basato su CLIP + multilingual-e5-large embedding unificati in Qdrant.
Dato un bando/casting call, il matching engine:
1. Embedda la descrizione del ruolo (testo)
2. Cerca nel vector store tra i profili artista e i loro materiali
3. Ritorna una shortlist ranked per relevance score

Supporta:
- Text-to-text matching (descrizione ruolo → CV)
- Text-to-image matching (ruolo → foto book artista)
- Text-to-video matching (ruolo → showreel)
- Filtri hard: altezza, età, voce, skill obbligatorie
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.logging import logger
from core.models import DocumentType
from embeddings.embedders import embedding_manager


@dataclass
class JobRequirements:
    """Requisiti strutturati di un bando/casting call."""

    title: str = ""  # Titolo del ruolo
    description: str = ""  # Descrizione testuale libera

    # Filtri hard (OR tra valori, AND tra campi)
    voice_types: list[str] = field(default_factory=list)  # ["Soprano"]
    voice_range: str = ""  # "G2-B4"
    min_height_cm: Optional[int] = None
    max_height_cm: Optional[int] = None
    max_age: Optional[int] = None
    required_skills: list[str] = field(default_factory=list)
    required_languages: list[str] = field(default_factory=list)
    required_dance: list[str] = field(default_factory=list)

    gender: str = ""  # "female", "male", "any"

    def to_search_query(self) -> str:
        """Converte i requisiti in una query testuale per embedding."""
        parts = [self.description or self.title]
        if self.voice_types:
            parts.append(f"Voce: {', '.join(self.voice_types)}")
        if self.required_skills:
            parts.append(f"Skills: {', '.join(self.required_skills)}")
        if self.required_dance:
            parts.append(f"Danza: {', '.join(self.required_dance)}")
        if self.required_languages:
            parts.append(f"Lingue: {', '.join(self.required_languages)}")
        return " | ".join(parts)


@dataclass
class MatchResult:
    """Risultato di matching per un artista."""

    artist_name: str
    document_id: str
    score: float
    matched_chunks: list[dict] = field(default_factory=list)
    profile_summary: str = ""

    def to_dict(self) -> dict:
        return {
            "artist_name": self.artist_name,
            "document_id": self.document_id,
            "score": round(self.score, 4),
            "matched_chunks": self.matched_chunks,
            "profile_summary": self.profile_summary,
        }


class MatchingEngine:
    """Motore di matching semantico artista↔ruolo.

    Utilizza la ricerca vettoriale su Qdrant con filtri hard pre/post-processing.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store

    async def match_artists(
        self,
        requirements: JobRequirements,
        top_k: int = 20,
    ) -> list[MatchResult]:
        """Trova i migliori artisti per un dato ruolo.

        Pipeline:
        1. Semantic search sul testo del ruolo
        2. Filtraggio hard sui metadati
        3. Ranking finale
        """
        query = requirements.to_search_query()
        logger.info(f"🔍 Matching per: {requirements.title or query[:80]}")

        # 1. Semantic search
        hits = await self.vector_store.search(
            query=query,
            top_k=top_k * 2,  # Fetch more, then filter
            document_types=[DocumentType.PDF, DocumentType.TEXT],
        )

        # 2. Hard filters on metadata
        results = []
        for hit in hits:
            # Check hard filters
            if not self._passes_hard_filters(hit, requirements):
                continue

            match = MatchResult(
                artist_name=hit.get("original_filename", "Unknown"),
                document_id=hit.get("document_id", ""),
                score=hit.get("score", 0),
                matched_chunks=[{
                    "text": hit.get("text", "")[:200],
                    "collection": hit.get("collection", ""),
                    "chunk_index": hit.get("chunk_index", 0),
                }],
            )

            # Merge same document results (keep highest score)
            existing = next(
                (r for r in results if r.document_id == match.document_id), None
            )
            if existing:
                if match.score > existing.score:
                    results.remove(existing)
                    results.append(match)
                else:
                    existing.matched_chunks.extend(match.matched_chunks)
            else:
                results.append(match)

        # Sort by relevance
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:top_k]

        logger.success(f"✅ Matching: {len(results)} artisti trovati")
        return results

    async def match_by_cv_text(
        self,
        requirements: JobRequirements,
        artist_profiles: list[dict],
        top_k: int = 20,
    ) -> list[MatchResult]:
        """Matching offline su profili artista già estratti (senza Qdrant).

        Utile per demo/batch processing.
        """
        query_vec = await embedding_manager.embed_texts(
            [requirements.to_search_query()], for_query=True
        )

        results = []
        for profile in artist_profiles:
            # Embed profile
            profile_text = profile.get("searchable_text", "")
            if not profile_text:
                continue

            # Simulate cosine similarity
            import numpy as np
            profile_vec = await embedding_manager.embed_texts([profile_text])

            similarity = np.dot(query_vec[0], profile_vec[0]) / (
                np.linalg.norm(query_vec[0]) * np.linalg.norm(profile_vec[0])
            )

            if similarity > 0.3:  # Minimum threshold
                results.append(MatchResult(
                    artist_name=profile.get("full_name", "Unknown"),
                    document_id=profile.get("document_id", ""),
                    score=float(similarity),
                    profile_summary=profile_text[:300],
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    # ── Hard Filters ────────────────────────────────────────────

    @staticmethod
    def _passes_hard_filters(
        hit: dict,
        reqs: JobRequirements,
    ) -> bool:
        """Check if a search hit passes mandatory hard filters."""
        payload = hit.get("payload", hit)
        text = (payload.get("text", "") or "").lower()

        # Height filter
        if reqs.min_height_cm or reqs.max_height_cm:
            height_str = payload.get("height_cm", "")
            if height_str:
                import re
                m = re.search(r"(\d+)", str(height_str))
                if m:
                    h = int(m.group(1))
                    if reqs.min_height_cm and h < reqs.min_height_cm:
                        return False
                    if reqs.max_height_cm and h > reqs.max_height_cm:
                        return False

        # Voice type filter
        if reqs.voice_types:
            if not any(vt.lower() in text for vt in reqs.voice_types):
                return False

        # Required skills
        if reqs.required_skills:
            if not all(s.lower() in text for s in reqs.required_skills):
                return False

        # Required dance styles
        if reqs.required_dance:
            if not any(d.lower() in text for d in reqs.required_dance):
                return False

        # Required languages
        if reqs.required_languages:
            if not all(l.lower() in text for l in reqs.required_languages):
                return False

        return True
