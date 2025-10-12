# NMTSA Learning Management System (LMS) — Software Requirements Specification (SRS)

Version: 1.0 • Date: 2025-10-12

Owner: NMTSA (Neurologic Music Therapy Services of Arizona)

Repository: nmstaeducationlms

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) defines the comprehensive functional and non-functional requirements for the NMTSA Learning Management System (LMS). The document is intended for:
- Stakeholders and leadership at NMTSA
- Product managers and UX designers
- Software engineers and QA testers
- DevOps and security teams
- External reviewers (e.g., grant committees, accreditation partners)

Objectives:
- Provide a single authoritative source of truth for scope, behavior, and constraints
- Enable reliable estimation, development, testing, and compliance reviews
- Reduce ambiguity through clear acceptance criteria and traceability

### 1.2 Scope
NMTSA requires a robust LMS to consolidate and deliver professional education for healthcare providers (continuing education and NMT certification) and resources for clients/families (free and paid content). The system will:
- Support dual authentication: OAuth (Auth0) for students/teachers, Django admin for admins
- Provide role-based access control (RBAC) with teacher verification workflow
- Manage courses, modules, lessons (video and blog), and downloadable resources
- Stream videos and track progress and completion
- Process payments for paid courses and generate certificates for CE credits
- Offer discussion forums, semantic search, and an AI assistant with persistent memory
- Ensure mobile-friendly, accessible (WCAG 2.1 AA+/AAA-aligned) UX with autism-friendly options
- Provide analytics to monitor engagement, course effectiveness, and system health

Boundaries:
- Focused on learning content delivery and community interaction; not a full EHR
- Payments limited to PayPal (per repo docs) for MVP

### 1.3 Definitions, Acronyms, and Abbreviations
- NMTSA: Neurologic Music Therapy Services of Arizona
- NMT: Neurologic Music Therapy
- LMS: Learning Management System
- RBAC: Role-Based Access Control
- OAuth: Open standard for authorization
- Auth0: OAuth/OIDC identity provider
- OIDC: OpenID Connect
- SSO: Single Sign-On
- MFA: Multi-Factor Authentication
- AMTA: American Music Therapy Association
- CE: Continuing Education
- UI/UX: User Interface / User Experience
- A11Y: Accessibility
- WCAG: Web Content Accessibility Guidelines
- CDN: Content Delivery Network
- API: Application Programming Interface
- REST: Representational State Transfer
- CSRF/CORS: Cross-Site Request Forgery / Cross-Origin Resource Sharing
- CI/CD: Continuous Integration / Continuous Delivery
- SLA/SLO/SLI: Service Level Agreement / Objective / Indicator
- PII: Personally Identifiable Information

### 1.4 Overview
The remainder of this SRS documents overall description (Section 2), system features (Section 3), external interfaces (Section 4), non-functional requirements (Section 5), database requirements (Section 6), system architecture (Section 7), and other requirements (Section 8). A rubric alignment appendix maps the solution to judging criteria.

---

## 2. Overall Description

### 2.1 Product Perspective
The LMS is a multi-app Django web application using a custom User model and centralized template system. It integrates with:
- Auth0 for OAuth (students/teachers)
- Django admin with username/password for admins
- PayPal for payment processing
- Supermemory AI for chat and semantic course search
- MoviePy (where needed) for video processing
- Tailwind for CSS with autism-friendly themes
- SQLite (current dev) and PostgreSQL (recommended prod).
It replaces scattered Google Drive content and manual processes with a unified, secure, and trackable platform.

### 2.2 Product Functions
High-level capabilities:
- Authentication + RBAC (student, teacher, admin) with onboarding and teacher verification
- Course and lesson management (video/blog), media uploads, transcripts, images
- Enrollment, progress tracking, video resume, completion, and CE certificate generation
- Payments for paid courses, publish/review workflow, admin approvals
- Discussion forums per course
- AI chat assistant with memory, semantic search across courses and resources
- SEO and sitemaps, localization (EN/ES), mobile-friendly responsive UI
- Analytics and audit logs

