# ArgosArt — Stato Avanzamento

_Ultimo aggiornamento: 2026-05-06 02:00 CET_

---

## Milestone Completate ✅

### MA1 — Fondamenta (06/05/2026 00:01)
- Creato repo [doureallydo/ArgosArt](https://github.com/doureallydo/ArgosArt)
- Clonato struttura da Argos con tutti i moduli
- Rinominato package `argos` → `argosart`
- README con visione he.Art e 4 cluster strategici
- Configurazione con estensioni artistiche (color analysis, style tagging, risoluzione)

### MA2 — Modelli Arte (06/05/2026 01:25)
- `core/models.py`: aggiunti campi `art_style`, `art_technique`, `art_medium`, `artist_name`, `artwork_title`, `proposal_status`
- `storage/models.py`: aggiunte colonne corrispondenti in SQLAlchemy ORM
- `.env.example`: aggiornato con variabili per funzionalità artistiche

---

## Milestone In Corso 🔄

### MA3 — CV Parser Artistico + Transcoding + Validator (0%)
- `ingestion/art_cv_parser.py` — da creare
- `ingestion/transcoder.py` — da creare
- `ingestion/validator.py` — da creare

### MA4 — Matching Engine (0%)
- `embeddings/matching.py` — da creare

### MA5 — API & UI per Producer (0%)
- Nuovi endpoint: `/api/match`, `/api/proposals`
- UI: vista galleria, shortlist, valutazioni

### MA6 — Deploy & Documentazione Commerciale (0%)
- Deploy su RunPod
- Presentazione per he.Art

---

## Riepilogo Tecnico

| Metrica | Valore |
|---|---|
| File totali | 68 |
| Righe di codice | ~7.500 |
| Moduli Python | 9 (core, ingestion×11, embeddings×3, storage×4, encryption×2, api×4) |
| Parser supportati | PDF, Word, Excel, PPT, TXT, MD, Immagini (8 formati), Audio (18 formati), Video (22 formati) |
| Embedding models | 4 (E5, CLIP, CLAP, Gemini2 opzionale) |
| Collection Qdrant | 4 (text, images, audio, video) |

---

## Decisioni Architetturali

1. **SPA servita da FastAPI** invece di React build separato → deploy più semplice
2. **Qdrant self-hosted** invece di ChromaDB → più performante su larga scala
3. **PDF parsing dual-engine**: pdfplumber (primario) + GLM-OCR (opzionale per layout complessi)
4. **Auth opzionale in dev mode** → accelera sviluppo e test
5. **Colima invece di Docker Desktop** → non richiede sudo su macOS
6. **Cloudflare Tunnel invece di ngrok** → già integrato con account Cloudflare

---

## Prossima Azione

Implementare MA3 (CV Parser + Transcoding + Validator)
