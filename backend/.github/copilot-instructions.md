# NMTSA LMS - AI Coding Assistant Instructions

## Project Overview
This is a Django-based Learning Management System (LMS) for NMTSA with Auth0 integration for authentication. The project uses a simplified Django structure with all main logic in the root `nmtsa_lms` module.

## Architecture Patterns

### Single-Module Django Structure
- **Project root**: `nmtsa_lms/` contains `manage.py` and the main Django project
- **Main module**: `nmtsa_lms/nmtsa_lms/` contains all views, URLs, settings, and templates
- **No separate apps**: All functionality is in the main project module (not standard Django app structure)
- **Templates location**: `nmtsa_lms/nmtsa_lms/templates/` (configured via `TEMPLATE_DIR` in settings)

### Authentication Architecture
- **Auth0 Integration**: Uses Authlib for OAuth2/OpenID Connect with Auth0
- **Session Management**: User data stored in Django sessions after Auth0 callback
- **OAuth Flow**: login → Auth0 → callback → session storage → redirect to index
- **Key files**: 
  - Views handle OAuth flow in `views.py`
  - Environment variables in `.env` (AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)

## Development Environment

### Python Setup
- **Python Version**: 3.13 (specified in `.python-version`)
- **Package Manager**: uv (has `uv.lock` file)
- **Virtual Environment**: `.venv/` directory
- **Dependencies**: Defined in `pyproject.toml` with Django 5.2.7, Authlib, DRF, python-dotenv

### Key Dependencies
```toml
django>=5.2.7
authlib>=1.6.5
django-restframework>=0.0.1
python-dotenv>=1.1.1
```

## Development Workflow

### Running the Project
```bash
# Activate virtual environment (if not using uv automatically)
.venv\Scripts\activate

# Run development server
cd nmtsa_lms
python manage.py runserver
```

### Environment Configuration
- **Required**: Create `.env` file with Auth0 credentials
- **Location**: Root directory (loaded via `python-dotenv`)
- **Variables**: AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET

### Database
- **Default**: SQLite (`db.sqlite3` in nmtsa_lms/)
- **Migrations**: Standard Django migrations (none exist yet)

## Code Conventions

### URL Patterns
- **Root URLs**: All defined in `nmtsa_lms/urls.py`
- **Pattern**: Function-based views imported from same module
- **Auth routes**: `/login`, `/logout`, `/callback` for Auth0 flow

### View Structure
- **File**: Single `views.py` contains all view logic
- **OAuth instance**: Global `oauth` object configured for Auth0
- **Session access**: `request.session.get("user")` for user data
- **Template context**: Includes both raw session and pretty-printed JSON

### Template Organization
- **Location**: `nmtsa_lms/templates/` (non-standard location)
- **Current**: Single `index.html` with conditional auth display
- **Context**: Expects `session` and `pretty` variables from views

## Integration Points

### Auth0 Configuration
- **Callback URL**: Must match Django's `/callback` route
- **Scopes**: "openid profile email" 
- **Discovery**: Uses Auth0's `.well-known/openid-configuration` endpoint

### Session Management
- **Storage**: Django's default session backend
- **Data**: Complete Auth0 token response stored as `user` key
- **Logout**: Clears Django session + redirects to Auth0 logout

## Important Notes for AI Agents

1. **Template Path**: Templates are in `nmtsa_lms/templates/`, not the standard `app/templates/` structure
2. **Environment Variables**: Always check `.env` exists and has Auth0 credentials before testing auth flows
3. **OAuth State**: The `oauth` object is globally configured - don't recreate it in views
4. **Session Data**: User info is nested as `session.userinfo` in templates (from Auth0 token structure)

# Project Plan and Requirements

## LMS Platform Architecture, Modules, Features, and Hackathon Priority

Each component is rated (1–10) by hackathon implementation priority for the NMTSA scenario, considering time constraints, impact on staff/admin workload, critical user experience for healthcare and family audiences, and revenue/education focus.

***

## 1. Authentication and User Management

### 1.1 Authentication **(10)**
- Essential for secure access
- Minimal but robust user signup and login, support for healthcare pro & client groups

### 1.2 Profile Management **(7)**
- Important for onboarding users, tracking key info for professional credits or family status

### 1.3 Payments Manager **(9)**
- Direct revenue stream; enables premium course access, invoices, and integration with Stripe/PayPal

***

## 2. Course and Lesson Management

### 2.1 Courses Manager **(10)**
- Critical to organize, publish, and track core training/professional courses for NMTSA and clients

### 2.2 Lessons Manager **(8)**
- Enables granular management of learning units (videos, docs); supports certification and credits

***

## 3. Role-Based Access Control

### 3.1 RBAC Dashboard **(8)**
- Needed for admin control, segmented access for healthcare pros, clients/families, and internal staff

***

## 4. Dashboards

### 4.1 Teacher Dashboard **(8)**
- Optimizes instructor workflow (uploading courses, content, videos) to reduce staff burden

### 4.2 Student Dashboard **(9)**
- Core for healthcare pro/client experience: enroll, track progress, get credits/certificates

### 4.3 Admin Dashboard **(7)**
- Reduces manual moderation, staff review—a key administrative benefit for NMTSA

***

## 5. Core LMS Features

### 5.1 Learning Experience **(10)**
- Course discovery and enrollment, progress tracking—must-have for learners and certification

### 5.2 Multimedia Content (Video Player) **(10)**
- Stored video streaming is vital for training, therapy, and education delivery
- Blog Reader **(5)** — nice-to-have for additional resources, less critical

***

## 6. AI and External Integrations

### 6.1 Supermemory Chat Integration **(5)**
- Adds support/feedback features; helpful but can be simplified/added later if needed

***

## 7. Profiles and User Flows

### 7.1 Profiles Component **(7)**
- As above, important for onboarding and credential management; not 100% urgent

***

## 8. Modular Summary Reference (Priority Breakdown)

- **Authentication (10):** Must be implemented for secure multi-user access
- **Profile Management (7):** Onboarding users, capturing credential/role info
- **Payments Manager (9):** Enable paid course access, automate receipts
- **Courses Manager (10):** Create, edit, organize courses for both user groups
- **Lessons Manager (8):** Upload, group, and deliver educational modules
- **RBAC Dashboard (8):** Control user/group permissions and platform segmentation
- **Teacher Dashboard (8):** Fast onboarding, course/video upload, admin-reducing workflows
- **Student Dashboard (9):** Discover, enroll, complete courses, access free/paid material
- **Admin Dashboard (7):** Moderate content/applications, automate staff workflows
- **Learning Experience (10):** Course discovery, enrollment, tracking, certificates
- **Multimedia - Video Player (10):** On-demand video streaming for core education/training
- **Blog Reader (5):** Supports additional context/resources
- **AI/Chat Integration (5):** Helpful support, optional under time constraints

***

*This plan identifies and prioritizes features for maximized impact and rapid execution targeted at NMTSA’s dual audience and urgent organizational needs in a 24-hour hackathon.*