# 🔌 Embeddable Widget & Lead-Capture Platform

**FlyRank Internship · Backend Track · Capstone Project**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/tests-31%20passing-brightgreen.svg)](#-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-style, multi-tenant backend platform that lets customers create embeddable widgets (contact forms, newsletter signups, CTA popovers) and install them on **any website** with a single `<script>` tag.

This is the same architecture pattern behind Intercom's chat bubble, Mailchimp's signup forms, and HubSpot's lead popups: a config API, a public embed script, and a hardened public submission endpoint that safely accepts traffic from the open internet.

---

## 📋 Table of Contents

- [What This Solves](#-what-this-solves)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Local Development](#-setup--local-development)
- [Running the Demo (Dual-Origin)](#-running-the-demo-dual-origin)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Resiliency & Security Patterns](#-resiliency--security-patterns-implemented)
- [Definition of Done](#-definition-of-done)
- [Limitations](#-limitations)
- [Stretch Goal Implemented: Real-Time Dashboard](#-stretch-goal-implemented-real-time-dashboard)
- [Evidence & Build Log](#-evidence--build-log)
- [License](#-license)

---

## 🎯 What This Solves

The public internet is the input surface here — **you cannot trust it, control it, or predict it.** This project exercises the specific engineering disciplines needed to survive that:

| Challenge | How It's Solved |
|---|---|
| Untrusted cross-origin traffic | CORS + strict Pydantic boundary validation |
| Abuse / flooding | Per-IP rate limiting (`slowapi`) → `429` |
| Bots | Honeypot field spam filter |
| Flaky third-party dependencies | Two-provider geo fallback chain (never fails the request) |
| Side effects that shouldn't break the main path | Email notifications fail silently, submission still succeeds |
| Multi-tenant data | Every query scoped to `owner_id` / `tenant_id` |

---

## 🏗 Architecture

```text
Widget Owner (Authenticated — JWT)
  ├─ CRUD /api/widgets              → PostgreSQL (tenant-isolated)
  ├─ GET  /api/widgets/:id/snippet  → returns the <script> embed line
  └─ GET  /api/dashboard/*          → aggregated submissions + stats

Customer Website (External Origin, e.g. http://localhost:5500)
  └─ <script src="http://localhost:8000/widget.js?id=<uuid>">
       ├─ GET /api/widgets/:id/config   (public · cached · CORS)
       └─ renders vanilla-JS form directly in the page DOM

Website Visitor (the public internet)
  └─ POST /api/submissions          (public · CORS)
       ├─ Boundary validation   → 4xx on malformed / oversized input
       ├─ Honeypot spam check   → silently rejected if bot-filled
       ├─ IP rate limit         → 429 on burst
       ├─ Geo enrichment        → ip-api.com → fallback ipapi.co → degrade gracefully
       ├─ Persist submission    → idempotent, tenant-linked
       └─ Email notification    → safe side-effect, never blocks the 201

Widget Owner
  └─ GET /api/dashboard/stats  ◄── submissions, counts, geo breakdown
```

### Request Flow Diagram

```
┌─────────────┐     JWT      ┌──────────────┐     SQL      ┌─────────────┐
│ Widget Owner│ ───────────► │  FastAPI App │ ───────────► │ PostgreSQL  │
└─────────────┘              └──────┬───────┘              └─────────────┘
                                     │
                         Public (no auth)
                                     │
┌─────────────────┐   <script>   ┌──▼───────────┐
│ Customer Website│ ───────────► │  /widget.js  │
│ (diff. origin)  │ ◄─────────── │  + /config   │
└────────┬────────┘   renders   └──────────────┘
         │
         │ visitor submits form
         ▼
┌──────────────────┐
│ POST /submissions │──► validate ──► rate-limit ──► honeypot ──► geo ──► store ──► email
└──────────────────┘        │              │             │          │
                          4xx on         429 on       drop if     fallback
                           bad input      burst         bot        A→B→none
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| Database | PostgreSQL 16 (via Docker) |
| ORM & Migrations | SQLAlchemy 2.0 + Alembic |
| Auth | JWT (`python-jose`) + `bcrypt` password hashing |
| Validation | Pydantic v2 |
| Rate Limiting | `slowapi` (in-memory, per-IP) |
| Geo Providers | `ip-api.com` (A) → `ipapi.co` (B) |
| Email (dev) | Console log / Mailpit (local SMTP catcher) |
| Testing | `pytest`, `pytest-asyncio`, `httpx` |
| Containerization | Docker Compose (Postgres + Mailpit) |

---

## 📁 Project Structure

```
flyrank-capstone-widget-platform/
├── app/
│   ├── main.py                  # FastAPI app, CORS, rate limiter, routers
│   ├── api/                     # Route handlers
│   │   ├── auth.py
│   │   ├── widgets.py
│   │   ├── submissions.py
│   │   └── dashboard.py
│   ├── core/
│   │   ├── config.py             # Settings (pydantic-settings)
│   │   └── security.py           # JWT + password hashing
│   ├── db/
│   │   └── session.py            # SQLAlchemy engine/session
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── widget.py
│   │   └── submission.py
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── widget.py
│   │   └── submission.py
│   ├── services/                 # Business logic layer
│   │   ├── user_service.py
│   │   ├── widget_service.py
│   │   ├── submission_service.py
│   │   ├── geo_service.py        # Fallback chain: A → B → none
│   │   ├── event_broadcaster.py
│   │   └── notification_service.py  # Safe side-effect
│   └── middleware/
│       └── rate_limiter.py
│   ├── docs/                 # Business logic layer
│       └──  screenshots/...
├── static/
│   ├── dashboard.html
│   └── widget.js                 # The embeddable widget script
├── test_site/
│   └── index.html                # "Customer website" (different origin)
├── tests/                        # Automated test suite (31 tests)
├── alembic/
│   ├── env.py
│   └── script.py.mako
├── seed.py                       # Demo data seeder
├── docker-compose.yml            # Postgres + Mailpit
├── requirements.txt
├── capstone.yaml                 # Evaluator manifest
├── EVIDENCE.md                   # Proof per Definition-of-Done checkbox
├── BUILDLOG.md                   # AI usage disclosure
├── design-doc.md                 # Phase 1 design document
└── README.md
```

---

## 🚀 Setup & Local Development

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/JIYA-YDV/flyrank-internship-tracker.git
cd flyrank-internship-tracker/Capstone/flyrank-capstone-widget-platform
```

### 2. Environment variables

```bash
cp .env.example .env
```
No changes needed for local development — all defaults work out of the box.

### 3. Start PostgreSQL and Mailpit

```bash
docker compose up -d
```

Verify:
```bash
docker compose ps
```
Both `db` and `mailpit` should show `Up`.

### 4. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Seed demo data

```bash
python seed.py
```

The script prints:
- Demo login credentials (`demo@example.com` / `demo1234`)
- Widget UUIDs (e.g. Contact Form, Newsletter Signup)

**Copy the "Contact Form" UUID** — you'll need it in the next step.

---

## 🎬 Running the Demo (Dual-Origin)

This project proves cross-origin embedding by running the API and the "customer website" on **two different local ports** (two different origins), exactly the way a real customer's site would differ from FlyRank's servers.

### 1. Wire the widget ID into the test site

Open `test_site/index.html` and replace the placeholder:

```html
<script src="http://localhost:8000/widget.js?id=REPLACE_WITH_WIDGET_ID"></script>
```

with the real UUID from the seed output:

```html
<script src="http://localhost:8000/widget.js?id=a3f2c8e1-4b5d-4e9a-9c1f-8d7e6a5b4c3d"></script>
```

### 2. Start the API — Terminal 1

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Start the customer site — Terminal 2

```bash
cd test_site
python -m http.server 5500
```

### 4. Open the browser

Navigate to **http://localhost:5500** (not `file://`).

You should see a fully rendered "Get in Touch" form under the "Contact Us" section, loaded live from the API on port `8000`.

| URL | Purpose |
|---|---|
| http://localhost:5500 | Customer website (widget renders here) |
| http://127.0.0.1:8000/docs | Interactive Swagger API docs |
| http://127.0.0.1:8000/health | Health check |
| http://127.0.0.1:8025 | Mailpit inbox (if using Docker SMTP) |

---

## 📖 API Documentation

Full interactive docs (Swagger UI) live at **http://127.0.0.1:8000/docs** while the server is running.

### Auth

| Method | Route | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | No | Register a new tenant/user |
| POST | `/api/auth/login` | No | Obtain JWT bearer token |

### Widgets (authenticated, tenant-isolated)

| Method | Route | Auth | Purpose |
|---|---|---|---|
| POST | `/api/widgets` | Yes | Create a new widget |
| GET | `/api/widgets` | Yes | List your widgets |
| GET | `/api/widgets/{id}` | Yes | Get one widget |
| PUT | `/api/widgets/{id}` | Yes | Update a widget (bumps version) |
| DELETE | `/api/widgets/{id}` | Yes | Delete a widget |
| GET | `/api/widgets/{id}/snippet` | Yes | Get the `<script>` embed line |

### Public (no auth — the internet-facing surface)

| Method | Route | Auth | Purpose |
|---|---|---|---|
| GET | `/api/widgets/{id}/config` | No | Widget config (cached, `max-age=60`) |
| POST | `/api/submissions` | No | Submit form data (CORS, rate-limited, validated) |
| GET | `/widget.js` | No | Embeddable JS bundle (cached, `immutable`) |
| GET | `/widget.v{n}.js` | No | Versioned bundle URL |

### Dashboard (authenticated)

| Method | Route | Auth | Purpose |
|---|---|---|---|
| GET | `/api/dashboard/submissions` | Yes | Paginated submission list |
| GET | `/api/dashboard/stats` | Yes | Aggregated counts + geo breakdown |

### Example: Login → Create Widget → Get Snippet

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demo1234"}'

# 2. Create a widget (use the returned access_token)
curl -X POST http://127.0.0.1:8000/api/widgets \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Contact Form",
        "widget_type": "contact_form",
        "title": "Get in Touch",
        "fields_config": [
          {"name":"name","label":"Full Name","field_type":"text","required":true},
          {"name":"email","label":"Email","field_type":"email","required":true}
        ],
        "button_text": "Send"
      }'

# 3. Get the embed snippet
curl http://127.0.0.1:8000/api/widgets/<widget_id>/snippet \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 🧪 Testing

The suite covers all six required acceptance probes: happy path, validation failures, rate-limit bursts, spam rejection, geo fallback, and safe side-effect failure — plus multi-tenant isolation.

```bash
pytest -v
```

**31 tests, all passing:**

```text
tests/test_auth.py .......................... 6 passed
tests/test_widgets.py ...................... 9 passed
tests/test_submissions.py ................... 9 passed
tests/test_geo_fallback.py .................. 3 passed
tests/test_rate_limiting.py ................. 1 passed
tests/test_side_effects.py .................. 1 passed
tests/test_dashboard.py ..................... 3 passed
========================= 31 passed in ~4s =========================
```

### What's specifically tested

| Category | Test file | What it proves |
|---|---|---|
| Auth | `test_auth.py` | Register, login, wrong password rejected, protected routes need a token |
| Multi-tenancy | `test_widgets.py::test_tenant_isolation` | Tenant B gets `404` on Tenant A's widget |
| CORS | `test_submissions.py::test_cors_preflight` | `OPTIONS` returns `Access-Control-Allow-Origin` |
| Validation | `test_submissions.py` | Malformed JSON → `400`; missing field → `400`; oversized payload → `4xx` |
| Rate limiting | `test_rate_limiting.py` | Burst of requests → `429`, then normal traffic resumes |
| Spam | `test_submissions.py::test_honeypot_spam_rejection` | Filled honeypot → rejected |
| Geo fallback | `test_geo_fallback.py` | Provider A down → B answers; both down → still stores |
| Safe side-effects | `test_side_effects.py` | Email throws → submission still returns `201` |
| Dashboard | `test_dashboard.py` | Stats + tenant-scoped submission listing |

---

## 🛡 Resiliency & Security Patterns Implemented

1. **Validation at the boundary** — FastAPI/Pydantic rejects malformed or oversized payloads with `400`/`413` before they ever reach business logic. The API never throws an unhandled `500` on bad input.

2. **Graceful degradation (fallback chain)** — `GeoService` tries `ip-api.com` first. If it times out, errors, or returns a bad response, it tries `ipapi.co`. If both fail, the submission is stored with `country=None` — enrichment degrades, the request never fails.

3. **Safe side-effects** — `NotificationService.send_submission_notification()` wraps SMTP calls in a blanket `try/except`. A dead mail server is logged, never raised — the visitor still gets `201 Created`.

4. **Tenant isolation** — Every widget and submission query is filtered by `owner_id` / `tenant_id` at the service layer, not just hidden in the UI. Proven by automated tests, not just code review.

5. **Idempotency** — Submissions accept an optional `idempotency_key`; a retried request with the same key returns the original stored row instead of creating a duplicate.

6. **Abuse resistance** — Per-IP rate limiting (`slowapi`) plus a honeypot field stop both brute-force floods and simple bots without needing CAPTCHAs.

---

## ✅ Definition of Done

| Requirement | Status |
|---|:---:|
| Authenticated, tenant-isolated widget CRUD | ✅ |
| Embed snippet generated per widget | ✅ |
| Public config endpoint with cache headers | ✅ |
| Versioned widget bundle (`widget.js`, cache-busted) | ✅ |
| Widget renders on a genuinely different origin | ✅ |
| CORS + preflight correctly handled | ✅ |
| Input validated; bad/oversized payloads → clean 4xx | ✅ |
| Valid submissions stored, linked to widget + tenant | ✅ |
| Rate limiting → `429` under burst, service stays up | ✅ |
| Honeypot spam control | ✅ |
| Geo enrichment with two-provider fallback chain | ✅ |
| All geo providers down → submission still succeeds | ✅ |
| Failing email side-effect never blocks storage | ✅ |
| Owner dashboard: list + aggregated stats | ✅ |
| Automated tests for all of the above | ✅ (31/31 passing) |
|Stretch Goal Implemented: Real-Time Dashboard |✅|
| README, EVIDENCE.md, BUILDLOG.md, capstone.yaml | ✅ |

Full pasted proof for every checkbox above lives in **[`EVIDENCE.md`](EVIDENCE.md)**.

---

## ⭐ Stretch Goal Implemented: Real-Time Dashboard

New submissions appear on the dashboard **instantly** via Server-Sent Events —
no polling. Try it:

1. Open http://127.0.0.1:8000/dashboard
2. Click "Connect" (uses demo credentials by default)
3. In another terminal, POST a submission
4. Watch it appear on the page immediately

Built with an in-process `asyncio.Queue`-based pub/sub broadcaster — no Redis
or external message broker needed for this scale. Broadcasting is wired in as
a **safe side-effect**: if it fails, the submission still succeeds (same
discipline as the email notification).

## ⚠️ Limitations

- No real CDN, domain, or hosting — the "customer site" is a plain HTML file on a second local port, per the assignment's constraints.
- Widget UI is intentionally minimal (a styled `<div>` + form) — the grading surface is the backend, not the CSS.
- Rate limiter storage is in-memory (`slowapi`, `storage_uri="memory://"`) and resets on process restart. Fine for a single-instance demo; would need Redis for multi-instance production.
- Email notifications go to Mailpit (local) or console log — deliverability isn't graded, only failure-safety.
- Geo providers are mocked in automated tests for determinism; real APIs (`ip-api.com`, `ipapi.co`) are used only in manual/dev testing.
- No CAPTCHA/proof-of-work bot defense (listed as a stretch goal, not implemented in the core).

---

## 📄 Evidence & Build Log

- **[`EVIDENCE.md`](EVIDENCE.md)** — pasted test output, curl transcripts, and screenshots proving every Definition-of-Done checkbox.
- **[`BUILDLOG.md`](BUILDLOG.md)** — honest disclosure of where AI tools helped, what they got wrong, and what was manually fixed (e.g., the SQLite/JSONB cross-dialect bug, the JWT `sub` UUID coercion bug).
- **[`design-doc.md`](design-doc.md)** — the Phase 1 design document: data model, API surface, and explicit non-goals.
- **[`capstone.yaml`](capstone.yaml)** — machine-readable manifest for automated evaluation (`run`, `seed`, `test`, `base_url`, `endpoints`).

---

## 📝 License

MIT — see [`LICENSE`](LICENSE).
