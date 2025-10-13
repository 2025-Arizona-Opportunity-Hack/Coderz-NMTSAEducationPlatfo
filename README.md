# NMTSA Learning Management System (LMS)

A Django-based LMS for neurologic music therapy education built for NMTSA, serving two audiences:
- Healthcare professionals pursuing continuing education (CE) and NMT certification
- Clients/families needing free resources and premium courses to support therapy journeys

This LMS consolidates scattered resources (previously on Google Drive) into a secure, trackable platform with dual authentication, autism-friendly UI, course management, video streaming, payments, certificates, discussions, and an AI assistant.


## Features at a Glance

- Dual authentication and RBAC
	- OAuth (Auth0) for Students/Teachers
	- Django Admin auth for Admins (admins do NOT use OAuth)
- Teacher onboarding + verification workflow (admin approval required)
- Course management (courses → modules → lessons)
	- Lesson types: VideoLesson (file + transcript) and BlogLesson (content + images)
	- Publish/review process with auto-unpublish on edits
- Student enrollment and progress tracking
	- Completed lessons, video resume (last position), completion thresholds
- Payments (PayPal)
	- Paid/free courses, capture + idempotent processing
- Certificates for CE credits (PDF generation with metadata)
- Discussions per course/module
- AI chat assistant with memory + semantic course search (Supermemory)
- Accessibility and autism-friendly UI
	- 4 themes (Light/Dark/High Contrast/Minimal), font size controls, zero animations/auto-play
- Localization (EN/ES), SEO + sitemaps
- Analytics (engagement, completions), export CSV


## Repository Structure (high level)

- `nmtsa_lms/` — Django project root
	- `manage.py` — Django CLI entry
	- `nmtsa_lms/` — core settings, URLs, OAuth views, Tailwind pipeline
	- `authentication/` — custom user, profiles, OAuth session middleware, onboarding
	- `teacher_dash/` — course and lesson modeling, review workflow
	- `student_dash/` — enrollment, progress
	- `admin_dash/` — admin verification + course review
	- `lms/` — shared models, AI chat/search APIs, sitemaps, course memory
	- `static/` and `templates/` — Tailwind CSS, base templates and components
- `docs/` — project documentation, integration guides, SRS

See also: `docs/SRS_NMTSA_LMS_FULL.md` for the complete SRS.


## Tech Stack

- Backend: Python 3.10+, Django 4.x+
- Frontend: Django templates + Tailwind CSS
- Auth: Auth0 (OAuth/OIDC) for users, Django admin for admins
- Payments: PayPal Checkout/Payments
- AI: Supermemory (chat and semantic search)
- Database: SQLite (dev), PostgreSQL (prod recommended)
- Video: HTML5 video, optional MoviePy utilities


## Prerequisites

- Python 3.10+
- Node.js 18+ and npm (for Tailwind)
- An Auth0 tenant (Domain, Client ID, Client Secret)
- PayPal credentials (Sandbox first: Client ID/Secret)
- Supermemory API key and base URL

On Windows using bash.exe (Git Bash/WSL-friendly commands below).


## Quick Start (Development)

1) Clone and create a virtual environment

```bash
git clone https://github.com/2025-Arizona-Opportunity-Hack/Coderz-NMTSAEducationPlatfo.git nmtsaeducationlms
cd nmtsaeducationlms
python -m venv .venv
source .venv/Scripts/activate
```

2) Install Python dependencies

```bash
pip install -r requirements.txt
```

3) Install Tailwind dependencies

```bash
cd nmtsa_lms
npm install
cd ..
```

4) Create a `.env` file at the repo root

```bash
cat > .env << 'EOF'
# Django
SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Auth0 (OAuth for Students/Teachers only)
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret

# PayPal
PAYPAL_CLIENT_ID=your-paypal-sandbox-client-id
PAYPAL_CLIENT_SECRET=your-paypal-sandbox-client-secret
PAYPAL_MODE=sandbox

# Supermemory
SUPERMEMORY_API_KEY=your-supermemory-key
SUPERMEMORY_BASE_URL=https://api.supermemory.ai
SUPERMEMORY_PROJECT_ID=nmtsa-lms

# Google Gemini (free tier)
GEMINI_API_KEY=your-gemini-api-key

# Database (dev)
# SQLite is default; for Postgres (prod), prefer: DATABASE_URL=postgres://user:pass@host:5432/dbname
# DATABASE_URL=postgres://...
EOF
```

