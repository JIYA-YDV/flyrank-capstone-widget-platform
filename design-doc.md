# design-doc.md

## Problem
Customers need embeddable widgets for their websites. The system must securely handle
cross-origin submissions from the public internet.

## Data Model

### Users (tenants)
- id (UUID PK)
- email (unique)
- hashed_password
- company_name
- created_at, updated_at

### Widgets
- id (UUID PK)
- owner_id (FK → users, tenant isolation key)
- name, widget_type, title, description
- fields_config (JSONB — field definitions)
- button_text, display_options (JSONB)
- version (integer, increments on update)
- is_active, allowed_origins (JSONB)
- created_at, updated_at

### Submissions
- id (UUID PK)
- widget_id (FK → widgets)
- tenant_id (denormalized for fast dashboard queries)
- data (JSONB — submitted form values)
- ip_address, country, city, region, lat, lng
- geo_provider (which provider enriched it)
- user_agent, referrer
- is_spam, email_sent
- idempotency_key (unique, prevents duplicates)
- created_at

## API Surface

### Auth (POST /api/auth/register, POST /api/auth/login)
### Widgets — authenticated CRUD (GET/POST /api/widgets, GET/PUT/DELETE /api/widgets/{id})
### Snippet (GET /api/widgets/{id}/snippet)
### Config — public (GET /api/widgets/{id}/config)
### Submissions — public (POST /api/submissions)
### Dashboard — authenticated (GET /api/dashboard/submissions, GET /api/dashboard/stats)
### Widget JS — public (GET /widget.js)

## Embed Flow
1. Customer creates widget via API → gets snippet
2. Customer pastes `<script src="http://host/widget.js?id=xxx">` into their page
3. widget.js fetches config from /api/widgets/{id}/config
4. widget.js renders the form in the page
5. Visitor submits → POST /api/submissions (CORS)
6. Backend validates, rate-limits, spam-checks, geo-enriches, stores, emails

## Non-Goal
- No real-time editing UI for widgets. API-only management is sufficient.