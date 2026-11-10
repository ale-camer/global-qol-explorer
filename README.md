# 🌍 Global Quality of Life Explorer

Interactive multilingual geospatial explorer for comparing structural development, socioeconomic, health, and well-being indicators across countries over time.

- **Live Frontend (GCS):** [https://storage.googleapis.com/global-qol-explorer-frontend/index.html](https://storage.googleapis.com/global-qol-explorer-frontend/index.html)
- **Live API (Cloud Run):** [https://qol-api-service-450135571603.us-central1.run.app/docs](https://qol-api-service-450135571603.us-central1.run.app/docs)

---

## 🏗️ Architecture

- **Frontend (`frontend/`):** Vue 3 (Composition API), Vite, `@vue-leaflet/vue-leaflet` (Leaflet.js choropleth maps), `vue-i18n` (17 languages), Bootstrap 5.
- **Backend (`backend/`):** FastAPI (Python 3.12), Pydantic v2, Google Cloud BigQuery (`global-qol-explorer.quality_of_life` dataset: `fact_indicators` & `dim_countries`), Dockerized on Cloud Run.

```text
global-qol-explorer/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # /data and /metadata REST endpoints
│   │   ├── api/static/         # world-geometry.json (GeoJSON boundaries)
│   │   ├── core/config.py      # GCP & BigQuery settings
│   │   ├── db/session.py       # BigQuery client dependency
│   │   └── schemas/schemas.py  # Pydantic response models
│   ├── geometries/             # GeoJSON builder from administrative boundaries
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/         # MapView, ControlsPanel, TablePanel, MapLegend, LanguageSwitcher
    │   ├── composables/        # Reactive BigQuery API hooks & choropleth state
    │   ├── content/            # 17 language dictionaries (JSON)
    │   ├── services/api.js     # REST client for Cloud Run API
    │   └── utils/helpers.js    # Choropleth color scales, CSV export & formatters
    ├── index.html
    └── vite.config.js
```

---

## 🚀 Local Development

### 1. Backend (FastAPI + BigQuery)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev
```
