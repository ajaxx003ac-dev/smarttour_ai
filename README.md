# SMARTTOUR AI — AI-Powered Smart Tourism Ecosystem

Competition-ready full-stack prototype for AICTE/MIC Student Innovation, Travel & Tourism.

## What makes it different

SMARTTOUR AI is **not a generic booking site**. Its core demo loop is:

**tourist intent → AI itinerary → crowd intelligence → disruption simulation → automatic re-planning → local business recommendation → tourism authority analytics**.

The prototype uses deterministic AI/recommendation logic so it works without a paid LLM or maps API. An LLM can be added later through environment variables.

## Stack

- Frontend: HTML + CSS + JavaScript
- Backend: FastAPI + SQLAlchemy
- Database: MySQL (SQLite fallback for zero-setup demo)
- Map: MapLibre GL JS + OpenStreetMap raster tiles
- Auth: JWT + role model (Tourist / Business / Admin)
- Charts: CSS analytics bars in the zero-dependency prototype; MapLibre for maps
- AI: transparent weighted recommendation engine + tourism assistant; optional LLM adapter point

## Project structure

```text
smarttour-ai/
  backend/
    app/
      ai.py
      config.py
      db.py
      main.py
      models.py
      schemas.py
      security.py
      seed.py
    requirements.txt
    .env.example
    schema.sql
    run.py
  frontend/
    index.html
    css/styles.css
    js/app.js
  README.md
```

## Demo accounts

All demo accounts use password `demo123`.

- Tourist: `tourist@smarttour.ai`
- Business: `business@smarttour.ai`
- Admin: `admin@smarttour.ai`

Change passwords before any real deployment.

# Deployment on Windows — NO Docker required

## 1. Install prerequisites

Install:

1. Python 3.11+.
2. MySQL Community Server 8+ and MySQL Workbench (optional but useful).
3. A modern browser.

You do **not** need Docker Desktop.

## 2. Create the MySQL database

Open MySQL Workbench or MySQL Command Line Client and run:

```sql
CREATE DATABASE smarttour CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Create a MySQL user if desired:

```sql
CREATE USER 'smarttour_user'@'localhost' IDENTIFIED BY 'StrongPasswordHere';
GRANT ALL PRIVILEGES ON smarttour.* TO 'smarttour_user'@'localhost';
FLUSH PRIVILEGES;
```

## 3. Configure backend

Open Command Prompt in `backend`:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=mysql+pymysql://smarttour_user:StrongPasswordHere@localhost:3306/smarttour
JWT_SECRET=replace-with-a-long-random-secret
```

If you already have MySQL with root credentials, use:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/smarttour
```

## 4. Start API

```bat
python run.py
```

API runs at `http://localhost:8000`.

Health check: `http://localhost:8000/api/health`

FastAPI documentation: `http://localhost:8000/docs`

The database tables and demo records are created automatically at startup.

## 5. Start frontend

Do not open `index.html` directly if your browser blocks local requests. Start a simple static server.

Open a second Command Prompt in `frontend`:

```bat
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The frontend expects the API at `http://localhost:8000/api`. If your backend uses another host/port, set this in the browser console before refresh:

```js
localStorage.setItem('smarttour_api','http://YOUR_HOST:8000/api')
```

## 6. Five-to-ten-minute competition demo

### Step A — Tourist

Open **AI Planner** and enter:

- Destination: Jaipur
- Days: 3
- Travelers: 4
- Budget: ₹12,000
- Interests: history,food
- Pace: relaxed
- Food: local,vegetarian
- Transport: public

Click **Generate AI itinerary**.

Explain that the score combines:

`Preference + Budget + Distance + Availability + Safety + Sustainability - Crowd Penalty`

### Step B — Crowd disruption

Click **Simulate Amber Fort crowd 92%**.

The backend updates Amber Fort crowd and regenerates the itinerary with crowd avoidance enabled.

Use this line during judging:

> “The itinerary is not static. When crowd pressure changes, the recommendation function changes the destination mix instead of forcing the tourist to follow the original plan.”

### Step C — Local business

