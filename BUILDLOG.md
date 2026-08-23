# Build Log

Honest disclosure of AI-assisted work, mistakes made, and what was learned —
per program rule: "AI-assisted building is encouraged — and owned."

---

## Phase 1 — Design

- Used AI to brainstorm the initial database schema (users, widgets, submissions).
  Manually reviewed and added a denormalized `tenant_id` column on `Submission`
  for fast dashboard queries without joining through `Widget` every time.
- Used AI to draft the first version of Pydantic schemas. Manually added the
  `@field_validator` for `widget_type` (restricting to `signup_form` /
  `contact_form` / `cta_popover`) and the payload-size validator on
  `SubmissionCreate.data`.

## Phase 2 — Hardened Submission Path

- Used AI to help structure `GeoService`'s two-provider fallback chain. Verified
  and rewrote the exception handling myself — the first AI draft only caught
  `httpx.HTTPStatusError` and missed plain connection/timeout exceptions, which
  would have broken the "degrade, never fail" requirement.
- Used AI to draft the honeypot spam field. Renamed the field from a generic
  suggestion to `_hp_field` and made sure it's excluded from required-field
  validation.
- Rate limiting (`slowapi`) decorator syntax was AI-assisted; the limit value
  and the exception handler wiring in `main.py` were manually verified against
  the slowapi docs.

## Phase 3 — Delivery & Dashboard

- Used AI to draft `static/widget.js`. Substantially rewrote the form-rendering
  loop and the honeypot injection — the first draft didn't include the hidden
  field at all, which would have defeated the spam control.
- Dashboard aggregation queries (`by_widget`, `by_country`) were AI-assisted.
  Fixed an incorrect timezone-naive `datetime.now()` call that broke the
  "submissions today" filter — replaced with `datetime.now(timezone.utc)`.
- Test suite scaffolding was AI-suggested. The geo-fallback mocks needed a full
  rewrite: the initial version mocked the `requests` library, but the service
  uses `httpx.AsyncClient` — had to redo the mocks with `AsyncMock` and correct
  `__aenter__`/`__aexit__` context manager behavior.

## Phase 4 — Debugging Session (Post Phase 3)

- **SQLite/JSONB compatibility bug:** Tests failed with
  `UnsupportedCompilationError: can't render element of type JSONB` because the
  models used PostgreSQL's native `JSONB` type directly, but tests run against
  SQLite. Fixed by using
  `JSON().with_variant(JSONB(), "postgresql")` so the same model works on both
  dialects. This was a bug I found and fixed myself after reading the
  SQLAlchemy traceback — AI's first suggestion for this was incomplete (it
  removed JSONB entirely rather than making it dialect-conditional, which would
  have lost the PostgreSQL-native performance benefit in production).
- **JWT `sub` UUID coercion bug:** Authenticated requests failed with
  `AttributeError: 'str' object has no attribute 'hex'` because
  `get_current_user` compared a `str` (from the decoded JWT `sub` claim)
  directly against a `UUID`-typed column. Fixed by explicitly converting with
  `uuid.UUID(user_id_str)` before the query. Found via the pytest traceback,
  fixed manually.
- **Repo structure mistake:** Initially built the capstone inside the
  assignments-track repository instead of its own standalone public repo, in
  violation of the program's "one separate, public repo" rule. Fixed by
  extracting the folder into `flyrank-capstone-widget-platform` as its own
  git-initialized, GitHub-hosted repository, and removing it from the
  assignments repo.

## What AI got wrong (explicit list)

1. First CORS middleware draft used `allow_credentials=True` combined with
   `allow_origins=["*"]` — browsers reject this combination outright. Fixed per
   MDN's CORS guide to use `allow_credentials=False` since the public
   submission endpoint doesn't need cookies.
2. Geo-provider mocks initially assumed a synchronous `requests` call; the real
   service uses async `httpx`. Had to rewrite every geo test with proper
   `AsyncMock`.
3. JSONB column type worked in the AI's example but was never tested against
   SQLite, causing the entire test suite to fail at fixture setup until fixed.
4. Seed script's first draft logged the demo password in a way that looked like
   it was encouraging shipping real plaintext credentials into logs — removed
   and clarified it's for local dev only.

## What I learned

- **CORS preflight debugging is genuinely a different skill** than normal
  backend debugging — the browser gives almost no useful error message, and
  you have to reason about it from the spec (MDN) rather than the console.
- **The fallback-chain pattern is more than "try/except twice."** You need to
  decide: what counts as "provider is down" (timeout? bad status? malformed
  JSON?), and make sure each layer degrades cleanly into the next without
  leaking exceptions upward.
- **Safe side-effects require a deliberate boundary.** It's not enough to wrap
  the email call in try/except — you have to make sure that boundary is placed
  *after* the database commit, so the submission is durable regardless of what
  happens next.
- **Cross-dialect ORM code needs to be tested against both databases early.**
  Building against PostgreSQL-only types and only discovering the SQLite
  incompatibility at test time cost real debugging time that could have been
  avoided by using `.with_variant()` from the start.