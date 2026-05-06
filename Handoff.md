# Handoff.md — ArgosArt × he.Art

_Ultimo aggiornamento: 2026-05-06 06:15 CET_
_A cura di: Neo (OpenClaw Agent)_

---

## 🎯 Obiettivo di Business

Vendere ad **he.Art** un sistema RAG chiavi in mano per:
- Ingestion e indicizzazione semantica di CV artistici, portfolio, video provini, audio demo
- Matching automatico artista↔ruolo/bando
- Dashboard producer per ricerca e shortlist

**Modello economico**: copertura 100% costi + margine significativo.
**Espansione futura**: offrire anche servizio di creazione ed esercizio ChatBot (sfruttando la pipeline RAG già sviluppata).
**Proposta commerciale**: `docs/PROPOSTA_COMMERCIALE.md`

---

## 📦 Progetti Attivi

| Progetto | Repo GitHub | Path Locale | Stato |
|---|---|---|---|
| **Argos** (RAG general-purpose) | [doureallydo/argos](https://github.com/doureallydo/argos) | `/Volumes/HD_esterno/OpenClaw_Workspace/argos/` | ✅ Completato, online |
| **ArgosArt** (RAG × he.Art) | [doureallydo/ArgosArt](https://github.com/doureallydo/ArgosArt) | `/Volumes/HD_esterno/OpenClaw_Workspace/argosart/` | ✅ MA1-MA7 completate |

---

## 🏗️ Architettura ArgosArt

```
argosart/
├── core/              # Config, modelli, logging
├── ingestion/         # 13 parser + transcoder + validator + art_cv_parser
├── embeddings/        # 4 embedders + vector_store + matching engine
├── storage/           # SQLAlchemy ORM + file_storage + repository
├── encryption/        # AES-256-GCM + Argon2id + JWT auth
├── api/               # FastAPI (main, routes, schemas, oauth, matching_routes)
├── ui/                # SPA (spa.html servita da FastAPI)
├── deploy/            # Docker, compose, script setup, entrypoint
├── docs/              # API ref, deployment guide, proposta commerciale
└── tests/             # Test suite (ingestion, encryption, storage)
```

---

## 🔑 Credenziali & Accessi

| Risorsa | Dettaglio |
|---|---|
| GitHub | account `doureallydo`, token via `gh auth token` |
| RunPod | API key in env, account `doureallydo@gmail.com` |
| Gmail invio | `my.mail.intelligence@gmail.com` (pw: env var `NEO_GMAIL_APP_PASSWORD`) |
| Admin | password: `radu` |
| Cloudflare | email `doureallydo@gmail.com` |

---

## 🐛 Bug Noti & Workaround

| Bug | Soluzione |
|---|---|
| GHCR package privato → RunPod non pulla | Rendere pubblico il package o usare Docker Hub |
| Colima rebuild cancella DB | Usare volume persistente o backup |
| Tunnel Cloudflare effimero | Tunnel named con dominio proprio |
| `asyncio.get_event_loop()` in thread | Usare `get_running_loop()` |
| Dimensioni vettori mismatch Qdrant | Verificare dim embedding prima di creare collection |

---

## 📋 Milestone Completate (8/8)

1. ✅ MA1 — Fondamenta (repo, struttura, README, config)
2. ✅ MA2 — Modelli Arte (campi art_style, technique, medium, artist_name, proposal_status)
3. ✅ MA3 — CV Parser Artistico + Smart Transcoder + Validator
4. ✅ MA4 — Matching Engine semantico
5. ✅ MA5 — API Matching & Dashboard (3 nuovi endpoint)
6. ✅ MA6 — UI Producer Dashboard (Matching + Ricerca Semantica)
7. ✅ MA7 — Documentazione Commerciale (PROPOSTA_COMMERCIALE.md con pricing, ROI, sinergia Tinexta)
8. ⬜ MA8 — Deploy su RunPod GPU (in attesa risoluzione GHCR)

---

_Istruzioni per AI model che riprende questo lavoro:_
1. Leggi questo file per capire lo stato corrente
2. Consulta `ArgosArt_stato_avanzamento.md` per lo storico dettagliato
3. Il codice è in `/Volumes/HD_esterno/OpenClaw_Workspace/argosart/`
4. Usa `git log --oneline` per vedere la cronologia commit
5. Tutte le modifiche vanno committate con commenti descrittivi e pushato su GitHub
6. La proposta commerciale è in `docs/PROPOSTA_COMMERCIALE.md`
