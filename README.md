# 🌍 Global Quality of Life Explorer

Interactive multilingual geospatial explorer for comparing structural development, socioeconomic, health, and well-being indicators across countries over time.

- **Live Frontend (GCS):** [https://storage.googleapis.com/global-qol-explorer-frontend/index.html](https://storage.googleapis.com/global-qol-explorer-frontend/index.html)
- **Live API (Cloud Run):** [https://qol-api-service-450135571603.us-central1.run.app/docs](https://qol-api-service-450135571603.us-central1.run.app/docs)

---

## 🏗️ Architecture

- **Frontend (`frontend/`):** Vue 3 (Composition API), Vite, `@vue-leaflet/vue-leaflet` (Leaflet.js choropleth maps over Dark Canvas basemap), `vue-i18n` (17 languages with RTL support), Dark Slate UI with interactive 2-step classification/indicator showcase, quick search filters, global ranking, and bidirectional map-table synchronization.
- **Backend (`backend/`):** FastAPI (Python 3.12), Pydantic v2, Google Cloud BigQuery (`global-qol-explorer.quality_of_life` dataset: `fact_indicators`, `dim_countries`, `dim_indicators`), persistent BigQuery client via FastAPI `lifespan`, in-memory TTL metadata cache, GZip compression, Dockerized on Cloud Run.

```text
global-qol-explorer/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # /data and /metadata REST endpoints
│   │   ├── api/static/         # world-geometry.json (GeoJSON boundaries)
│   │   ├── core/config.py      # GCP, BigQuery, cache & CORS settings
│   │   ├── db/session.py       # Persistent BigQuery client dependency
│   │   └── schemas/schemas.py  # Pydantic v2 response models
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

### 1. Backend (FastAPI + BigQuery)
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
Open `http://localhost:5173/global-qol-explorer-frontend/`.
