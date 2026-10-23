# Smart Library deployment guide

This copy has local deployment fixes. It has not been pushed or deployed.
The existing design and Unity assets are preserved.

## Accounts and secrets

Use your own Firebase project, Vercel account, and Render account. Do not share
passwords or service-account private keys in chat or commit them to Git.
First check https://console.firebase.google.com/ for an existing project.
If none exists, create one, register a Web app, and enable Authentication >
Email/Password. Microsoft university SSO additionally requires configuration
of the Microsoft provider and access to that university's identity setup.
The login currently targets the original university Microsoft tenant.

## 1. Database and API on Render

Create a fresh PostgreSQL database and a Python web service in the same region.
Use the repository branch containing these reviewed fixes when publishing is approved.
Set the service root directory to `backend` and Python to 3.11.9.
Build command: `pip install -r requirements.txt`
Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
Health check path: `/`

Set these backend environment values securely in Render:
- DATABASE_URL: database internal URL, using the `postgresql+psycopg2://` scheme.
- FIREBASE_JSON: full service-account JSON from your own Firebase project.
- CORS_ORIGINS: exact frontend HTTPS origin, without a trailing slash. Multiple
  allowed origins can be separated by commas.
- ENABLE_DEMO_ENDPOINTS: `false` (keep destructive demo operations disabled).

No SECRET_KEY is needed: authentication uses Firebase tokens.
FIREBASE_CREDENTIALS is an alternative local credential-file path.
The API initializes tables at startup; startup fails if credentials or DB access
are missing. Do not run seed scripts against existing data.

Existing databases need a backup and reviewed migration for search_logs.user_id:
it now uses UUID to match user.id. create_all does not change existing columns.
No existing database has been accessed or migrated by these fixes.

## 2. Frontend on Vercel

Import the repository only after publishing is approved. Root: `frontend`.
Framework: Next.js. Node: 24.x. Install: `npm ci`. Build: `npm run build`.
Leave the output directory at the Next.js preset default (not `dist`).

Copy the variable names from frontend/.env.example into Vercel settings.
NEXT_PUBLIC_API_BASE_URL must be the backend HTTPS URL, without `/api/v1`.
Get the six NEXT_PUBLIC_FIREBASE_* values from Firebase Project settings > Your
apps > Web app > SDK setup and configuration. These are web configuration;
never put the service-account JSON in a NEXT_PUBLIC variable.
Set these values before building; changing them requires rebuilding.

Add the Vercel domain in Firebase Authentication > Settings > Authorized domains.
Set the same frontend origin in the backend CORS_ORIGINS value.

## 3. Create your login and library roles

Create an Email/Password user in Firebase Authentication > Users.
From a trusted backend environment with credentials configured, run:
`python manage_user.py --email YOUR_EMAIL --role admin`
Use `--role student` or `--role staff` for other accounts.
This links an existing Firebase user to the library database; it never creates
shared passwords. Admin routes require admin; circulation and restocking allow
staff or admin. Demo/reset routes additionally require ENABLE_DEMO_ENDPOINTS=true.
Catalog reading remains public; dashboard and search logging require login.
UI pages are not a security boundary: backend authorization protects the data.

## 4. Verify before sharing

Frontend locally, with real values configured in frontend/.env.local:
```
cd frontend
npm ci
npm run build
npm start
```

Check home/login, actual login, catalog, student dashboard, admin role rejection,
issuing/returning test books, and the Unity locator. Test with a separate test
database first. Unity downloads about 49 MB; test on mobile and slower networks.
The existing 50-metre campus geofence remains unchanged and is a browser-side
feature, not a server authorization boundary.

API checks: `/` should return active; unauthorized admin/mutation requests must
be denied. Confirm browser Network and Console show no failed API calls.
No real end-to-end login can be validated without your Firebase project.

## Local changes

- Added role checks and disabled demo/reset operations by default.
- Centralized fresh Firebase token attachment in the frontend API helper.
- Configurable CORS and credential setup, with ignored local secrets.
- Fixed search-log foreign-key type and an undefined seed response variable.
- Removed password console logging and unnecessary SQL query logging.
- Updated dependencies within existing ranges plus targeted security overrides.
- Excluded large Unity assets from precache and disabled API response caching.

Build-only tests may use fake Firebase web configuration. That proves compilation
only, not working authentication, database connectivity, or public deployment.

## Test results

Backend: 9 isolated tests passed using an in-memory SQLite database and mocked
Firebase token verification. Python dependencies passed pip check. Real Firebase
sign-in and PostgreSQL startup still require project credentials and a database.
Frontend dependency audit reported zero known advisories after targeted updates.

Windows sandbox builds encountered intermittent EPERM directory-creation errors.
The frontend compiled and passed TypeScript with clearly fake Firebase web
configuration; this is not an end-to-end authentication test.

The complete production build then passed in a clean verification copy using
precreated output directories and one build worker (Windows workaround only).
All 17 static pages generated and both dynamic routes built successfully.
The build used fake, nonfunctional Firebase configuration only. The shipping
configuration keeps Next.js default worker/output settings.

HTTP smoke checks passed against the built server: home, login, catalog, Unity
loader, Unity data and Unity WebAssembly returned HTTP 200. The .wasm asset
was served as application/wasm. Browser visual QA, real login and a real
PostgreSQL connection remain pending account configuration.
