# Crash Monitor API (Backend)

Backend service for **CrashMonitor** – a RESTful API that receives crash reports from the Android SDK and serves analytics data for the management dashboard.

> This repository contains the server-side component only.  
> Android SDK + Demo app: `crash-monitor-android`  
> Dashboard: Retool-based analytics portal (see “Dashboard” section below)

---

## Architecture (High level)

**Android App (with SDK)** → **CrashMonitor API** → **Database** → **Analytics Dashboard**

- **Android SDK** sends crash/non-fatal events, device/app metadata, and queue snapshots.
- **API** exposes endpoints for ingesting events and querying analytics.
- **DB** stores crashes, devices, sessions, and derived aggregates (depending on your implementation).
- **Dashboard** (Retool) queries the API to show graphs and tables.

---

## Features

- Ingest crash events (fatal & non‑fatal) with metadata (device, OS, app version, timestamp, stack trace, tags).
- Device & app version grouping for analytics.
- Time-range and device filters for dashboards.
- Health endpoint for deployment monitoring.
- Basic validation & error handling.
- (Optional) Presets/filters storage if you implemented it in the backend.

---

## Tech Stack

> Update these lines to match your actual code.

- Language: **Python**
- Framework: **Flask** (or FastAPI)
- Database: **MongoDB** (MongoDB Atlas) / (or other)
- Deployment: **Koyeb** / (or other cloud provider)

---

## API Endpoints (example)

> Replace/align with your actual routes.

### Health
- `GET /health` → `{ "status": "ok" }`

### Crash ingestion
- `POST /api/crashes`
  - Body: crash payload (stack trace, message, severity, device info, app info, timestamp, etc.)
  - Returns: created event id

### Analytics
- `GET /api/analytics/summary?from=...&to=...`
- `GET /api/analytics/by-device?from=...&to=...`
- `GET /api/analytics/by-version?from=...&to=...`
- `GET /api/crashes?deviceId=...&from=...&to=...&severity=...`

---

## Local Setup

### 1) Prerequisites
- Python 3.10+
- pip / virtualenv
- MongoDB (local) **or** MongoDB Atlas connection string

### 2) Install
```bash
git clone https://github.com/OriaCohen054/crash-monitor-api.git
cd crash-monitor-api
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3) Configure environment variables
Create a `.env` file (do **NOT** commit it):
```env
MONGODB_URI=YOUR_MONGODB_CONNECTION_STRING
DB_NAME=crash_monitor
API_KEY=YOUR_API_KEY_OPTIONAL
```

> **Security note:**  
> Never commit secrets (DB URI / API keys). Use `.env` locally and environment variables in Koyeb.

### 4) Run
```bash
python app.py
# or (Flask)
# flask --app app run --host=0.0.0.0 --port=5000
```

---

## Deployment

### Koyeb (example)
- Set environment variables in the Koyeb service configuration:
  - `MONGODB_URI`, `DB_NAME`, (and `API_KEY` if used)
- Deploy from GitHub repository
- Verify with:
  - `GET /health`

> **Do I need to publish the Koyeb URL publicly?**  
> Not mandatory. For the README you can:
> - Provide the public base URL **without** secrets (safe), or
> - Write “Deployed on Koyeb (URL shared with instructor privately)” if you prefer.

---

## Dashboard

Retool analytics dashboard (public embed link):
- **CrashMonitorAnalyticsDashboard:** *(paste your public link here)*

If you prefer not to expose it publicly, keep it private and provide demo screenshots + a short video/GIF.

---

## Repository Structure (example)

```
.
├─ app.py / main.py
├─ routes/
├─ services/
├─ models/
├─ requirements.txt
└─ README.md
```

---

## Troubleshooting

- **401/403**: Check API key header / auth middleware.
- **Cannot connect to DB**: Verify `MONGODB_URI` and network access (Atlas IP whitelist).
- **CORS issues** (dashboard): Add CORS configuration for the Retool origin.

---

## License
Add a license file at the root (MIT/Apache 2.0/etc.)
