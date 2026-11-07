# Resume Optimizer

AI-powered LaTeX resume optimizer that tailors your resume to specific job descriptions while preserving your exact template. Built with a FastAPI backend (Claude-powered), a Next.js web dashboard, and a Chrome extension that scrapes job postings directly from career portals.

## Architecture

```
                     Chrome Extension
                ┌──────────────────────────┐
                │  Content Script (scraper) │
                │  Background (API relay)   │
                │  Sidebar (React)          │
                └────────────┬─────────────┘
                             │
    Next.js Web App          │
  ┌──────────────────┐       │
  │  Dashboard        │       │
  │  DiffViewer        │───────┼───► FastAPI Backend
  │  Resume Manager    │       │     ├── LaTeX Parser
  └──────────────────┘       │     ├── LLM Engine (Claude)
                             │     ├── ATS Scorer
                             │     ├── LaTeX Compiler
                             │     └── PostgreSQL
                             │
```

**Three main modules:**

| Module | Tech | Purpose |
|---|---|---|
| `backend/` | FastAPI, SQLAlchemy, Anthropic SDK | API server: parses LaTeX, runs the 3-stage LLM pipeline, compiles PDFs, stores versions |
| `web/` | Next.js 15, Tailwind, shadcn/ui | Dashboard: application tracker (kanban), diff viewer, resume manager |
| `extension/` | Vite, React, Chrome Manifest V3 | Browser extension: scrapes JDs from job portals, sidebar with optimize flow |

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Docker** (for PostgreSQL and LaTeX compilation)
- **Anthropic API key** (Claude access)
- **Google Cloud project** with OAuth 2.0 credentials (for authentication)
- **pdflatex** (or use the Docker TeX Live container)

---

## Project Setup

### 1. Clone and navigate

```bash
git clone https://github.com/suyeon240park/resume-optimizer.git
cd resume-optimizer
```

### 2. Backend setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv

# Activate it
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies (including dev extras)
pip install -e ".[dev]"

# Copy the example env file and fill in your values
cp .env.example .env
```

Edit `.env` with your actual credentials:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resume_optimizer
ANTHROPIC_API_KEY=sk-ant-your-actual-key
LATEX_COMPILE_DIR=/tmp/latex-compile
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
JWT_SECRET=<run: python -c "import secrets; print(secrets.token_hex(32))">
CORS_ORIGINS=http://localhost:3000
```

> **Security note:** `JWT_SECRET` has no default and is required. The server will not start without it. Generate a strong random value; never reuse across environments.

### 3. Start the database

```bash
# From backend/
docker compose up -d db
```

This starts PostgreSQL 16 on port 5432.

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### 6. Run backend tests

```bash
python -m pytest tests/ -v
```

### 7. Web app setup

```bash
cd ../web

# Install dependencies
npm install

# Copy env example
cp .env.local.example .env.local
```

Edit `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### 8. Start the web app

```bash
npm run dev
```

The dashboard is now running at `http://localhost:3000`.

### 9. Chrome extension setup

```bash
cd ../extension

# Install dependencies
npm install

# Copy env example and configure
cp .env.example .env
```

Edit `.env`:

```
VITE_API_URL=http://localhost:8000
VITE_WEB_URL=http://localhost:3000
```

Build the extension:

```bash
npm run build
```

> **Note:** `VITE_API_URL` and `VITE_WEB_URL` are inlined at build time by Vite. You must rebuild after changing them.

### 10. Load the extension in Chrome

1. Open `chrome://extensions/` in Chrome.
2. Enable **Developer mode** (top-right toggle).
3. Click **Load unpacked**.
4. Select the `extension/dist` directory.
5. The extension is now active. Navigate to any supported job posting to see the floating "R" button.

---

## Security Model

### Authentication

All API endpoints (except `/api/auth/*`) require a `Bearer` JWT in the `Authorization` header. Tokens are issued via Google OAuth.

### CORS

CORS origins are configured via the `CORS_ORIGINS` environment variable (comma-separated). Default: `http://localhost:3000`. Set this to your production web dashboard URL in deployment.

### Rate Limiting

Global rate limit: **60 requests/minute** per IP (via `slowapi`). LLM-consuming endpoints (`/optimize`, `/scrape`) are further limited to **10 requests/minute**. The `/apply` endpoint is capped at **20 requests/minute**.

### Input Validation

All text inputs have `max_length` constraints (JD text: 50K chars, LaTeX source: 200K chars, mutations capped at 100 per request). Mutation types are constrained to `edit|add|remove|reorder` via regex validation.

