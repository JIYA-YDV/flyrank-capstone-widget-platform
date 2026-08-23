# Evidence — Definition of Done

This document provides one pasted proof per checkbox from the capstone brief §6.
All screenshots referenced below live in `docs/screenshots/`.

## Setup Before Collecting Evidence

![01-docker-compose-and-migrations](docs/screenshots/01-docker-compose-and-migrations-1.png)

![02-database-seed-success](docs/screenshots/02-database-seed-success.png)

## Widget Management

### ☑ Authenticated CRUD endpoints for widgets; unauthenticated requests rejected

**No token → rejected:**

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i http://127.0.0.1:8000/api/widgets
HTTP/1.1 403 Forbidden
date: Sun, 23 Aug 2026 05:03:19 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"detail":"Not authenticated"}

![03-unauthenticated-widgets-access](docs/screenshots/03-unauthenticated-widgets-access.png)

**With valid token → succeeds:**

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -X POST http://127.0.0.1:8000/api/auth/login `
>>   -H "Content-Type: application/json" `
>>   -d "{\`"email\`":\`"demo@example.com\`", \`"password\`":\`"demo1234\`"}"
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZTE5YTdmMy03YWI5LTQyNzctYjU4Mi1jOGVkMDk0ODg2MWIiLCJleHAiOjE3ODc0NjUwNTB9.rIVUFlTu58EFzWfPSLgxNKOfuNxA9fDKQV1-SeZNfxs","token_type":"bearer"}
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> $TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZTE5YTdmMy03YWI5LTQyNzctYjU4Mi1jOGVkMDk0ODg2MWIiLCJleHAiOjE3ODc0NjUwNTB9.rIVUFlTu58EFzWfPSLgxNKOfuNxA9fDKQV1-SeZNfxs"
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe http://127.0.0.1:8000/api/widgets `
>>   -H "Authorization: Bearer $TOKEN"
[{"id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","owner_id":"8e19a7f3-7ab9-4277-b582-c8ed0948861b","name":"Contact Form","widget_type":"contact_form","title":"Get in Touch","description":"We'd love to hear from you. Fill out the form below.","fields_config":[{"name":"name","label":"Full Name","required":true,"field_type":"text","placeholder":"John Doe"},{"name":"email","label":"Email Address","required":true,"field_type":"email","placeholder":"john@example.com"},{"name":"message","label":"Message","required":true,"field_type":"textarea","placeholder":"Your message..."}],"button_text":"Send Message","display_options":{"theme":"light"},"version":1,"is_active":"active","allowed_origins":[],"created_at":"2026-08-23T04:58:13.626267Z","updated_at":"2026-08-23T04:58:13.626267Z"},{"id":"1d751f41-4296-497a-9a24-2d80c0990a45","owner_id":"8e19a7f3-7ab9-4277-b582-c8ed0948861b","name":"Newsletter Signup","widget_type":"signup_form","title":"Subscribe to Our Newsletter","description":"Get the latest updates delivered to your inbox.","fields_config":[{"name":"email","label":"Email","required":true,"field_type":"email","placeholder":"you@example.com"},{"name":"first_name","label":"First Name","required":false,"field_type":"text","placeholder":"Jane"}],"button_text":"Subscribe","display_options":{"theme":"dark"},"version":1,"is_active":"active","allowed_origins":[],"created_at":"2026-08-23T04:58:13.628286Z","updated_at":"2026-08-23T04:58:13.628286Z"}]

![04-authenticated-widgets-success](docs/screenshots/04-authenticated-widgets-success.png)

### ☑ Multi-tenant isolation proven

