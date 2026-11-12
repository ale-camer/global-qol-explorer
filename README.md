# 🌍 Global Quality of Life Explorer

Interactive multilingual geospatial explorer for comparing structural development, socioeconomic, health, and well-being indicators across countries over time.

- **Live Frontend (GCS):** [https://storage.googleapis.com/global-qol-explorer-frontend/index.html](https://storage.googleapis.com/global-qol-explorer-frontend/index.html)
- **Live API (Cloud Run):** [https://qol-api-service-450135571603.us-central1.run.app/docs](https://qol-api-service-450135571603.us-central1.run.app/docs)

---

## 🏗️ Architecture

- **Frontend (`frontend/`):** Vue 3 (Composition API), Vite, `@vue-leaflet/vue-leaflet` (Leaflet.js choropleth maps over Dark Canvas basemap), `vue-i18n` (17 languages with RTL support), Dark Slate UI with interactive 2-step classification/indicator showcase, quick search filters, global ranking, and bidirectional map-table synchronization.
- **Backend (`backend/`):** FastAPI (Python 3.12), Pydantic v2, clustered SQLite snapshot (`backend/data/qol.sqlite` with ~1–5 ms query latency and automatic fallback to Google Cloud BigQuery `global-qol-explorer.quality_of_life`), in-memory TTL metadata cache, GZip compression, Dockerized on Cloud Run.
- **Automated Data Ingestion (`backend/ingestion/` & `.github/workflows/ingest_owid.yml`):** Weekly scheduled GitHub Actions workflow (`Mondays 08:00 UTC / 05:00 ART`) that fetches all 44 indicators directly from Our World in Data (OWID Grapher), validates parity against the preserved baseline, atomically refreshes `backend/data/qol.sqlite`, and sends a plain-text status alert to WhatsApp via CallMeBot.

```text
global-qol-explorer/
├── .github/workflows/
│   └── ingest_owid.yml         # Weekly automated OWID ingestion & WhatsApp alerts
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # /data and /metadata REST endpoints
│   │   ├── api/static/         # world-geometry.json (GeoJSON boundaries)
│   │   ├── core/config.py      # SQLite snapshot, GCP, BigQuery, cache & CORS settings
│   │   ├── db/session.py       # Read-only SQLite connection & BigQuery fallback
│   │   └── schemas/schemas.py  # Pydantic v2 response models
│   ├── data/
│   │   ├── baseline_backup/    # Preserved baseline manifest & local CSV backup
│   │   └── qol.sqlite          # Clustered SQLite snapshot (240 countries, 44 indicators)
│   ├── ingestion/
│   │   ├── catalog.json        # Canonical 240 countries & 44 OWID indicator slugs
│   │   ├── ingest_owid.py      # Parallel OWID downloader & atomic SQLite builder
│   │   ├── compare_baseline.py # Parity auditor against baseline_backup/
│   │   └── notify_whatsapp.py  # Plain-text WhatsApp notifier (CallMeBot / Meta / Twilio)
│   ├── geometries/             # Offline GeoJSON builder & dedicated requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # MapView, ControlsPanel, TablePanel, MapLegend, LanguageSwitcher
│   │   ├── composables/        # Reactive API hooks, AbortController & choropleth state
│   │   ├── content/            # 17 language dictionaries (JSON)
│   │   ├── services/api.js     # REST client with request cancellation support
│   │   └── utils/helpers.js    # Choropleth scales, ranking, CSV export & formatters
│   ├── .env.example
│   ├── index.html
│   └── vite.config.js
└── docker-compose.dev.yml
```

---

## 🚀 Local Development

### 1. Backend (FastAPI + SQLite Snapshot / BigQuery Fallback)
```bash
cd backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*(Or using containers: `docker compose -f docker-compose.dev.yml up --build`)*

### 2. Frontend (Vue 3 + Vite)
```bash
cd frontend
cp .env.example .env.development.local
npm install
npm run dev
```
Open `http://localhost:5173/`.

### 3. Refresh Data Snapshot & Audit Against Baseline
```bash
PYTHONPATH=. python -m backend.ingestion.ingest_owid
PYTHONPATH=. python -m backend.ingestion.compare_baseline
```
To enable automated WhatsApp notifications in GitHub Actions (`Settings -> Secrets and variables -> Actions`), add:
- `WHATSAPP_PHONE`: Your phone number with country code (e.g., `+54911...`)
- `WHATSAPP_APIKEY`: Your CallMeBot API key