5) Apply migrations and create an admin user

```bash
cd nmtsa_lms
python manage.py migrate
python manage.py createsuperuser
# After login to Django admin, set role='admin' and onboarding_complete=True for your admin user
```

6) (Optional) Seed demo data

```bash
python manage.py seed_demo_courses
```

7) Start the dev servers in two terminals

- Terminal A (Django):
```bash
cd nmtsa_lms
python manage.py runserver
```

- Terminal B (Tailwind CSS watcher):
```bash
cd nmtsa_lms
npm run dev
```

Visit http://127.0.0.1:8000


## Auth: Login Flows

- Students/Teachers: Use OAuth via Auth0.
	- Flow: `/login` → Auth0 → `/callback` → Select Role (if first time) → Onboarding → Dashboard
	- Session key: `request.session['user']` with `userinfo`, `role`, `onboarding_complete`
- Admins: Use Django credentials at `/auth/admin-login/`.
	- Admins do NOT use OAuth; enforced by role selection and decorators.

RBAC decorators (enforced at view level):
- `login_required`, `student_required`, `teacher_required`, `admin_required`, `teacher_verified_required`, `onboarding_complete_required`


## Core Workflows

- Teacher onboarding + verification
	- Teacher uploads resume/certifications → status `pending` → Admin approves/rejects
	- Only approved teachers can create/edit courses
- Course review and publish
	- Create course → add modules/lessons → submit for review
	- Admin approves → Teacher can publish
	- Editing a published course auto-unpublishes and re-submits for review
- Student progress and CE certificate
	- Enrollment tracks progress; video resume stored; completion triggers certificate generation (PDF)
- Payments (PayPal)
	- Paid courses require checkout; sandbox and live supported; webhook/idempotent processing recommended
- Discussions
	- Course/module discussions with moderation controls (teachers/admins)
- AI chat + semantic search
	- Available to all users (including guests); integrates with Supermemory; course data can be synced to memory


## Tailwind CSS

- Dev watch: `npm run dev` (in `nmtsa_lms`)
- Production build: `npm run build`

Tailwind compiles `static/css/input.css` → `static/css/output.css`. Ensure templates reference the generated output.


## Running Tests

```bash
cd nmtsa_lms
python manage.py test
```

Targeted apps:
- `authentication/tests.py`
- `teacher_dash/tests.py`
- `lms/tests.py`
- `student_dash/tests.py`


## Payments (PayPal Sandbox Quick Test)

1) Set `PAYPAL_ENV=sandbox` and provide sandbox credentials in `.env`.
2) Start the app, set a course to paid with a price.
3) Use a PayPal sandbox buyer to complete a test purchase.
4) Verify enrollment unlock and transaction state stored.

See `docs/PAYPAL_QUICK_TEST.md` and `docs/PAYPAL_INTEGRATION_SUMMARY.md` for details.


## Supermemory (AI Chat + Search)

1) Provide `SUPERMEMORY_API_KEY`, `SUPERMEMORY_BASE_URL`, and `SUPERMEMORY_PROJECT_ID` in `.env`.
2) Chat endpoints (REST):
	 - `GET /lms/api/chat/rooms/`
	 - `GET /lms/api/chat/rooms/<id>/messages/`
	 - `POST /lms/api/chat/rooms/<id>/send/`
	 - `POST /lms/api/chat/rooms/<id>/typing/`
	 - `GET /lms/api/chat/rooms/<id>/typing/status/`
3) Semantic course search: `POST /lms/api/courses/search/`
4) Course memory syncing: see `lms/course_memory.py` and `lms/supermemory_client.py`.

Refer to `docs/SUPERMEMORY_SETUP_GUIDE.md` and `docs/CHAT_IMPLEMENTATION.md` for end-to-end steps.


## Provider Setup: Auth0, Supermemory, and Gemini