### 2.3 User Classes and Characteristics
- Visitor/Guest: Unauthenticated, can browse public landing pages and chat
- Student/Family: Authenticated via OAuth; consumes courses and resources; may purchase courses; mobile-compatible usage
- Teacher/Educator/Therapist: Authenticated via OAuth; must complete onboarding and be verified by admins; uploads courses and lessons; professional users
- Admin: Authenticated via Django admin login; verifies teachers, reviews and approves courses, manages global settings; highly trusted users

### 2.4 Operating Environment
- Client: Modern browsers (Chrome, Edge, Safari, Firefox) on desktop and mobile; responsive layout
- Server: Python 3.10+, Django 4.x+, Linux (Ubuntu) or Windows Server; Gunicorn/Uvicorn + Nginx (recommended)
- Database: SQLite for development, PostgreSQL for production
- Storage: Local filesystem for media in dev; S3-compatible object storage recommended for prod; CDN optional
- Dependencies: Auth0 tenant, PayPal credentials, Supermemory API key, Gemini API key

### 2.5 Design and Implementation Constraints
- Custom User model must remain AUTH_USER_MODEL
- Dual auth architecture: OAuth for teachers/students; Django auth for admins only
- Teacher actions gated by verification status
- Published courses automatically unpublish and re-enter review upon edits
- Accessibility: zero animations/auto-play; themes and font size controls persist with localStorage
- Security: Only minimal PII; no PHI handling; must follow OWASP best practices
- Budget/hosting constraints: prefer open-source and cost-effective services

### 2.6 User Documentation
- Inline help, tooltips, and onboarding guides
- Public README and QUICK_START for developers
- Admin handbook for verification and course review workflows
- Teacher upload guide with formatting/validation rules
- Student FAQ for enrollment, playback, and certificates

### 2.7 Assumptions and Dependencies
- Reliable internet connection for streaming and OAuth redirects
- Auth0, PayPal, and Supermemory services are available and reachable
- Media encoding is browser-compatible (H.264 MP4 recommended)

---

## 3. System Features
Each feature is specified with Description & Priority, Stimulus/Response sequences, Functional Requirements (FR-IDs), UI Requirements, and Backend Requirements.

### 3.1 Authentication & RBAC
- Description & Priority: Provide secure login and role enforcement using Auth0 (students/teachers) and Django admin auth (admins). Priority: High.
- Stimulus/Response:
  - User clicks Login → OAuth redirect to Auth0 → Callback stores session userinfo → Role selection if missing → Onboarding redirect if needed → Dashboard
  - Admin visits /auth/admin-login/ → Username/password → Admin dashboard
- Functional Requirements:
  - FR-AUTH-1: Implement OAuth login via Auth0 using global OAuth instance. Acceptance: Successful redirect, userinfo stored in session.
  - FR-AUTH-2: Enforce role selection and onboarding completion before dashboard access. Acceptance: Unauthorized redirects.
  - FR-AUTH-3: Provide Django admin login strictly for admins; block OAuth for admins. Acceptance: Admin login succeeds; admin role enforced.
  - FR-AUTH-4: Middleware syncs Auth0 user to local User model each request. Acceptance: Local user fields updated from session.
  - FR-AUTH-5: RBAC decorators enforce role access at view level (student_required, teacher_required, admin_required, teacher_verified_required, onboarding_complete_required). Acceptance: Access control test coverage.
- UI Requirements:
  - Login, role selection, and onboarding screens accessible and responsive
  - Clear error and success states; no animations; large touch targets on mobile
- Backend Requirements:
  - nmtsa_lms/views.py for OAuth flow; authentication/middleware.py for sync; decorators for RBAC
  - Session key: request.session['user'] with userinfo, role, onboarding_complete

