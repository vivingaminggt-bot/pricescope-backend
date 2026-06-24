# Deploying the PriceScope Backend (FastAPI + Firebase)

You already know this drill from the frontend — same GitHub + Render flow,
just a different repo and one extra step (Firebase).

## Step 1 — Create your Firebase project

1. Go to https://console.firebase.google.com
2. Click **Add project** → name it `pricescope` → finish setup (you can
   skip Google Analytics).
3. Inside the project, go to **Build → Firestore Database** → **Create
   database** → choose "Start in production mode" → pick a location close
   to you (e.g. `asia-south1` for India) → Enable.
4. Click the **gear icon (⚙) → Project settings → Service accounts**.
5. Click **Generate new private key**. This downloads a `.json` file —
   keep it secret, never upload it to GitHub.

## Step 2 — Upload this backend to GitHub

Same as before:

1. Create a new repo, e.g. `pricescope-backend`.
2. Go inside the extracted folder (so you see `main.py`, `routes/`, etc.
   directly — not a wrapper folder).
3. Select everything inside and drag it into GitHub's upload page.
4. Commit.

Your repo should look like:
```
pricescope-backend/
├── main.py
├── requirements.txt
├── render.yaml
├── routes/
├── scraper/
├── firebase/
└── models/
```

## Step 3 — Deploy on Render

1. Go to https://dashboard.render.com → **New → Web Service** (not Static
   Site this time — this one runs Python).
2. Connect your `pricescope-backend` GitHub repo.
3. Fill in:

| Field | Value |
|---|---|
| Name | `pricescope-api` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

4. Before clicking Create, scroll to **Environment Variables** and add:
   - Key: `FIREBASE_CREDENTIALS_JSON`
   - Value: open the `.json` key file you downloaded in Step 1, copy its
     **entire contents**, and paste it as the value (it's one long line of
     JSON — that's fine).
5. Click **Create Web Service**. First deploy takes 2–3 minutes.

You'll get a URL like:
```
https://pricescope-api.onrender.com
```

## Step 4 — Test it

Visit these in your browser once it's live:
- `https://pricescope-api.onrender.com/` → should show `{"status":"ok",...}`
- `https://pricescope-api.onrender.com/api/products/` → 10 products
- `https://pricescope-api.onrender.com/api/prices/` → live simulated prices
- `https://pricescope-api.onrender.com/api/history/p1` → 1 year of history
- `https://pricescope-api.onrender.com/api/alerts/` → AI alerts

Add `?save=true` to `/api/prices/` to also write a snapshot into your
Firestore database — check the **Firestore Database** tab in Firebase
console afterward to see the `price_snapshots` collection appear.

## Step 5 — Connect your frontend to this backend

In your frontend's `js/app.js` (or `data.js`), replace the hardcoded/mock
data calls with fetch calls to your new API, e.g.:

```js
const API_BASE = "https://pricescope-api.onrender.com/api";

async function loadProducts() {
  const res = await fetch(`${API_BASE}/products/`);
  const data = await res.json();
  return data.products;
}
```

Then commit that change to your **frontend** GitHub repo (`pricescope`) —
Render auto-redeploys it within ~30 seconds, same as before.

## Notes & gotchas

- **Free-tier spin-down**: unlike your static frontend, this is a real
  Python web service, so on Render's free plan it *does* spin down after
  15 min of inactivity. First request after a gap takes 30–60s to wake up.
  This is normal — fine for demos, not for guaranteed-instant production.
- **CORS**: `main.py` currently allows all origins (`*`). Once both sites
  are live, tighten this to your actual frontend URL for safety.
- **Real scraping later**: this version uses a deterministic simulator
  (`scraper/simulator.py`) so prices look realistic without hitting
  external sites. Swapping in real scraping (Playwright/BeautifulSoup) only
  requires replacing the functions in that one file — the API contract for
  your frontend stays the same.
