# Handoff.md — ArgosArt × he.Art

_Ultimo aggiornamento: 2026-05-06 02:35 CET_
_A cura di: Neo (OpenClaw Agent)_

---

## 🎯 Obiettivo di Business

Vendere ad **he.Art** un sistema RAG chiavi in mano per:
- Ingestion e indicizzazione semantica di CV artistici, portfolio, video provini, audio demo
- Matching automatico artista↔ruolo/bando
- Dashboard producer per ricerca e shortlist

**Modello economico**: copertura 100% costi + margine significativo.
**Espansione futura**: offrire anche servizio di creazione ed esercizio ChatBot (sfruttando la pipeline RAG già sviluppata).

---

## 📦 Progetti Attivi

| Progetto | Repo GitHub | Path Locale | Stato |
|---|---|---|---|
| **Argos** (RAG general-purpose) | [doureallydo/argos](https://github.com/doureallydo/argos) | `/Volumes/HD_esterno/OpenClaw_Workspace/argos/` | ✅ Completato, online |
| **ArgosArt** (RAG × he.Art) | [doureallydo/ArgosArt](https://github.com/doureallydo/ArgosArt) | `/Volumes/HD_esterno/OpenClaw_Workspace/argosart/` | 🔄 MA5 completato, MA6 in corso |

---

## 🏗️ Architettura ArgosArt

```
argosart/
├── core/              # Config, modelli, logging
│   ├── config.py      # Settings con estensioni artistiche
│   ├── models.py      # DocumentRecord con campi arte
│   └── logging.py     # Loguru
├── ingestion/         # Parser documenti
│   ├── base.py        # Interfaccia parser + registry
│   ├── pdf_parser.py  # PDF (pdfplumber + GLM-OCR opzionale)
│   ├── image_parser.py    # Immagini (EasyOCR + Tesseract)
│   ├── art_cv_parser.py   # ✅ CV artistico strutturato
│   ├── transcoder.py      # ✅ HEIC→JPG, MOV→MP4, resize
│   ├── validator.py       # ✅ Checklist materiali richiesti
│   ├── pipeline.py        # Orchestratore ingestion
│   └── ...
├── embeddings/        # Modelli embedding + Qdrant
│   ├── embedders.py   # CLIP + E5 + CLAP + Gemini opzionale
│   ├── vector_store.py    # Qdrant async client
│   └── matching.py        # ✅ Artista↔Ruolo matching
├── storage/           # Database relazionale + file storage
│   ├── models.py      # SQLAlchemy ORM (con campi arte)
│   ├── database.py    # Session factory
│   ├── file_storage.py    # Backend local/S3/MinIO
│   └── repository.py  # CRUD operations
├── encryption/        # AES-256-GCM + Argon2id
│   ├── engine.py
│   └── auth.py        # JWT/OAuth2
├── api/               # FastAPI REST
│   ├── main.py        # App entrypoint
│   ├── routes.py      # Endpoints (upload, search, documents)
│   ├── schemas.py     # Pydantic models
│   └── matching_routes.py  # ✅ Endpoint matching + portfolio
├── ui/                # Frontend SPA
│   └── spa.html       # Single-page app (servita da FastAPI)
├── deploy/            # Docker, compose, script
└── tests/             # Test suite
```

---

## 🔧 Stack Tecnologico

| Componente | Tecnologia | Versione |
|---|---|---|
| Backend | Python | ≥3.11 |
| API | FastAPI | ≥0.115 |
| Vector DB | Qdrant | 1.13.x |
| Cache/Queue | Redis | 7.x |
| Storage | MinIO / Local | latest |
| Text Embeddings | multilingual-e5-large | - |
| Image Embeddings | CLIP ViT-L/14 | - |
| Audio Embeddings | CLAP HTSAT | - |
| OCR | EasyOCR + Tesseract | - |
| Speech-to-Text | OpenAI Whisper | base model |
| PDF Parsing | pdfplumber + GLM-OCR (opz) | - |
| Encryption | AES-256-GCM + Argon2id | - |
| Auth | JWT (python-jose) + OAuth2 | HS256 |
| Frontend | HTML/CSS/JS vanilla | - |
| Container | Docker + Colima (Mac) | - |
| Tunnel | Cloudflare Tunnel (cloudflared) | 2026.3.0 |

---

## 🔑 Credenziali & Accessi

| Risorsa | Dettaglio |
|---|---|
| GitHub | account `doureallydo`, token via `gh auth token` |
| RunPod | API key in env, account `doureallydo@gmail.com` |
| Gmail invio | `my.mail.intelligence@gmail.com` (password in env var `NEO_GMAIL_APP_PASSWORD`) |
| Admin Argos/ArgosArt | password: `radu` |
| Cloudflare | email `doureallydo@gmail.com` |

---

## 🐛 Bug Noti & Workaround

| Bug | Sintomo | Soluzione |
|---|---|---|
| GHCR package privato | RunPod non pulla immagine | Rendere pubblico il package o usare Docker Hub |
| Colima rebuild cancella DB | Documenti persi | Usare volume persistente o backup |
| Tunnel Cloudflare effimero | URL cambia a ogni riavvio | Usare tunnel named con dominio proprio |
| `asyncio.get_event_loop()` in thread | Crash in produzione | Usare `asyncio.get_running_loop()` |
| Dimensioni vettori mismatch | 400 Bad Request da Qdrant | Verificare dimensione embedding model prima di creare collection |

---

## 📋 Milestone Completate

1. ✅ MA1 — Fondamenta (repo + struttura + README + config)
2. ✅ MA2 — Modelli Arte (campi art_style, technique, medium, artist_name, proposal_status)
3. ✅ MA3 — CV Parser Artistico + Smart Transcoder + Validator
4. ✅ MA4 — Matching Engine semantico (JobRequirements, hard filters, rank merge)
5. ✅ MA5 — API Matching & Dashboard (POST /api/match, GET /api/profile, GET /api/dashboard/stats)

## 📋 Prossimi Step

1. [ ] MA6 — UI Producer Dashboard (ricerca semantica + shortlist + profili artista)
2. [ ] MA7 — Deploy & Documentazione Commerciale (RunPod + presentazione he.Art)

---

_Istruzioni per AI model che riprende questo lavoro:_
1. Leggi questo file per capire lo stato corrente
2. Consulta `ArgosArt_stato_avanzamento.md` per lo storico delle milestone
3. Il codice è in `/Volumes/HD_esterno/OpenClaw_Workspace/argosart/`
4. Usa `git log --oneline` per vedere la cronologia commit
5. Tutte le modifiche vanno committate con commenti descrittivi e pushato su GitHub
