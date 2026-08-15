# Deploy Vigil PIDS to Render

This project has two parts. On Render you create **two services** from the same GitHub repo.

| Service | Type | Role |
|---------|------|------|
| Backend | Web Service | FastAPI + weather + recommendations |
| Frontend | Static Site | React dashboard |

---

## 0. Before Render (one-time)

1. Create a free account at [https://render.com](https://render.com)
2. Push this project to **GitHub** (public or private repo)
3. On Render, connect your GitHub account

```bash
# From project root (example)
git add .
git commit -m "Prepare Vigil PIDS for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## 1. Deploy the Backend (Web Service)

1. Render Dashboard → **New +** → **Web Service**
2. Select your GitHub repository
3. Configure:

| Setting | Value |
|---------|--------|
| Name | `vigil-pids-api` (any name) |
| Region | Choose closest (e.g. Singapore / Frankfurt) |
| Root Directory | `backend` |
| Runtime | **Python 3** |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

4. Click **Create Web Service**
5. Wait until status is **Live**
6. Copy your API URL, for example:  
   `https://vigil-pids-api.onrender.com`

7. Test in browser:  
   `https://YOUR-API-URL.onrender.com/api/health`  
   You should see `"status": "ok"`

> Free tier sleeps after inactivity. First request after sleep can take 30–60 seconds.

---

## 2. Deploy the Frontend (Static Site)

1. Render Dashboard → **New +** → **Static Site**
2. Select the **same** GitHub repository
3. Configure:

| Setting | Value |
|---------|--------|
| Name | `vigil-pids-dashboard` |
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |

4. Add an **Environment Variable**:

| Key | Value |
|-----|--------|
| `VITE_API_BASE` | `https://YOUR-API-URL.onrender.com` |

   (Use the exact backend URL from step 1 — **no trailing slash**)

5. Click **Create Static Site**
6. Open the frontend URL Render gives you, for example:  
   `https://vigil-pids-dashboard.onrender.com`

---

## 3. After deploy checklist

- [ ] `/api/health` on the backend URL works
- [ ] Dashboard opens and shows **API online**
- [ ] Search a city (e.g. Agra) and run **Fetch weather & recommend**
- [ ] Demo scenarios (High Wind / Thunderstorm) work

---

## Common issues

| Problem | Fix |
|---------|-----|
| Frontend shows API offline | Check `VITE_API_BASE` matches backend URL exactly, then **Manual Deploy → Clear build cache & deploy** |
| CORS / blocked requests | Backend already allows `*`. Confirm you call HTTPS API URL, not localhost |
| Backend 404 on `/api/...` | Root Directory must be `backend` |
| Frontend blank page | Publish Directory must be `dist` |
| Cold start timeout | Wait ~1 minute and refresh (free tier sleep) |
| SQLite data resets | Normal on free Render — disk is ephemeral after redeploy |

---

## Optional: Blueprint (`render.yaml`)

If the repo contains `render.yaml` at the root, you can use:

**New + → Blueprint** → select the repo → Render creates both services from the file.

After the API is created, set `VITE_API_BASE` on the static site to the live API URL (or update the blueprint once you know it).

---

## What NOT to upload

- Do not upload `.venv`, `node_modules`, or local `.db` files
- Do not put secrets in the repo (this project needs no weather API key)
- Submit your **GitHub link** + **live Render URLs** in the case-study PDF / video
