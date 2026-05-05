# ArgosArt — Sistema RAG per Portfolio Creativi e Collaborazione Artistica

**ArgosArt** è un sistema RAG modulare ottimizzato per portfolio creativi, documenti artistici, e collaborazioni nel mondo dell'arte e del design. Derivato da Argos, adattato per la partnership con **he.Art**.

> 🎨 Argos + Art = Il riconoscimento visivo e semantico applicato al mondo creativo.

## ✨ Caratteristiche

- 🖼️ **Portfolio Ingestion**: Carica e indicizza portfolio artistici in qualsiasi formato
- 🎯 **Ricerca semantica creativa**: Trova opere, stili, concept attraverso descrizioni testuali
- 🎵 **Multimodale nativo**: Immagini ad alta risoluzione, video d'arte, audio di performance
- 📋 **Creative Brief Parser**: Estrai e struttura brief creativi da PDF, Word e Markdown
- 🏷️ **Tagging automatico**: Stili, tecniche, palette colori rilevati automaticamente
- 🔐 **Crittografia AES-256-GCM**: Portfolio e proposte riservate protette
- 🤝 **Source Attribution**: Ogni artista/studio ha la propria fonte tracciabile
- 🌐 **API REST + UI**: FastAPI + React, deployabile ovunque

## 🏗️ Architettura

```
argosart/
├── core/           # Configurazione, modelli (con estensioni artistiche)
├── ingestion/      # Parser ottimizzati per contenuti creativi
├── embeddings/     # CLIP-first per dominio artistico
├── storage/        # Archiviazione portfolio + metadati
├── encryption/     # AES-256-GCM + Argon2id per contenuti riservati
├── api/            # FastAPI REST con endpoint portfolio
├── ui/             # UI in stile galleria
├── deploy/         # Docker + guide cloud
└── tests/          # Test suite
```

## 🎨 Stack Tecnologico

| Modulo | Tecnologia | Focus Creativo |
|---|---|---|
| **Backend API** | Python 3.11+ FastAPI | Endpoint portfolio |
| **Vision AI** | CLIP ViT-L/14 | Dominante per ricerca visiva |
| **PDF parsing** | GLM-OCR (opzionale) | Brief creativi, cataloghi |
| **OCR immagini** | EasyOCR + Tesseract | Didascalie opere, testi in mostra |
| **Vector DB** | Qdrant | Collezioni per portfolio, stili, artisti |
| **Color analysis** | ColorThief + Pillow | Palette detection automatica |
| **Encryption** | AES-256-GCM + Argon2id | Protezione opere inedite |
| **Frontend** | React + Tailwind | UI galleria, mood board |

## 🚀 Quick Start

```bash
# 1. Clona
git clone https://github.com/doureallydo/ArgosArt.git
cd argosart

# 2. Ambiente
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 3. Config
cp .env.example .env

# 4. Servizi (Qdrant, Redis, MinIO)
docker compose -f deploy/docker-compose.yml up -d

# 5. Avvia
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## 🤝 Collaborazione he.Art

ArgosArt è progettato per la partnership con **he.Art**:

- **Portfolio condivisi**: Artisti caricano opere, il sistema le indicizza semanticamente
- **Creative Matching**: Abbinamento automatico artista-progetto basato su stile e competenze
- **Proposal Tracking**: Gestione proposte di collaborazione con versioning e commenti
- **Exhibition Planning**: Organizzazione mostre con ricerca semantica tra opere
- **Rights Management**: Gestione diritti e licenze con crittografia documentale

## 📄 Licenza

MIT — vedi [LICENSE](LICENSE)

---

_ArgosArt: Dove l'intelligenza artificiale incontra la creatività umana._
