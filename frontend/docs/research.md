### 🧠 **AI Agent Prompt — Full Frontend Generation**

**Prompt:**

Build a **complete, production-ready frontend** for a web-based **Learning Management System (LMS)** named **“NMTSA Learn”**, designed for **Comprehensive LMS for Professional Training & Client Education** for **Neurologic Music Therapy Services of Arizona (NMTSA)**.

### 🏗️ Core Requirements

- **Framework:** React + TypeScript
- **Bundler:** Vite
- **Styling:** Tailwind CSS v4
- **UI Library:** HeroUI
- **State Management:** Zustand
- **Routing:** React Router v7
- **Accessibility:** WCAG 2.2 AA compliant; fully keyboard-navigable, semantic HTML, ARIA attributes, focus rings, and skip links.
- **Responsiveness:** Fully responsive across all devices (desktop, tablet, mobile, large screens).
- **SEO Optimized:** Semantic structure, meta tags, dynamic page titles, Open Graph, schema.org structured data for courses, lessons, and authors.
- **Security:** Sanitize all inputs (especially markdown), prevent XSS/CSRF, safe rendering of HTML, and secure navigation patterns.
- **Performance:** Code splitting, lazy loading, image optimization, skeleton loaders, caching strategies.
- **Internationalization (i18n):** Multi-language support using `react-i18next`. Include sample English + Spanish setup.
- **Localization:** Date, currency, and language formatting handled dynamically.
- **Backend Integration:** Assume APIs are already available for auth, courses, progress, etc. (just connect to endpoints).

---

### 📚 Major Pages to Implement

#### 1. **Landing Page**

- Hero section (headline, CTA: “Explore Courses”)
- Featured courses carousel
- Categories section (filter by discipline or therapy area)
- Testimonials slider
- Partner logos and mission statement
- CTA buttons for “Join as Student” / “Become an Instructor”
- Footer with about, contact, accessibility, and language selector

#### 2. **Explore Courses Page**

- Search bar with autocomplete
- Filters (category, difficulty, duration, credits, rating)
- Sort dropdown (popularity, newest, difficulty)
- Responsive grid/list view
- Pagination or infinite scroll
- Each course card shows title, thumbnail, instructor, progress (if enrolled)

#### 3. **Course Detail Page**

- Hero banner with course title, description, difficulty, credits, rating
- Instructor bio and profile
- Accordion or collapsible section for course structure (modules → lessons)
- Enrollment button / Continue Learning if enrolled
- Estimated time, prerequisites, tags
- Student reviews and preview of discussion forum
- Course progress bar

#### 4. **Lesson Page**

- Markdown-based **lesson viewer**
- Embedded media (videos, PDFs, images)
- Lesson navigation sidebar (previous/next, jump to module)
- “Mark as complete” button
- Personal notes panel with autosave (stored locally)
- Lesson-level discussion/comment section
- Mini quiz UI (optional placeholder)
- Progress tracking visualization

#### 5. **User Dashboard**

- Overview: total learning hours, progress graph, credits earned, enrolled courses list
- Tabs: My Courses, Certificates, Progress Analytics, Notifications
- Progress charts using Recharts
- Quick resume for current courses
- Settings shortcut

#### 6. **Account Settings**

- Edit profile (photo, bio, contact info)
- Language & theme toggle (light/dark)
- Change password
- Notification preferences
- Delete account confirmation

#### 7. **Authentication Pages**

- Login / Register / Forgot Password / Email Verification
- Responsive, branded design using HeroUI components
- Role-based redirect (student → dashboard, instructor → instructor dashboard)

#### 8. **Student Application Page**

- Form for background, goals, eligibility
- File upload (CV, transcripts)
- Progress tracker (draft, submitted, under review)
- Review guidelines and submission confirmation modal

#### 9. **Teacher Application Page**

- Form for bio, credentials, expertise, intended course topics
- Upload certifications or proof
- Agreement checkbox for terms/policies
- Status tracker (pending, approved, rejected)

#### 10. **Discussion Forum**

- Course-wide and lesson-specific discussion boards
- Create post, reply, like, markdown editor with preview
- Threaded replies, pagination, and filters (newest, most liked)
- Instructor/moderator tags

#### 11. **Certificates Page**

- List of earned certificates
- Preview and download (PDF export)
- Share to LinkedIn or social
- Certificate verification link integration

---

### ⚙️ Global Features

- **Navbar:** dynamic based on user role (guest, student, instructor, admin)
- **Sidebar:** collapsible for dashboards
- **Footer:** includes contact info, site map, accessibility, and social links
- **Toast/Alert System:** show success/error/status messages
- **Global Loader/Skeletons:** for async content
- **Theme & Language persistence:** stored in Zustand
- **Custom 404 & 500 Pages**
- **Legal Pages:** Terms, Privacy, Accessibility Statement
- **Accessibility shortcuts:** skip to content, focus states, screen reader labels

---

### 🗂️ Project Architecture

```
src/
├── components/
│   ├── ui/
│   ├── layout/
│   ├── course/
│   ├── lesson/
│   ├── dashboard/
│   ├── auth/
│   ├── forms/
│   └── common/
├── pages/
│   ├── index.tsx
│   ├── explore/
│   ├── course/[id]/
│   ├── lesson/[id]/
│   ├── dashboard/
│   ├── account/
│   ├── auth/
│   ├── student-application/
│   ├── teacher-application/
│   ├── forum/
│   ├── certificates/
│   ├── terms/
│   ├── privacy/
│   ├── accessibility/
│   └── 404.tsx
├── store/
├── hooks/
├── i18n/
├── utils/
├── assets/
├── types/
├── styles/
└── main.tsx
```

---

### 🧩 Zustand Stores

- `useAuthStore`: handles login state, roles, tokens
- `useCourseStore`: course list, filtering, sorting, pagination
- `useProgressStore`: user progress tracking per course/lesson
- `useThemeStore`: theme and language preferences
- `useNotificationStore`: toasts and user messages

---

### 🎨 UI/UX Design Guidelines

- Clean, modern, minimal design (like Coursera/edX)
- Consistent use of HeroUI design tokens and Tailwind utilities
- Animated transitions with Framer Motion for page changes
- Skeleton loaders for all async data
- Focus on **professional, educational aesthetic** (white/blue palette)
- Visual consistency across all components (buttons, inputs, forms)

---

### 🌐 Localization Setup

- Implement `react-i18next` with a `locales/` folder (e.g., `en`, `es`)
- Each page and UI string should use translation keys
- Include a language switcher in the navbar

---

### ✅ Deliverables

- Fully functional UI with dummy data connected to placeholder APIs
- Responsive across all devices
- Accessible, SEO-optimized, and secure
- Production-ready folder structure
- Example `.env.example` for API endpoints
- Clear README with setup instructions

---

### 🧠 Notes

- Backend already handles logic (auth, DB, processing), so focus purely on frontend UI + data consumption.
- Use mock data or Axios calls for integration.
- Prioritize accessibility, modern design, and internationalization.

**Goal:** A complete, polished, modern, and responsive LMS frontend experience with accessibility, internationalization, and modular scalability for future features.