**Tenant B cannot access Tenant A's widget:**

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -X POST http://127.0.0.1:8000/api/auth/login `
>>   -H "Content-Type: application/json" `
>>   -d "{\`"email\`":\`"other@example.com\`", \`"password\`":\`"other1234\`"}"
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3NjdmNmY0ZS1iMjliLTQzYjEtYTFiZC1lMjU2MDI3Y2VlMmEiLCJleHAiOjE3ODc0NjUxNDZ9.mAVw5h-ZGszSWxgOHSWsQTXBOyuWKwaKuzM-IBC51Pg","token_type":"bearer"}

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> $TOKEN2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3NjdmNmY0ZS1iMjliLTQzYjEtYTFiZC1lMjU2MDI3Y2VlMmEiLCJleHAiOjE3ODc0NjUxNDZ9.mAVw5h-ZGszSWxgOHSWsQTXBOyuWKwaKuzM-IBC51Pg"

(venv) PS 
D:\flyrankai\capstone\flyrank-capstone-widget-platform> $WIDGET_ID = "c18b6dfd-e46b-46e5-a33e-3ae2a3993de8"

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i http://127.0.0.1:8000/api/widgets/$WIDGET_ID `
>>   -H "Authorization: Bearer $TOKEN2"
HTTP/1.1 404 Not Found
date: Sun, 23 Aug 2026 05:07:07 GMT
server: uvicorn
content-length: 29
content-type: application/json

{"detail":"Widget not found"}


**Automated proof:**

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_widgets.py::test_tenant_isolation -v
=========================== test session starts ===========================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_widgets.py::test_tenant_isolation PASSED                  [100%]
============================ 1 passed in 1.13s ============================