### 3.2 Teacher Onboarding & Verification
- Description & Priority: Collect teacher credentials and route to admin for approval. Priority: High.
- Stimulus/Response:
  - Teacher logs in first time → Selects role → Completes onboarding form (resume, certifications) → Status pending → Admin reviews → Approved or rejected
- Functional Requirements:
  - FR-TEACH-1: Store TeacherProfile with verification_status (pending, approved, rejected). Acceptance: Status transitions persisted.
  - FR-TEACH-2: Block course creation/editing until approved. Acceptance: Decorator prevents access pre-approval.
  - FR-TEACH-3: Allow re-submission after rejection with feedback. Acceptance: Updated documents and notes visible to admin.
- UI Requirements:
  - Upload forms with validation and accessible inputs; progress indicators for uploads
- Backend Requirements:
  - authentication/models.py (TeacherProfile), views.py for onboarding, admin_dash for verification views

### 3.3 Course Management & Review Workflow
- Description & Priority: Full CRUD for courses/modules/lessons with admin review and publish. Priority: High.
- Stimulus/Response:
  - Teacher creates course → Adds modules/lessons → Submits for review → Admin approves/rejects → Teacher publishes → Students enroll
  - Edit published course → Auto unpublish + re-submit for review
- Functional Requirements:
  - FR-COURSE-1: Course states: is_published, is_submitted_for_review, admin_approved. Acceptance: State machine respected.
  - FR-COURSE-2: Submission locks editing except via review flow. Acceptance: UI/logic prevents edits during review.
  - FR-COURSE-3: Auto-unpublish and resubmit on content edits. Acceptance: Trigger on save.
  - FR-COURSE-4: Tagging, descriptions, pricing, and paid/free flags supported. Acceptance: Fields persisted and validated.
- UI Requirements:
  - Forms with preview; clear status badges; publish controls post-approval
- Backend Requirements:
  - teacher_dash/models.py, forms.py, views.py; admin_dash for review

### 3.4 Lesson Types: Video and Blog
- Description & Priority: Support base Lesson with VideoLesson or BlogLesson details. Priority: High.
- Stimulus/Response:
  - Teacher uploads video file and transcript OR writes blog content with images → Students view appropriately
- Functional Requirements:
  - FR-LESSON-1: Base Lesson with lesson_type, duration, and 1:1 to VideoLesson/BlogLesson. Acceptance: ORM relationships correct.
  - FR-LESSON-2: VideoLesson stores video_file (media/videos) and transcript; BlogLesson stores content and images. Acceptance: Upload, storage, retrieval work.
  - FR-LESSON-3: File type/size validation. Acceptance: Rejected invalid uploads.
- UI Requirements:
  - Accessible video player with captions; readable blog typography; image alt text
- Backend Requirements:
  - Media storage in media/, settings serve MEDIA_URL in DEBUG; production to object storage recommended

### 3.5 Enrollment & Student Progress
- Description & Priority: Track enrollments, lesson completion, and progress. Priority: High.
- Stimulus/Response:
  - Student enrolls → Progress updates as lessons completed → Completion triggers certificate
- Functional Requirements:
  - FR-ENR-1: Enrollment model linking Student ↔ Course with progress percentage and completed flag. Acceptance: Accurate aggregation.
  - FR-ENR-2: CompletedLesson unique per Enrollment/Lesson. Acceptance: Idempotent completion marking.
  - FR-ENR-3: VideoProgress save last_position_seconds, completed_percentage. Acceptance: Resume playback.
- UI Requirements:
  - Progress bars; resume indicators; completion badges
- Backend Requirements:
  - authentication/models.py (Enrollment); lms/models.py (CompletedLesson, VideoProgress)

### 3.6 Video Hosting, Streaming & Tracking
- Description & Priority: Upload, stream, and track videos with resume. Priority: High.
- Stimulus/Response:
  - Student plays a video → Player reports time updates → Server stores progress → Completion at threshold
