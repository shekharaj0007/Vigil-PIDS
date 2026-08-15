# Setup Instructions

## Prerequisites

- Python **3.10+**
- Node.js **18+** and npm
- Internet access (for Open-Meteo live calls and first `npm`/`pip` install)

## Backend setup

```bash
cd backend
python -m venv .venv
```

Activate:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows CMD: `.venv\Scripts\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

Optional: copy `.env.example` to `.env` and change default location.

Start API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify: open http://127.0.0.1:8000/api/health

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api` to port 8000.

## Demo without waiting for bad weather

1. Start backend + frontend  
2. On the dashboard, click **High Wind**, **Heavy Rain**, or **Thunderstorm**  
3. Or POST scenarios from `sample_data/weather_scenarios.json` to `/api/calibrate/simulate`

## Common issues

| Issue | Fix |
|-------|-----|
| Dashboard shows API offline | Start uvicorn on port 8000 |
| Weather API error 502 | Check internet / Open-Meteo availability |
| `npm` fails | Upgrade Node to 18+ |
| Port in use | Change `--port` / Vite `server.port` |

## Video demo checklist

1. Show architecture slide / README  
2. Start backend + dashboard  
3. Live calibrate for a city preset  
4. Run High Wind and Thunderstorm scenarios  
5. Show analytics chart + history table  
6. Briefly open Swagger `/docs`