Below is a quick, practical guide to get credentials and wire them up with this repo. For deeper context, see the docs referenced at the end of each section.

### Auth0 (OAuth for Students/Teachers)

What you’ll create in Auth0:
- A Regular Web Application (OIDC)

Allowed URLs (must match your Django routes):
- Allowed Callback URLs: http://127.0.0.1:8000/callback
- Allowed Logout URLs: http://127.0.0.1:8000/
- Allowed Web Origins: http://127.0.0.1:8000

Steps:
1) Sign in at https://manage.auth0.com and create a Regular Web Application.
2) In Settings, set the Allowed URLs exactly as above for local dev.
3) Copy Domain, Client ID, and Client Secret.
4) Add these to your `.env` at the repo root:
	- AUTH0_DOMAIN=your-tenant.us.auth0.com
	- AUTH0_CLIENT_ID=...
	- AUTH0_CLIENT_SECRET=...
5) Start the server and test the flow:
	- Visit http://127.0.0.1:8000/login
	- Complete Auth0 login
	- You’ll be routed to role selection → onboarding → dashboard

Notes:
- Admins use Django username/password at /auth/admin-login/ (not Auth0).
- If you see a redirect_mismatch error, re-check your Callback/Logout URLs.

See also: `docs/AUTH_SYSTEM_SUMMARY.md`, `docs/AUTHENTICATION_COMPLETE.md`.

### Supermemory (AI memory + semantic search)

What you’ll get:
- An API key (optionally a project ID; base URL defaults to https://api.supermemory.ai)

Steps:
1) Create an account at https://supermemory.ai and generate an API key.
2) Add to your `.env`:
	- SUPERMEMORY_API_KEY=...
	- SUPERMEMORY_BASE_URL=https://api.supermemory.ai
	- SUPERMEMORY_PROJECT_ID=nmtsa-lms
3) Install required packages (already listed in requirements.txt):
	- supermemory
	- openai (used for Google Gemini via Memory Router)
4) Seed and sync memories (optional but recommended):
	- python manage.py seed_website_memory
	- python manage.py sync_courses_to_memory

Test:
- Chat endpoints under /lms/api/chat/... will respond using memory.
- Semantic search via POST /lms/api/courses/search/.

See also: `docs/SUPERMEMORY_SETUP_GUIDE.md`, `docs/SUPERMEMORY_INTEGRATION_SUMMARY.md`, `docs/CHAT_IMPLEMENTATION.md`, `docs/SUPERMEMORY_QUICK_REF.md`.

### Google Gemini (free tier)

What you’ll get:
- A free API key from Google AI Studio.

Steps:
1) Visit https://makersuite.google.com/app/apikey and create an API key.
2) Add to your `.env`:
	- GEMINI_API_KEY=AIza... (your key)
3) Ensure packages are installed (requirements.txt includes openai which powers Gemini via Memory Router).

How it’s used here:
- The `lms/supermemory_client.py` uses Supermemory’s Memory Router with Gemini to generate responses while injecting relevant memories.
- Env var is read in `nmtsa_lms/settings.py` and in the Supermemory client.

Troubleshooting:
- If chat returns a configuration error, verify SUPERMEMORY_API_KEY and GEMINI_API_KEY are present and correct.
- Check server logs for “Supermemory not configured” or OpenAI client initialization errors.


## Deployment (Production)

Recommended stack: Nginx → Gunicorn/Uvicorn → Django (ASGI) + Postgres + object storage (for media) + CDN (optional)

1) Environment
- Set `DEBUG=false`, strong `SECRET_KEY`, and `ALLOWED_HOSTS` to your domain(s)
- Configure `DATABASE_URL` to PostgreSQL
- Configure Auth0/PayPal/Supermemory for production (new credentials)

2) Build assets
```bash
cd nmtsa_lms
npm run build
```

3) Collect static files
```bash
cd nmtsa_lms
python manage.py collectstatic --noinput
```

4) Run migrations
```bash
cd nmtsa_lms
python manage.py migrate
```