(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_dashboard.py::test_dashboard_tenant_isolation -v
=========================== test session starts ===========================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_dashboard.py::test_dashboard_tenant_isolation PASSED      [100%]
============================ 1 passed in 1.50s ============================

![05-multi-tenant-isolation-proof](docs/screenshots/05-multi-tenant-isolation-proof.png)

## WIDGET DELIVERY

### ☑ Embed snippet generated per widget

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe http://127.0.0.1:8000/api/widgets/$WIDGET_ID/snippet `
>>   -H "Authorization: Bearer $TOKEN"
{"widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","snippet":"<script src=\"http://127.0.0.1:8000/widget.js?id=c18b6dfd-e46b-46e5-a33e-3ae2a3993de8\"></script>"}

![06-widget-snippet-and-config](docs/screenshots/06-widget-snippet-and-config.png)

### ☑ Public config endpoint with cache headers

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i http://127.0.0.1:8000/api/widgets/$WIDGET_ID/config
HTTP/1.1 200 OK
date: Sun, 23 Aug 2026 05:16:34 GMT
server: uvicorn
cache-control: public, max-age=60, stale-while-revalidate=30
x-widget-version: 1
content-length: 578
content-type: application/json

{"id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","widget_type":"contact_form","title":"Get in Touch","description":"We'd love to hear from you. Fill out the form below.","fields_config":[{"name":"name","label":"Full Name","required":true,"field_type":"text","placeholder":"John Doe"},{"name":"email","label":"Email Address","required":true,"field_type":"email","placeholder":"john@example.com"},{"name":"message","label":"Message","required":true,"field_type":"textarea","placeholder":"Your message..."}],"button_text":"Send Message","display_options":{"theme":"light"},"version":1}

![06-widget-snippet-and-config](docs/screenshots/06-widget-snippet-and-config-1.png)

### ☑ Versioned bundle served

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i http://127.0.0.1:8000/widget.js
HTTP/1.1 200 OK
date: Sun, 23 Aug 2026 05:24:47 GMT
server: uvicorn
cache-control: public, max-age=31536000, immutable
x-widget-version: 1
content-type: application/javascript
content-length: 6847
last-modified: Sat, 22 Aug 2026 15:59:51 GMT
etag: "2829db0c35cb221bad83b0cfdff612bd"

![07-widget-js-serving](docs/screenshots/07-widget-js-serving.png)

### ☑ Widget renders on different-origin page

Customer site origin: `http://localhost:5500`
API origin: `http://localhost:8000`

![08-widget-cross-origin](docs/screenshots/08-widget-cross-origin.png)

![09-network-tab-cross-origin-requests](docs/screenshots/09-network-tab-cross-origin-requests.png)

## Public Submission API

### ☑ CORS headers correct, preflight handled

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i -X OPTIONS http://127.0.0.1:8000/api/submissions `
>>   -H "Origin: http://localhost:5500" `
>>   -H "Access-Control-Request-Method: POST" `
>>   -H "Access-Control-Request-Headers: Content-Type"
HTTP/1.1 200 OK
date: Sun, 23 Aug 2026 05:29:10 GMT
server: uvicorn
access-control-allow-origin: *
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
access-control-max-age: 600
access-control-allow-headers: Content-Type
content-length: 2
content-type: text/plain; charset=utf-8

OK

![10-cors-preflight-curl-response](docs/screenshots/10-cors-preflight-curl-response.png)

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_submissions.py::test_cors_preflight -v
======================== test session starts ========================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_submissions.py::test_cors_preflight PASSED          [100%]
========================= 1 passed in 0.65s 

![11-cors-preflight-pytest-passed](docs/screenshots/11-cors-preflight-pytest-passed.png)

### ☑ Input validated; malformed/oversized rejected with 4xx

**Malformed JSON:**

**Automated tests:**

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> # Malformed JSON
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i -X POST http://127.0.0.1:8000/api/submissions `
>>   -H "Content-Type: application/json" `
>>   -d "not valid json{{{"
HTTP/1.1 400 Bad Request
date: Sun, 23 Aug 2026 05:30:37 GMT
server: uvicorn
content-length: 25
content-type: application/json
{"detail":"Invalid JSON"}

![12-malformed-json-rejection](docs/screenshots/12-malformed-json-rejection.png)

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> # Missing required field
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i -X POST http://127.0.0.1:8000/api/submissions `
>>   -H "Content-Type: application/json" `
>>   -d "{\"widget_id\":\"$WIDGET_ID\",\"data\":{\"message\":\"no name or email\"}}"
HTTP/1.1 400 Bad Request
date: Sun, 23 Aug 2026 05:30:45 GMT
server: uvicorn
content-length: 25
content-type: application/json

![13-missing-required-field-rejection](docs/screenshots/13-missing-required-field-rejection.png)

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_submissions.py::test_invalid_json_payload tests/test_submissions.py::test_missing_required_field tests/test_submissions.py::test_oversized_payload -v
======================== test session starts ========================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 3 items
tests/test_submissions.py::test_invalid_json_payload PASSED    [ 33%]
tests/test_submissions.py::test_missing_required_field PASSED  [ 66%]
tests/test_submissions.py::test_oversized_payload PASSED       [100%]
========================= 3 passed in 1.21s =========================

![14-input-validation-pytest-suite-passed](docs/screenshots/14-input-validation-pytest-suite-passed.png)

### ☑ Valid submissions stored, linked to correct widget/tenant

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> $body = @{
>>     widget_id = "$WIDGET_ID"
>>     data = @{
>>         name = "Evidence Test"
>>         email = "evidence@test.com"
>>         message = "Proof of storage"
>>     }
>> } | ConvertTo-Json -Depth 3
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform>
(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/submissions" `
>>     -Method Post `
>>     -ContentType "application/json" `
>>     -Body $body


id           : 83fd69ab-8986-4824-8f45-8fda35b5c05b
widget_id    : c18b6dfd-e46b-46e5-a33e-3ae2a3993de8
data         : @{name=Evidence Test; email=evidence@test.com;
               message=Proof of storage}
country      :
city         :
region       :
geo_provider :
created_at   : 2026-08-23T05:34:07.629329Z



(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe http://127.0.0.1:8000/api/dashboard/submissions `
>>   -H "Authorization: Bearer $TOKEN"
{"submissions":[{"id":"83fd69ab-8986-4824-8f45-8fda35b5c05b","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Evidence Test","email":"evidence@test.com","message":"Proof of storage"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:34:07.629329Z"},{"id":"e6ad1f63-4159-4501-812e-f39400c73d63","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Jiya Yadav","email":"yjiya1012@gmail.com","message":"i am good\n"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:26:58.905401Z"},{"id":"f59e773f-1060-4591-8c5a-fb7ff4c5ea2d","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Jiya Yadav","email":"yjiya1012@gmail.com","message":"i am ok\n"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:26:49.880404Z"},{"id":"7eb3c31f-2815-4d73-b1ce-2928d66e3852","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber6@example.com","first_name":"Subscriber 6"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-23T01:58:13.631293Z"},{"id":"9c19a38b-59c7-4a5a-9a07-01f846873547","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber1@example.com","first_name":"Subscriber 1"},"country":"Canada","city":"Toronto","region":null,"geo_provider":"seed-data","created_at":"2026-08-22T15:58:13.631293Z"},{"id":"f0f8dd01-4871-488f-b8c2-88f9fa538581","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 23","email":"user23@example.com","message":"This is test message number 23."},"country":"Australia","city":"Sydney","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-22T14:58:13.631293Z"},{"id":"d2eb8c19-7909-4f71-ab3b-beb999f71d8c","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber8@example.com","first_name":"Subscriber 8"},"country":"Brazil","city":"São Paulo","region":null,"geo_provider":"seed-data","created_at":"2026-08-22T12:58:13.631293Z"},{"id":"f5de70ce-7838-4d7a-91b7-5635f9178b8e","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 7","email":"user7@example.com","message":"This is test message number 7."},"country":"United Kingdom","city":"London","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-20T19:58:13.631293Z"},{"id":"97de60ee-1195-4f42-a571-77187a41260d","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber7@example.com","first_name":"Subscriber 7"},"country":"Japan","city":"Tokyo","region":null,"geo_provider":"seed-data","created_at":"2026-08-18T21:58:13.631293Z"},{"id":"82526e11-8440-4439-a713-0682d671edf6","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber3@example.com","first_name":"Subscriber 3"},"country":"Brazil","city":"São Paulo","region":null,"geo_provider":"seed-data","created_at":"2026-08-18T12:58:13.631293Z"},{"id":"d131ad73-4ea0-4cbd-aae8-744f74f1c1ca","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber5@example.com","first_name":"Subscriber 5"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-17T18:58:13.631293Z"},{"id":"0008cef5-3258-4b6b-9723-06ea74c9d4e5","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 16","email":"user16@example.com","message":"This is test message number 16."},"country":"Germany","city":"Berlin","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-15T06:58:13.631293Z"},{"id":"3eaa2a14-a7a3-49f2-a1d1-8c98aa1855a0","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 18","email":"user18@example.com","message":"This is test message number 18."},"country":"United States","city":"New York","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-13T18:58:13.631293Z"},{"id":"6840d986-467e-454d-9af1-de55e5491662","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber2@example.com","first_name":"Subscriber 2"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-13T11:58:13.631293Z"},{"id":"a59dcdd2-2085-4ab1-a1f0-3089ccfcb362","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber9@example.com","first_name":"Subscriber 9"},"country":"United States","city":"New York","region":null,"geo_provider":"seed-data","created_at":"2026-08-13T00:58:13.631293Z"},{"id":"8631e420-a26d-4809-b357-3ff9d5919d64","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber10@example.com","first_name":"Subscriber 10"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-10T01:58:13.631293Z"},{"id":"15dd6bf9-febd-4594-ab84-f4c6dedeb771","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber4@example.com","first_name":"Subscriber 4"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-09T23:58:13.631293Z"},{"id":"1cf67669-a431-4776-be42-18af7b05d7b9","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 25","email":"user25@example.com","message":"This is test message number 25."},"country":"Canada","city":"Toronto","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-09T21:58:13.631293Z"},{"id":"9c2b79d4-2f36-4732-a977-8313c560a938","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 14","email":"user14@example.com","message":"This is test message number 14."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-09T07:58:13.631293Z"},{"id":"89ea76cf-9458-44ca-94bb-f4de08a632eb","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 1","email":"user1@example.com","message":"This is test message number 1."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-08T15:58:13.631293Z"},{"id":"f3e635e0-ae55-40e1-bf59-97c5ed038278","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 12","email":"user12@example.com","message":"This is test message number 12."},"country":"Australia","city":"Sydney","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-05T15:58:13.631293Z"},{"id":"63aff54f-08b2-4e13-99f7-3ab753ed101b","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 22","email":"user22@example.com","message":"This is test message number 22."},"country":"Germany","city":"Berlin","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-04T10:58:13.631293Z"},{"id":"d0a8ded7-3824-4015-b9a8-5d478fec3e38","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 10","email":"user10@example.com","message":"This is test message number 10."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-03T21:58:13.631293Z"},{"id":"a07b1efb-c7b2-48f6-848d-c1e87b5a662b","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 2","email":"user2@example.com","message":"This is test message number 2."},"country":"United Kingdom","city":"London","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-03T12:58:13.631293Z"},{"id":"cddc6c58-91b4-4b72-9ca5-4a16d15ac466","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 9","email":"user9@example.com","message":"This is test message number 9."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-02T23:58:13.631293Z"},{"id":"a3c49de4-8334-4bd8-90f3-9e24b02202a4","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 20","email":"user20@example.com","message":"This is test message number 20."},"country":"Brazil","city":"São Paulo","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-02T19:58:13.631293Z"},{"id":"553bcd67-7ff4-4eab-a266-0cdf7892e39d","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 11","email":"user11@example.com","message":"This is test message number 11."},"country":"Japan","city":"Tokyo","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-02T10:58:13.631293Z"},{"id":"62a5933a-daa5-49ee-b5b9-222fd0843cba","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 13","email":"user13@example.com","message":"This is test message number 13."},"country":"Japan","city":"Tokyo","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-01T17:58:13.631293Z"},{"id":"82b2e1ee-e732-44bb-91e3-1edcc2bfff45","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 21","email":"user21@example.com","message":"This is test message number 21."},"country":"Germany","city":"Berlin","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-30T19:58:13.631293Z"},{"id":"551e48e7-7444-44be-9141-9a8b3bc846db","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 3","email":"user3@example.com","message":"This is test message number 3."},"country":"Canada","city":"Toronto","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-29T16:58:13.631293Z"},{"id":"f6766242-004d-4495-bc24-c8d00c1f0375","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 4","email":"user4@example.com","message":"This is test message number 4."},"country":"United Kingdom","city":"London","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-29T06:58:13.631293Z"},{"id":"e706e604-29fa-485d-b744-037972c5b46c","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 15","email":"user15@example.com","message":"This is test message number 15."},"country":"United Kingdom","city":"London","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-28T23:58:13.631293Z"},{"id":"2a964cc2-23c0-4827-b3b5-667a1215bf52","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 19","email":"user19@example.com","message":"This is test message number 19."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-28T19:58:13.631293Z"},{"id":"0b88f2f8-992f-41a5-9549-58bc1109d033","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 5","email":"user5@example.com","message":"This is test message number 5."},"country":"United States","city":"New York","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-28T13:58:13.631293Z"},{"id":"928e04c0-2620-45cb-8041-6e22aca26e3e","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 8","email":"user8@example.com","message":"This is test message number 8."},"country":"Australia","city":"Sydney","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-28T09:58:13.631293Z"},{"id":"dbc68a13-8650-49a4-ac0a-5322b17c32cb","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 24","email":"user24@example.com","message":"This is test message number 24."},"country":"France","city":"Paris","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-26T07:58:13.631293Z"},{"id":"a5db5f4d-85c1-457f-ab6a-b94098a51f35","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 17","email":"user17@example.com","message":"This is test message number 17."},"country":"Canada","city":"Toronto","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-26T03:58:13.631293Z"},{"id":"bbd09d67-cd19-41c5-8a5d-ec4f54c02224","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 6","email":"user6@example.com","message":"This is test message number 6."},"country":"Canada","city":"Toronto","region":"Test Region","geo_provider":"seed-data","created_at":"2026-07-25T13:58:13.631293Z"}],"total":38,"page":1,"page_size":50}

![15-valid-submission-and-dashboard-verification](docs/screenshots/15-valid-submission-and-dashboard-verification.png)

## Abuse Protection

### ☑ Rate limiting returns 429 under burst

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> for ($i=1; $i -le 20; $i++) {
>>   curl.exe -s -o NUL -w "Request $i : %{http_code}`n" -X POST http://127.0.0.1:8000/api/submissions `
>>     -H "Content-Type: application/json" `
>>     -d "{\"widget_id\":\"$WIDGET_ID\",\"data\":{\"name\":\"Burst $i\",\"email\":\"burst$i@test.com\"}}"
>> }
Request 1 : 400
Request 2 : 400
Request 3 : 400
Request 4 : 400
Request 5 : 400
Request 6 : 400
Request 7 : 400
Request 8 : 400
Request 9 : 400
Request 10 : 400
Request 11 : 429
Request 12 : 429
Request 13 : 429
Request 14 : 429
Request 15 : 429
Request 16 : 429
Request 17 : 429
Request 18 : 429
Request 19 : 429
Request 20 : 429

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_rate_limiting.py -v
========================= test session starts =========================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_rate_limiting.py::test_rate_limiting_burst PASSED     [100%]
========================== 1 passed in 0.96s ==========================

![16-rate-limiting-burst-proof](docs/screenshots/16-rate-limiting-burst-proof.png)

### ☑ Spam prevention blocks spam submission

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe -i -X POST http://127.0.0.1:8000/api/submissions `
>>   -H "Content-Type: application/json" `
>>   -d "{\"widget_id\":\"$WIDGET_ID\",\"data\":{\"name\":\"Bot\",\"email\":\"bot@spam.com\"},\"_hp_field\":\"I am a bot\"}"
HTTP/1.1 400 Bad Request
date: Sun, 23 Aug 2026 05:36:52 GMT
server: uvicorn
content-length: 25
content-type: application/json

{"detail":"Invalid JSON"}curl: (3) unmatched brace in position 110:
widget_id\:\c18b6dfd-e46b-46e5-a33e-3ae2a3993de8\,\data\:{\name\:\Bot\,\email\:\bot@spam.com\},\_hp_field\:\I
                                                    
                                                                                                        ^


(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_submissions.py::test_honeypot_spam_rejection -v
============================== test session starts ===============================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_submissions.py::test_honeypot_spam_rejection PASSED              [100%]
=============================== 1 passed in 0.66s ================================

![17-spam-prevention-honeypot-proof](docs/screenshots/17-spam-prevention-honeypot-proof.png)

## Enrichment & Safe Side Effects

### ☑ Geo enrichment with provider fallback chain

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_geo_fallback.py -v
============================== test session starts ===============================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 3 items

tests/test_geo_fallback.py::test_provider_a_succeeds PASSED                 [ 33%]
tests/test_geo_fallback.py::test_provider_a_fails_provider_b_succeeds PASSED [ 66%]
tests/test_geo_fallback.py::test_both_providers_down PASSED                 [100%]

=============================== 3 passed in 0.13s ================================

![18-geo-fallback-chain-pytest-passed](docs/screenshots/18-geo-fallback-chain-pytest-passed.png)

Optional bonus (real API, manual only): submit a real form on the test site and check the dashboard shows a real country/city:

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> curl.exe http://127.0.0.1:8000/api/dashboard/stats -H "Authorization: Bearer $TOKEN"
{"total_submissions":38,"submissions_today":4,"submissions_this_week":11,"submissions_this_month":28,"by_widget":[{"widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","widget_name":"Newsletter Signup","count":10},{"widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","widget_name":"Contact Form","count":28}],"by_country":[{"country":"Australia","count":8},{"country":"France","count":6},{"country":"Canada","count":5},{"country":"United Kingdom","count":4},{"country":"Japan","count":3},{"country":"Germany","count":3},{"country":"United States","count":3},{"country":"Brazil","count":3}],"recent":[{"id":"83fd69ab-8986-4824-8f45-8fda35b5c05b","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Evidence Test","email":"evidence@test.com","message":"Proof of storage"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:34:07.629329Z"},{"id":"e6ad1f63-4159-4501-812e-f39400c73d63","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Jiya Yadav","email":"yjiya1012@gmail.com","message":"i am good\n"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:26:58.905401Z"},{"id":"f59e773f-1060-4591-8c5a-fb7ff4c5ea2d","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Jiya Yadav","email":"yjiya1012@gmail.com","message":"i am ok\n"},"country":null,"city":null,"region":null,"geo_provider":null,"created_at":"2026-08-23T05:26:49.880404Z"},{"id":"7eb3c31f-2815-4d73-b1ce-2928d66e3852","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber6@example.com","first_name":"Subscriber 6"},"country":"Australia","city":"Sydney","region":null,"geo_provider":"seed-data","created_at":"2026-08-23T01:58:13.631293Z"},{"id":"9c19a38b-59c7-4a5a-9a07-01f846873547","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber1@example.com","first_name":"Subscriber 1"},"country":"Canada","city":"Toronto","region":null,"geo_provider":"seed-data","created_at":"2026-08-22T15:58:13.631293Z"},{"id":"f0f8dd01-4871-488f-b8c2-88f9fa538581","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 23","email":"user23@example.com","message":"This is test message number 23."},"country":"Australia","city":"Sydney","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-22T14:58:13.631293Z"},{"id":"d2eb8c19-7909-4f71-ab3b-beb999f71d8c","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber8@example.com","first_name":"Subscriber 8"},"country":"Brazil","city":"São Paulo","region":null,"geo_provider":"seed-data","created_at":"2026-08-22T12:58:13.631293Z"},{"id":"f5de70ce-7838-4d7a-91b7-5635f9178b8e","widget_id":"c18b6dfd-e46b-46e5-a33e-3ae2a3993de8","data":{"name":"Test User 7","email":"user7@example.com","message":"This is test message number 7."},"country":"United Kingdom","city":"London","region":"Test Region","geo_provider":"seed-data","created_at":"2026-08-20T19:58:13.631293Z"},{"id":"97de60ee-1195-4f42-a571-77187a41260d","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber7@example.com","first_name":"Subscriber 7"},"country":"Japan","city":"Tokyo","region":null,"geo_provider":"seed-data","created_at":"2026-08-18T21:58:13.631293Z"},{"id":"82526e11-8440-4439-a713-0682d671edf6","widget_id":"1d751f41-4296-497a-9a24-2d80c0990a45","data":{"email":"subscriber3@example.com","first_name":"Subscriber 3"},"country":"Brazil","city":"São Paulo","region":null,"geo_provider":"seed-data","created_at":"2026-08-18T12:58:13.631293Z"}]}

![dashboard-stats-and-side-effects-test](docs/screenshots/dashboard-stats-and-side-effects-test.png)

### ☑ Failing email/webhook does not prevent submission storage

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_geo_fallback.py -v
============================== test session starts ===============================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 3 items
tests/test_geo_fallback.py::test_provider_a_succeeds PASSED                 [ 33%]
tests/test_geo_fallback.py::test_provider_a_fails_provider_b_succeeds PASSED [ 66%]
tests/test_geo_fallback.py::test_both_providers_down PASSED                 [100%]
=============================== 3 passed in 0.23s ================================

![18-geo-fallback-chain-pytest-passed](docs/screenshots/18-geo-fallback-chain-pytest-passed.png)

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> pytest tests/test_side_effects.py -v
============================== test session starts ===============================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collected 1 item
tests/test_side_effects.py::test_email_failure_does_not_block_submission PASSED [100%]
=============================== 1 passed in 0.63s ================================

![19-side-effects-email-failure-pytest-passed](docs/screenshots/19-side-effects-email-failure-pytest-passed.png)

## Tests & Documentation

### ☑ Automated tests cover required scenarios

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> cat pytest_full_output.txt
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.3.3, pluggy-1.6.0 -- D:\flyrankai\capstone\flyrank-capstone-widget-platform\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\flyrankai\capstone\flyrank-capstone-widget-platform
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2, asyncio-0.24.0, httpx-0.30.0
asyncio: mode=Mode.STRICT, default_loop_scope=function
collecting ... collected 31 items

tests/test_auth.py::test_register_success PASSED                         [  3%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [  6%]
tests/test_auth.py::test_register_short_password PASSED                  [  9%]
tests/test_auth.py::test_login_success PASSED                            [ 12%]
tests/test_auth.py::test_login_wrong_password PASSED                     [ 16%]
tests/test_auth.py::test_protected_endpoint_without_token PASSED         [ 19%]
tests/test_dashboard.py::test_dashboard_submissions PASSED               [ 22%]
tests/test_dashboard.py::test_dashboard_stats PASSED                     [ 25%]
tests/test_dashboard.py::test_dashboard_tenant_isolation PASSED          [ 29%]
tests/test_geo_fallback.py::test_provider_a_succeeds PASSED              [ 32%]
tests/test_geo_fallback.py::test_provider_a_fails_provider_b_succeeds PASSED [ 35%]
tests/test_geo_fallback.py::test_both_providers_down PASSED              [ 38%]
tests/test_rate_limiting.py::test_rate_limiting_burst PASSED             [ 41%]
tests/test_side_effects.py::test_email_failure_does_not_block_submission PASSED [ 45%]
tests/test_submissions.py::test_valid_submission PASSED                  [ 48%]
tests/test_submissions.py::test_cors_preflight PASSED                    [ 51%]
tests/test_submissions.py::test_invalid_json_payload PASSED              [ 54%]
tests/test_submissions.py::test_missing_required_field PASSED            [ 58%]
tests/test_submissions.py::test_oversized_payload PASSED                 [ 61%]
tests/test_submissions.py::test_honeypot_spam_rejection PASSED           [ 64%]
tests/test_submissions.py::test_nonexistent_widget_submission PASSED     [ 67%]
tests/test_submissions.py::test_submission_with_idempotency PASSED       [ 70%]
tests/test_widgets.py::test_create_widget PASSED                         [ 74%]
tests/test_widgets.py::test_create_widget_invalid_type PASSED            [ 77%]
tests/test_widgets.py::test_list_widgets PASSED                          [ 80%]
tests/test_widgets.py::test_get_widget PASSED                            [ 83%]
tests/test_widgets.py::test_update_widget PASSED                         [ 87%]
tests/test_widgets.py::test_delete_widget PASSED                         [ 90%]
tests/test_widgets.py::test_tenant_isolation PASSED                      [ 93%]
tests/test_widgets.py::test_get_snippet PASSED                           [ 96%]
tests/test_widgets.py::test_public_config_endpoint PASSED                [100%]
============================= 31 passed in 14.46s =============================

![20-pytest-full-output-all-passed](docs/screenshots/20-pytest-full-output-all-passed.png)

### ☑ README + submission-pack files present

(venv) PS D:\flyrankai\capstone\flyrank-capstone-widget-platform> dir


    Directory: D:\flyrankai\capstone\flyrank-capstone-widget-platform


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         8/22/2026  10:37 PM                .pytest_cache
d-----         8/22/2026   8:56 PM                alembic
d-----         8/22/2026   9:26 PM                app
d-----         8/23/2026  12:28 AM                docs
d-----         8/22/2026   9:44 PM                static
d-----         8/22/2026  10:36 PM                tests
d-----         8/22/2026   9:52 PM                test_site
d-----         8/22/2026  10:22 PM                venv
-a----         8/22/2026   8:33 PM            398 .env
-a----         8/22/2026   8:33 PM            398 .env.example
-a----         8/22/2026   8:32 PM            137 .gitignore
-a----         8/22/2026   8:51 PM            653 alembic.ini
-a----         8/22/2026   8:46 PM            417 BUILDLOG.md
-a----         8/22/2026   8:46 PM            635 capstone.yaml
-a----         8/22/2026   9:15 PM           1915 design-doc.md
-a----         8/22/2026   8:46 PM            470 docker-compose.yml
-a----         8/23/2026  11:32 AM          35016 EVIDENCE.md
-a----         8/23/2026  11:02 AM         136712 image.png
-a----         8/22/2026   8:31 PM           1088 LICENSE
-a----         8/22/2026  11:06 PM            164 pytest.ini
-a----         8/23/2026  11:27 AM           6216 pytest_full_output.txt
-a----         8/22/2026   8:31 PM             33 README.md
-a----         8/23/2026  10:42 AM            363 requirements.txt
-a----         8/22/2026   9:54 PM           7022 seed.py
-a----         8/23/2026  11:27 AM          49152 test.db 

![21-repo-files-directory-listing](docs/screenshots/21-repo-files-directory-listing.png)