### LaTeX Compilation

`pdflatex` runs with `--no-shell-escape` to prevent code execution. The Docker container runs as a non-root `appuser`. A `.dockerignore` prevents secrets from being copied into the image.

### Extension Security

- **Background service worker** validates sender identity (only extension pages can issue `API_CALL`, `SET_TOKEN`, `GET_TOKEN`).
- **API path allowlist** uses regex patterns with path boundary checks to prevent prefix collisions and path traversal.
- **postMessage** uses the extension origin (not `"*"`) and the sidebar validates `event.origin`.
- **Content scripts** are scoped to known job board domains and job-URL patterns (not `<all_urls>`).

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string (must use `postgresql+asyncpg://` driver) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `JWT_SECRET` | Yes | Secret for signing JWTs — no default, must be set |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 client ID |
| `LATEX_COMPILE_DIR` | No | Defaults to `/tmp/latex-compile` |
| `CORS_ORIGINS` | No | Comma-separated allowed origins. Defaults to `http://localhost:3000` |

### Web (`web/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 client ID |

### Extension (`extension/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Backend API URL (inlined at build time) |
| `VITE_WEB_URL` | Yes | Web dashboard URL (inlined at build time) |

---

## Google OAuth Setup

Both the web app and extension use Google Sign-In. You need a Google Cloud OAuth 2.0 Client ID.

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services > Credentials**.
4. Click **Create Credentials > OAuth 2.0 Client ID**.
5. Application type: **Web application**.
6. Add **Authorized JavaScript origins**:
   - `http://localhost:3000` (for local dev)
   - Your production domain
7. Add **Authorized redirect URIs**:
   - `http://localhost:3000` (for local dev)
8. Copy the **Client ID** and paste it into:
   - `backend/.env` as `GOOGLE_CLIENT_ID`
   - `web/.env.local` as `NEXT_PUBLIC_GOOGLE_CLIENT_ID`

---

## Production Deployment

### Backend (Railway / Docker)

1. Push to GitHub.
2. Deploy from the `backend/` directory (Railway detects the `Dockerfile` automatically).
3. Add a PostgreSQL database in Railway.
4. Set environment variables:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
ANTHROPIC_API_KEY=your-production-key
JWT_SECRET=<strong-random-64-char-hex>
GOOGLE_CLIENT_ID=your-production-client-id
CORS_ORIGINS=https://your-web-dashboard.vercel.app
LATEX_COMPILE_DIR=/tmp/latex-compile
```

> **Note:** Railway provides `DATABASE_URL` as `postgresql://...`. The backend automatically converts it to `postgresql+asyncpg://...` at runtime.

5. Generate a public domain under **Settings > Networking**.

**Railway networking:** The Dockerfile listens on the `PORT` environment variable that Railway injects (with a fallback of `8000` for local Docker). If Uvicorn is bound to a fixed port while Railway’s proxy targets `$PORT`, the public URL will show **“Application failed to respond”** even though logs show the server started.

### Web (Vercel / any Node host)

```bash
cd web
npm run build
```

Set `NEXT_PUBLIC_API_URL` to your production backend URL.

Deploy the web app and note its URL (for example `https://your-app.vercel.app`). The login page lives in **Next.js**, not in FastAPI—there is no `/login` route on the API.

### Extension (Chrome Web Store)

1. Set production URLs in `extension/.env`:

```
VITE_API_URL=https://your-api.up.railway.app
VITE_WEB_URL=https://your-web-dashboard.vercel.app
```

`VITE_API_URL` must be your **FastAPI** base URL. `VITE_WEB_URL` must be your **Next.js dashboard** base URL (same host you use in the browser for the web app). Do not point both at the Railway API service, or **Open Dashboard** will open `/login` on the wrong host.

2. Rebuild: `cd extension && npm run build`
3. ZIP the `dist/` directory and upload to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole).

---

## API Reference

All endpoints require a `Bearer` token in the `Authorization` header (except `/api/auth/*`).

