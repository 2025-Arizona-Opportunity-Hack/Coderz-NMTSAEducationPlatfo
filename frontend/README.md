# NMTSA Learn - Frontend

A modern, accessible Learning Management System (LMS) for Neurologic Music Therapy Services of Arizona (NMTSA).

## 🚀 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 6
- **UI Library**: HeroUI v2
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Internationalization**: react-i18next (en, es)
- **Animations**: Framer Motion
- **Icons**: Lucide React

## ✨ Features

- 🔐 **Authentication**: JWT-based auth with role-based access control (Student, Instructor, Admin)
- 🌐 **Internationalization**: Multi-language support (English, Spanish)
- ♿ **Accessibility**: WCAG 2.2 AA compliant with keyboard navigation and screen reader support
- 📱 **Responsive**: Mobile-first design, works on all devices
- 🎨 **Theme**: Dark/Light mode support
- 🔒 **Security**: XSS protection, input sanitization, secure token storage

## 📋 Prerequisites

- Node.js 18+ (LTS recommended)
- pnpm 8+ (or npm/yarn)
- Backend API running (see backend repository)

## 🛠️ Installation

1. **Clone the repository**

```bash
cd frontend
```

2. **Install dependencies**

```bash
pnpm install
```

3. **Configure environment variables**

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:3000/api
VITE_API_VERSION=v1
VITE_DEBUG=false
```

4. **Run the development server**

```bash
pnpm dev
```

The application will be available at `http://localhost:5173`

## 📦 Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build
- `pnpm lint` - Run ESLint and fix issues
- `pnpm lint:check` - Check for linting issues without fixing

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── layout/         # Layout components (Navbar, Footer)
│   └── icons.tsx       # Icon components
├── config/             # Configuration files
│   ├── api.ts          # Axios instance and interceptors
│   └── site.ts         # Site configuration
├── hooks/              # Custom React hooks
│   └── useAuth.ts      # Authentication hook
├── i18n/               # Internationalization
│   ├── config.ts       # i18n configuration
│   └── locales/        # Translation files
├── pages/              # Page components
│   ├── Home.tsx
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   └── ...
├── services/           # API services
│   └── auth.service.ts # Authentication API calls
├── store/              # Zustand stores
│   └── useAuthStore.ts # Auth state management
├── styles/             # Global styles
│   └── globals.css
├── types/              # TypeScript types
│   ├── api.ts          # API response types
│   └── index.ts        # General types
├── App.tsx             # Main app component with routing
├── main.tsx            # App entry point
└── provider.tsx        # HeroUI provider wrapper
```

## 🔌 Backend Integration

This frontend is designed to work with a REST API backend. Update the `VITE_API_BASE_URL` in your `.env` file to point to your backend server.

### Expected API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/update-password` - Update password
- `GET /api/auth/me` - Get current user
- `GET /api/users/:id` - Get user profile

See `src/services/auth.service.ts` for the complete API integration.

## 🌍 Internationalization

The app supports multiple languages. To add a new language:

1. Create a new JSON file in `src/i18n/locales/` (e.g., `fr.json`)
2. Add translations following the same structure as `en.json`
3. Update `src/i18n/config.ts` to include the new language

## 🚢 Deployment

### Build for Production

```bash
pnpm build
```

The build output will be in the `dist/` directory.

### Deploy to Vercel

This project includes a `vercel.json` configuration file. Simply connect your repository to Vercel for automatic deployments.

### Deploy to Netlify

```bash
pnpm build
# Upload the dist/ folder to Netlify
```

## 🧪 Current Status

✅ **Completed:**
- Step 1: Project scaffold with Vite, TypeScript, Tailwind, Zustand, i18n
- Step 2: Authentication pages and token-based auth flow
- Global layout with Navbar, Footer, Skip-to-content

⏳ **Next Steps:**
- Step 3: Explore page with course listing and filters
- Step 4: Course detail page
- Step 5: Lesson page with markdown support
- Step 6: Student dashboard with progress tracking
- Step 7: Application forms (Teacher/Student)
- Step 8: Discussion forum
- Step 9: Final polish, SEO, and accessibility audit

## 📝 Notes

- This frontend uses token-based authentication (JWT)
- Tokens are stored in `localStorage` with the key `auth-token`
- The auth state is persisted using Zustand's persist middleware
- All API calls include automatic token injection via Axios interceptors
- 401 responses automatically clear auth state and redirect to login

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run `pnpm lint` to ensure code quality
4. Submit a pull request

## 📄 License

Licensed under the MIT license.