- Functional Requirements:
  - FR-VID-1: Use HTML5 video with compatible codec; no auto-play. Acceptance: Manual play only, captions supported.
  - FR-VID-2: Update progress periodically; mark completed at 90% watched. Acceptance: Threshold configurable.
  - FR-VID-3: Support transcripts and downloadable resources. Acceptance: Transcript rendering.
- UI Requirements:
  - Large controls; keyboard accessible; high-contrast theme compatibility
- Backend Requirements:
  - Endpoints to record progress; model updates; optional MoviePy utilities

### 3.7 Payments & Monetization (PayPal)
- Description & Priority: Process payments for paid courses. Priority: High.
- Stimulus/Response:
  - Student clicks Buy → PayPal checkout → Return webhook/redirect → Enrollment unlocked
- Functional Requirements:
  - FR-PAY-1: Integrate PayPal per docs with sandbox and live modes. Acceptance: Successful test transaction.
  - FR-PAY-2: Mark course enrollment as paid upon verified capture. Acceptance: Enrollment state updated; receipts logged.
  - FR-PAY-3: Handle refunds/chargebacks via admin tools. Acceptance: Manual or automated state adjustments.
- UI Requirements:
  - Clear pricing; disabled access until paid; error handling on failed payments
- Backend Requirements:
  - nmtsa_lms/paypal_service.py; secure webhook validation; idempotent processing

### 3.8 Certificates for CE Credits
- Description & Priority: Generate certificates upon completion, with CE metadata. Priority: Medium-High (critical for professionals).
- Stimulus/Response:
  - Enrollment reaches completion → Certificate generated (PDF) → Download link/email
- Functional Requirements:
  - FR-CERT-1: Certificate contains user name, course title, hours, date, unique ID, instructor, and AMTA-aligned fields. Acceptance: PDF validated.
  - FR-CERT-2: Regenerate on demand; prevent tampering (hash/ID). Acceptance: Stable, consistent output.
- UI Requirements:
  - Accessible download; clear instructions for CE reporting
- Backend Requirements:
  - Use PDF generation utilities per docs; store metadata and unique identifiers

### 3.9 Discussion Forums
- Description & Priority: Facilitate peer interaction in courses. Priority: Medium.
- Stimulus/Response:
  - Student/Teacher posts → Thread appears → Replies and notifications
- Functional Requirements:
  - FR-DISC-1: DiscussionPost model linked to course/module with author and timestamps. Acceptance: CRUD works with RBAC.
  - FR-DISC-2: Moderation controls for teachers/admins. Acceptance: Delete/lock threads.
- UI Requirements:
  - Threaded view; markdown or rich text support; report abuse affordances
- Backend Requirements:
  - teacher_dash/models.py (DiscussionPost) and related views

### 3.10 AI Chat & Semantic Search (Supermemory)
- Description & Priority: AI assistant with memory and course-aware search. Priority: High.
- Stimulus/Response:
  - User opens chat → Asks question → AI responds; memory enhanced; semantic search returns courses
- Functional Requirements:
  - FR-CHAT-1: REST endpoints: /lms/api/chat/rooms/, /rooms/<id>/messages/, /send/, /typing/, /typing/status/. Acceptance: 200 responses and expected JSON.
  - FR-CHAT-2: Supermemory chat_completion with use_memory=True. Acceptance: Contextual replies.
  - FR-CHAT-3: Add memory events (enrollment, progress) and course sync to memory. Acceptance: Memory entries present.
  - FR-SEARCH-1: /lms/api/courses/search/ performs semantic search via Supermemory. Acceptance: Relevant ranked results.
- UI Requirements:
  - templates/components/chat.html and static/js/chat.js with typing indicators and history
- Backend Requirements:
  - lms/views.py, lms/supermemory_client.py, lms/course_memory.py

### 3.11 SEO & Sitemaps
- Description & Priority: Improve discoverability. Priority: Medium.
- Functional Requirements:
  - FR-SEO-1: Generate sitemap via lms/sitemaps.py. Acceptance: Valid sitemap.xml.
  - FR-SEO-2: Apply meta tags and schema.org as per docs. Acceptance: Lighthouse SEO pass.