Open **Explore** and show restaurants, homestays, guides and handicraft businesses. Explain that local recommendations are ranked by destination, category, price, rating and availability.

### Step D — Business impact

Open **Business**. Show bookings, occupancy, demand, revenue and the AI package recommendation.

### Step E — Authority impact

Open **Admin**. Show crowd monitor, destination demand and the impact insight. Explain that authorities can identify over-visited and under-visited locations.

### Step F — Assistant + safety

On Home, ask:

- “What can I do if it rains?”
- “Find a restaurant under ₹500.”
- “Which attraction is less crowded?”

Then open Safety and demonstrate the SOS simulation.

## OpenStreetMap note

The map uses OpenStreetMap tiles through MapLibre. There is no Google Maps API key. For a public production launch, follow OpenStreetMap tile usage policies and consider a dedicated OSM-compatible tile provider for higher traffic.

## Production hardening checklist

Before public deployment:

- Put the FastAPI service behind HTTPS and a reverse proxy.
- Set a strong random `JWT_SECRET`.
- Replace demo passwords and add password reset/email verification.
- Restrict CORS to the production frontend origin.
- Add rate limiting, audit logs and structured logging.
- Move secrets to environment/secret management.
- Use a managed MySQL instance with backups.
- Add real weather, traffic, transit, attraction availability and payment providers only where required.
- Add real geospatial routing and verified emergency data.
- Use a dedicated OSM-compatible tile/routing provider for production traffic.
- Add automated tests and CI/CD.

## Optional real LLM

The current app is deliberately functional without an LLM. For competition judging, this avoids a broken demo caused by API quotas. To integrate an OpenAI-compatible provider, add these environment variables and implement the provider call in `backend/app/ai.py`:

```env
LLM_API_KEY=...
LLM_BASE_URL=https://...
LLM_MODEL=...
```

Keep the deterministic scorer as the fallback so the system remains demo-safe.

## API overview

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/attractions`
- `GET /api/businesses`
- `POST /api/planner`
- `POST /api/trips/{trip_id}/simulate-event`
- `POST /api/assistant`
- `POST /api/bookings`
- `GET /api/safety`
- `GET /api/business/dashboard`
- `GET /api/admin/overview`

## Innovation/impact story

### Tourist
Personalized, adaptive and safer trips.

### Local business
Demand generated by context-aware recommendations rather than only popularity-based discovery.

### Tourism authority
A demand-distribution layer that can reduce pressure on iconic sites and surface emerging destinations.

### Sustainability
The planner scores transport mode, local-business participation and crowd distribution, creating a measurable sustainability signal.

# Real AI / LLM integration

The project now supports a real LLM through the backend-only OpenAI Responses API. The browser never receives the API key. OpenAI's current Responses API returns generated text through the response output, and the official quickstart uses `responses.create(...)` with a model and input. See the OpenAI API documentation for current model availability and pricing.

Set these values in `backend/.env`:

```env
OPENAI_API_KEY=your_real_api_key
LLM_MODEL=gpt-5.6-luna
# Optional OpenAI-compatible endpoint:
# LLM_BASE_URL=https://api.openai.com/v1
```

If `OPENAI_API_KEY` is missing, SMARTTOUR automatically falls back to its deterministic tourism engine, so the competition demo still works offline.

## What the LLM does

- **AI Trip Planner:** the deterministic engine first selects real seeded attractions/businesses using crowd, budget, safety, sustainability and preference signals. The LLM then turns that grounded plan into natural-language trip guidance and reasons without inventing database facts.
- **AI Tourist Assistant:** the assistant receives the current destination's seeded attractions and local businesses as context, then answers the tourist's question with the LLM.
- **Dynamic re-planning:** crowd events are still evaluated by the deterministic optimization engine; the LLM explains the optimized result instead of being trusted with safety-critical numeric decisions.
- **AI status:** `GET /api/ai/status` reports whether the real LLM is enabled.

## Recommended competition setup

For a live judging demo, configure the API key on the backend machine only, run FastAPI, and demonstrate the same planner + crowd simulation flow. Never put the API key into frontend JavaScript or commit `.env` to source control.