### Authentication

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/google` | Exchange a Google ID token for a JWT pair |
| POST | `/api/auth/refresh` | Rotate access token using a refresh token |

### Resumes

| Method | Path | Description |
|---|---|---|
| POST | `/api/resumes` | Upload a LaTeX resume |
| GET | `/api/resumes` | List all resumes (`?limit=&offset=`) |
| GET | `/api/resumes/:id` | Get resume detail (includes parsed sections) |
| PATCH | `/api/resumes/:id` | Update resume name or source |
| DELETE | `/api/resumes/:id` | Delete a resume |

### Applications

| Method | Path | Description |
|---|---|---|
| POST | `/api/applications` | Create an application (with JD text) |
| GET | `/api/applications` | List applications (`?status=&limit=&offset=`) |
| GET | `/api/applications/:id` | Get application detail (includes JD snapshot) |
| PATCH | `/api/applications/:id` | Update status |
| DELETE | `/api/applications/:id` | Delete application |
| GET | `/api/applications/:id/versions` | List resume versions (`?limit=&offset=`) |

### Optimization (rate-limited: 10/min)

| Method | Path | Description |
|---|---|---|
| POST | `/api/applications/:id/optimize` | Run the 3-stage LLM pipeline, returns proposed mutations |
| POST | `/api/applications/:id/apply` | Apply approved mutations, create a new version (20/min) |

### Compilation

| Method | Path | Description |
|---|---|---|
| POST | `/api/versions/:id/compile` | Compile LaTeX to PDF |
| GET | `/api/versions/:id/pdf` | Download compiled PDF (compiles on demand if needed) |
| GET | `/api/versions/:id/diff/:other_id` | Compare two versions |

---

## Project Structure

```
resume-optimizer/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # HTTP endpoints
│   │   ├── core/               # Business logic
│   │   │   ├── latex_parser.py # LaTeX AST extraction + reconstruction
│   │   │   ├── llm_engine.py   # 3-stage Claude pipeline
│   │   │   ├── ats_scorer.py   # Keyword matching + scoring
│   │   │   ├── auth.py         # JWT + Google OAuth
│   │   │   └── compiler.py     # pdflatex subprocess
│   │   ├── db/                 # SQLAlchemy models + Alembic migrations
│   │   ├── schemas/            # Pydantic request/response models
│   │   └── rate_limit.py       # Shared rate limiter instance
│   ├── tests/
│   ├── .dockerignore
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── pyproject.toml
├── web/                        # Next.js 15 dashboard
│   └── src/
│       ├── app/                # App Router pages
│       ├── components/         # UI components (kanban, diff viewer, etc.)
│       ├── hooks/              # React Query hooks
│       └── lib/                # API client, auth, types
├── extension/                  # Chrome Manifest V3 extension
│   ├── public/manifest.json
│   ├── .env.example
│   └── src/
│       ├── config.ts           # Shared API_URL and WEB_URL from env
│       ├── content/            # Content script + portal scrapers
│       ├── background/         # Service worker (API relay + auth)
│       └── sidebar/            # React app (optimize flow)
├── .gitignore
└── README.md
```

---

## Key Technical Decisions

- **LaTeX-first**: Unlike competitors that force proprietary editors, we parse and reconstruct real LaTeX with byte-accurate source offsets, preserving the user's exact template.
- **3-stage LLM pipeline**: JD analysis, resume-JD alignment scoring, and mutation generation run as separate Claude calls for better control and debuggability.
- **Brace-aware parsing**: The LaTeX parser handles nested braces (e.g., `{O(n \log n)}`) correctly instead of using fragile regex.
- **Reverse-order replacement**: Multiple mutations are applied from the end of the file backwards to avoid invalidating source offsets.
- **Message-passing architecture**: The Chrome extension sidebar never holds auth tokens or makes direct API calls. Everything flows through the background service worker with sender validation and path allowlisting.
- **Zero-trust API proxy**: The background service worker validates every API call against a regex-based path allowlist, rejects path traversal, and only accepts messages from extension pages (not content scripts).

## Sample Data and Human Review

The test fixture in `backend/tests/fixtures/jake_resume.tex` contains Jake's
sample resume, with its original author and template attribution. It is demo
data and does not describe the project author's work history.

Optimization produces proposed changes for review. Users can approve, reject,
or edit suggestions before applying them to a new version. The generation
prompt instructs Claude to preserve factual experience; users must verify the
suggestions themselves. This prompt is guidance, not a guarantee against
incorrect output. No real candidate data or API credentials are needed to run
the mocked backend tests.

For a portfolio demo, use this sample resume and a fictional job description;
show the before/after review screen and the approval controls. Do not include
private resumes, application records, or credentials in screenshots.

## Repository Hygiene

Copy `extension/.env.example` to `extension/.env` and set your local URLs before
building the extension. Environment files, generated Python package metadata,
and extension ZIP bundles are ignored. Create distribution bundles locally
from `extension/dist/` after configuring and rebuilding the extension.

The repository history retains previous versions of tracked files. Removing a
file from the current branch does not remove it from earlier commits.

## License

[MIT](LICENSE). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the
sample resume template's attribution and upstream license notice.