### 3.12 Localization (EN/ES)
- Description & Priority: Internationalization for English and Spanish. Priority: Medium.
- Functional Requirements:
  - FR-I18N-1: Implement translation hooks in templates and views. Acceptance: Language toggle works.
  - FR-I18N-2: Provide locale-based content for key pages. Acceptance: Strings externalized and translated.

### 3.13 Accessibility & Autism-Friendly UI
- Description & Priority: Meet WCAG, support sensory-friendly design. Priority: High.
- Functional Requirements:
  - FR-A11Y-1: Provide 4 themes (Light, Dark, High Contrast, Minimal) and font-size controls; persist via localStorage. Acceptance: Theme persistence across sessions.
  - FR-A11Y-2: No animations/auto-play; keyboard navigation; ARIA labels. Acceptance: Axe/Lighthouse Accessibility pass (>= 95).

### 3.14 Analytics & Reporting
- Description & Priority: Track engagement and course effectiveness. Priority: Medium.
- Functional Requirements:
  - FR-ANL-1: Aggregate enrollments, completions, and time-on-video per course. Acceptance: Admin dashboard metrics present.
  - FR-ANL-2: Export CSV for accreditation reporting. Acceptance: CSV columns match spec.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- Responsive UI built with Tailwind; centralized templates in nmtsa_lms/templates/
- Primary pages: Landing, Login/Callback, Role Selection, Teacher Onboarding, Dashboards (student/teacher/admin), Course Catalog, Course Detail, Lesson Player/Reader, Checkout, Certificates, Discussions, Chat
- Accessibility: WCAG 2.1 AA+/AAA lean; keyboard-first; high contrast; no auto-play; focus outlines; alt text; semantic HTML
- Navigation: Top navbar + optional sidebar; breadcrumbs inside course context

### 4.2 Hardware Interfaces
- None direct. Server hardware provisioned by hosting provider; recommendations documented in deployment section.

### 4.3 Software Interfaces
- Auth0 OAuth/OIDC: authorize, callback endpoints; uses environment variables AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET
- PayPal: Orders API for checkout/capture; webhooks for event confirmation
- Supermemory: Chat endpoints and semantic search via API key, base URL, project ID
- MoviePy: Optional for video processing tasks
- Django Admin: Admin verification and model management

