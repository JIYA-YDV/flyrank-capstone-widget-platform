# Evidence — Definition of Done

## Widget Management
- [ ] Authenticated CRUD endpoints for widgets
- [ ] Multi-tenant isolation proven

## Widget Delivery
- [ ] Embed snippet generated per widget
- [ ] Public config endpoint with cache headers
- [ ] Versioned bundle served
- [ ] Widget renders on different-origin page

## Public Submission API
- [ ] CORS headers correct, preflight handled
- [ ] Input validated, malformed/oversized rejected with 4xx
- [ ] Valid submissions stored, linked to correct widget/tenant

## Abuse Protection
- [ ] Rate limiting returns 429 under burst
- [ ] Spam prevention blocks spam submission

## Enrichment & Safe Side Effects
- [ ] Geo enrichment with fallback chain
- [ ] All providers down → submission still succeeds
- [ ] Failing email/webhook does not prevent submission storage

## Tests & Documentation
- [ ] Automated tests cover required scenarios
- [ ] README with architecture diagram and setup instructions