5) Start application server
- Example (ASGI with Gunicorn + Uvicorn worker):
```bash
gunicorn nmtsa_lms.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

6) Configure Nginx
- Proxy `location /` to `127.0.0.1:8000`
- Serve static (`/static/`) and media (`/media/`) from disk or object storage/CDN
- Enable HTTPS (Let’s Encrypt recommended) and HSTS

7) Media storage (recommended)
- Use S3-compatible storage for `media/` and a CDN for performance

8) Background tasks (optional)
- Add Redis + Celery for long-running tasks if needed

9) Monitoring
- Logs, metrics, and uptime checks; consider error reporting tools


## Security Hardening Checklist

- DEBUG=false in production
- Strong `SECRET_KEY`; rotate credentials regularly
- `ALLOWED_HOSTS` restricted to known domains
- CSRF and session cookies set `Secure`, `HttpOnly`, `SameSite`
- CORS locked to allowed origins only
- Security headers: CSP, X-Frame-Options, X-Content-Type-Options, HSTS via proxy
- Validate/sanitize uploads (MIME types, size limits)
- Minimal PII; no PHI; adhere to OWASP Top 10 mitigations
- Admin actions and payment events audited


## Troubleshooting

- OAuth redirect mismatch
	- Ensure Auth0 callback URL matches your `http(s)://<host>/callback`
- Static/Tailwind not updating
	- Verify `npm run dev` is running or re-run `npm run build`
- Database errors after pull
	- Run `python manage.py migrate` and optionally `python manage.py makemigrations`
- Admin login not working
	- Use `/auth/admin-login/` and ensure your user has `role='admin'` and `onboarding_complete=True`
- Media not loading in prod
	- Check storage configuration and Nginx location blocks


## Useful Commands (reference)

```bash
# Activate venv (Windows bash)
source .venv/Scripts/activate

# Migrations
cd nmtsa_lms
python manage.py makemigrations
python manage.py migrate

# Run dev server
python manage.py runserver

# Tailwind
npm run dev      # watch
npm run build    # production build

# Seed demo
python manage.py seed_demo_courses

# Tests
python manage.py test
```


## Documentation

- SRS: `docs/SRS_NMTSA_LMS_FULL.md`
- Auth: `docs/AUTH_SYSTEM_SUMMARY.md`, `docs/AUTHENTICATION_COMPLETE.md`
- Payments: `docs/PAYPAL_INTEGRATION_SUMMARY.md`, `docs/PAYPAL_QUICK_TEST.md`
- AI Chat/Search: `docs/CHAT_IMPLEMENTATION.md`, `docs/SUPERMEMORY_SETUP_GUIDE.md`
- Localization: `docs/LOCALIZATION_GUIDE_EN_ES.md`
- SEO/Sitemaps/Schema: `docs/SEO_COMPLETE_CHECKLIST.md`, `docs/SCHEMA_IMPLEMENTATION_GUIDE.md`


---

Built for NMTSA to reduce administrative burden, create new revenue streams, and provide better support for families and healthcare professionals through evidence-based educational content.

## Hackathon & Team Info

Please replace the placeholder values below with your real links and names before submission.

- Team name: NMTSA-LMS Team
- Team members: Alice Example, Bob Example, Carol Example (replace with real names)
- Slack channel: #nmtsa-lms (replace with your workspace channel or invite link)

Problem statement
- Provide an accessible, trackable online learning platform for neurologic music therapy education that supports dual authentication, teacher verification, course review workflows, student progress tracking, and an AI assistant for search and chat.

Live demo / Judges
- Working project (live/demo): <REPLACE_WITH_LIVE_URL>
- DevPost: <REPLACE_WITH_DEVPOST_URL>
- Final demo video: <REPLACE_WITH_FINAL_VIDEO_URL>

Designs & repo links
- Figma (designs): <REPLACE_WITH_FIGMA_LINK>
- GitHub (this repo): <REPLACE_WITH_GITHUB_REPO_URL>

Notes
- The canonical "Tech Stack" and "Quick Start (Development)" / run instructions are provided earlier in this README — please use those sections as the authoritative source to avoid duplication.
- Replace all <REPLACE_...> placeholders with final values before submitting to judges. If you send me the final values I can fill them in for you.