### 4.4 Communications Interfaces
- Protocols: HTTPS for all client-server communications; HSTS recommended
- APIs: RESTful JSON endpoints under /lms/api/* for chat and search; CSRF-protected POSTs where applicable
- Authentication/Authorization: Session-based after OAuth; RBAC decorators enforce access; admin via Django auth
- Versioning: URL versioning reserved for future (v1)

---

## 5. Non-Functional Requirements (NFRs)

### 5.1 Performance
- P95 page load time for authenticated dashboard: <= 1.2s on broadband; P99 <= 2.5s
- API latency P95: <= 300ms for standard endpoints, excluding third-party network calls
- Video streaming uses HTTP range requests; server should support chunked responses
- Concurrency target (MVP): 500 concurrent users; scale-out guidance provided

### 5.2 Security
- OAuth/OIDC via Auth0 with PKCE; rotate secrets; store only minimal userinfo
- RBAC enforced via decorators; admins restricted to Django login only
- CSRF protection on state-changing endpoints; CORS locked to known origins
- Passwords hashed (Django default); sessions secured (Secure, HttpOnly, SameSite=Lax/Strict)
- Input validation and file upload sanitization; restrict media MIME types and sizes
- OWASP Top 10 mitigations documented; dependency scanning in CI; security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- Audit logging for admin actions, payments, and verification changes

### 5.3 Usability
- Autism-friendly controls: themes, large fonts, no flashing/animation
- Mobile-first layouts with touch targets >= 44px; readable color contrast ratios
- Clear empty states, error handling, and success feedback

### 5.4 Reliability
- Uptime SLO: 99.9% (excludes scheduled maintenance)
- Data durability: Daily backups of DB and media metadata; RPO <= 24h, RTO <= 4h
- Idempotent payment and progress update handlers; retry with backoff

### 5.5 Maintainability
- Django app modularization: authentication, teacher_dash, student_dash, lms, admin_dash
- Style and linting per repo conventions; tests in each app; fixtures/seed commands provided
- Structured logging with correlation IDs for request tracing where possible
- Config via environment variables; 12-factor principles

### 5.6 Portability
- Dev: Windows/macOS/Linux via virtualenv; SQLite default
- Prod: Linux container recommended; Postgres; S3-compatible storage; Nginx + Gunicorn/Uvicorn
- Dockerization recommended but optional for MVP

### 5.7 Scalability
- Stateless web tier for horizontal scaling; sticky sessions avoided where possible
- DB vertical scaling and read replicas (future); caching layer optional
- Media served via CDN for global performance (future enhancement)

---

## 6. Database Requirements

### 6.1 Data Model (Conceptual)
Entities and relationships (see models files for canonical definitions):
- User (custom): role, onboarding_complete, profile links
- TeacherProfile: user↔1:1, verification_status, resume, certifications
- StudentProfile: user↔1:1
- Course: teacher FK, title, description, tags, price, is_paid, is_published, is_submitted_for_review, admin_approved
- Module: title, order; Many-to-Many with Course
- Lesson (base): module M2M, lesson_type, duration; O2O to VideoLesson OR BlogLesson
- VideoLesson: video_file, transcript
- BlogLesson: content, images
- Enrollment: student↔course, progress_percentage, completed, timestamps
- CompletedLesson: enrollment↔lesson (unique together)
- VideoProgress: enrollment↔lesson, last_position_seconds, completed_percentage
- DiscussionPost: course/module FK, author FK, body, timestamps
- Payment/Transaction: records PayPal order/capture IDs (as modeled in migrations)

### 6.2 Data Dictionary (Key Fields)
- User: id (PK), email (unique), role [admin|teacher|student], onboarding_complete (bool)
- TeacherProfile: id, user_id (unique), verification_status [pending|approved|rejected], resume_file, certification_files
- Course: id, teacher_id, title (idx), description (full-text search planned), is_paid (bool), price (decimal), is_published (bool), is_submitted_for_review (bool), admin_approved (bool)
- Module: id, title, order
- Lesson: id, lesson_type [video|blog], duration (int)
- VideoLesson: id, video_file (path), transcript (text)
- BlogLesson: id, content (text), images (paths)
- Enrollment: id, student_id, course_id, progress_percentage (0-100), completed (bool)
- CompletedLesson: id, enrollment_id, lesson_id (unique pair)
- VideoProgress: id, enrollment_id, lesson_id, last_position_seconds (int), completed_percentage (0-100)
- DiscussionPost: id, course_id, module_id?, author_id, body, created_at
- Payment: id, order_id (unique), payer_id, amount, currency, status, captured_at

Constraints and Indexing:
- Unique together: (enrollment_id, lesson_id) in CompletedLesson and VideoProgress
- Indexes on Course.title, Course.is_published, Enrollment.course_id, Enrollment.student_id
- Foreign keys cascade rules per models; soft deletes out of scope

### 6.3 Data Access Layer
- Django ORM for all CRUD and aggregation
- Select_related/prefetch_related to reduce N+1 queries on dashboards/catalog
- Transactions for payment capture and enrollment changes; idempotency keys for webhooks

### 6.4 Backup and Recovery
- Daily automated DB backups; retain 30 days
- Test restore quarterly
- Media: store original uploads in redundant storage; maintain checksums for integrity

---

## 7. System Architecture

### 7.1 Architectural Design
- Web MVC via Django; apps: authentication, teacher_dash, student_dash, lms, admin_dash
- OAuth handled once via global OAuth() instance in nmtsa_lms/views.py; middleware syncs with DB
- Templates centralized with components; Tailwind pipeline for CSS
- Media served from media/ in dev; object storage and CDN in prod

### 7.2 Component Diagram (Narrative)
- Client (Browser)
  - Interacts with Django views/templates and REST endpoints (chat/search)
- Server (Django)
  - authentication: user, profiles, onboarding, RBAC
  - teacher_dash: course/lesson management and review submission
  - admin_dash: verifications and course approvals
  - lms: chat/search APIs, progress tracking, sitemaps
- External Services
  - Auth0 for OAuth; PayPal for payments; Supermemory for AI/search
- Data Layer
  - PostgreSQL (prod) / SQLite (dev); media storage; logs/metrics

### 7.3 Deployment Architecture
- Environments: Dev, Staging, Production
- Recommended stack: Nginx → Gunicorn/Uvicorn → Django apps; Redis (optional) for caching/session
- CI/CD: GitHub Actions (suggested) with lint/tests, migrations, and deploy steps
- Configuration via environment variables (.env for local)

---

## 8. Other Requirements

### 8.1 Legal and Licensing
- Comply with GDPR/CCPA where applicable for PII; transparent privacy policy
- Content licensing: Ensure rights for videos, transcripts, and images; copyright held by NMTSA or licensed
- Third-party licenses (Django, Tailwind, MoviePy) tracked via requirements

### 8.2 Localization
- Support English and Spanish per localization docs; ensure date/number formats respect locale
- Content authors can supply localized descriptions and titles where relevant

### 8.3 Ethical and Accessibility
- Prioritize inclusive design for neurodivergent users: zero animations, high contrast, predictable navigation
- No dark patterns; clear consent and opt-out for data collection

---

## 9. Acceptance, Testing, and Traceability
- Each FR is testable with view tests, API tests, and integration tests. Map tests to FR IDs in test docstrings.
- Seed command (teacher_dash.management.commands.seed_demo_courses) enables demo verification
- Accessibility and SEO checks via Lighthouse; security checks via OWASP ZAP (optional)

---

## 10. Risks and Mitigations
- Third-party dependency outages (Auth0, PayPal, Supermemory) → Graceful degradation and retries; status page monitoring
- Video storage costs → Use object storage with lifecycle policies; compress and transcode appropriately
- Content moderation burden → Provide reporting tools and moderation controls

---

## 11. Roadmap and Work Remaining (MVP → V1)
- MVP: Auth + RBAC, onboarding/verification, course CRUD and review workflow, video/blog lessons, enrollments, progress, payments, certificates (basic), discussions (basic), chat/search (baseline), localization (core), accessibility, SEO/sitemaps
- V1: Analytics dashboards, refund tooling, CDN integration, advanced certificate templates, richer moderation, Docker and IaC, end-to-end tests, object storage

---

## Appendix A — Rubric Alignment

1) Scope of Solution
- Impact on Community: Serves healthcare professionals and families; scalable to thousands via web; supports nonprofits and clinics partnering with NMTSA
- Complexity of Problem Solved: Consolidates fragmented content, payments, accreditation requirements, and community into an accessible LMS with AI-assisted discovery; improves beyond generic LMS by autism-friendly UI and CE certificates

2) Documentation
- Code and UX Documentation: This SRS, repo docs for auth, payments, chat, localization, and quick start; inline help and onboarding
- Ease of Understanding: Modular Django apps, clear RBAC decorators, centralized templates/components, well-defined workflows

3) Polish
- Work Remaining: Minimal for MVP per roadmap; comprehensive workflows defined; seed data for demos
- Can Use Today: Deployable to cloud with standard Django stack; PayPal sandbox and Auth0 config ready; SQLite dev → Postgres prod

4) Security
- Data Protection: OAuth with Auth0, CSRF, secure sessions, minimal PII, hardened headers, upload validation, audit logs
- Role-based Security: Strict separation—admins via Django auth only; student/teacher via OAuth; decorators and middleware enforce access; teacher verification gates authoring

---

End of Document.
